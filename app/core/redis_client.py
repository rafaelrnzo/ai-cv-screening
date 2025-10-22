import time
import uuid
import array
from typing import List, Dict, Any, Optional

import redis
from urllib.parse import urlparse, urlunparse
from sentence_transformers import SentenceTransformer
from redis.commands.search.field import TextField, TagField, VectorField
from redis.commands.search.query import Query

from app.core.config import settings


# ---------- connection helper (fallback redis-stack -> localhost) ----------
def _with_host(url: str, new_host: str) -> str:
    p = urlparse(url)
    return urlunparse(p._replace(netloc=p.netloc.replace(p.hostname or "", new_host, 1)))

def _connect(url: str, retries: int = 3, delay: float = 0.5):
    candidates = [url]
    try:
        host = urlparse(url).hostname or ""
        if host == "redis-stack":
            candidates.append(_with_host(url, "localhost"))
    except Exception:
        pass

    last_err = None
    for candidate in candidates:
        for _ in range(retries):
            try:
                r = redis.from_url(
                    candidate,
                    socket_timeout=2,
                    socket_connect_timeout=2,
                    decode_responses=False,
                )
                r.ping()
                return r
            except Exception as e:
                last_err = e
                time.sleep(delay)
    raise RuntimeError(f"Cannot connect to Redis. Tried {candidates}. Last error: {last_err}")


# ---------- globals ----------
r = _connect(settings.REDIS_URL)
embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
EMBED_DIM = embedder.get_sentence_embedding_dimension()
INDEX_NAME = settings.INDEX_NAME
DOC_PREFIX = settings.DOC_PREFIX


# ---------- utils ----------
def f32(v: List[float]) -> bytes:
    arr = array.array("f", v)
    return arr.tobytes()

def embed_texts(texts: List[str]) -> List[List[float]]:
    emb = embedder.encode(texts, normalize_embeddings=True)
    return emb.tolist()


# ---------- seed docs ----------
SEED_DOCS = [
    {
        "title": "Backend Job Description",
        "text": (
            "Product Engineer (Backend): build APIs, DB schemas, scalable services; "
            "integrate LLMs (prompting, chaining, RAG); handle async jobs & retries; "
            "testing & clean code; collaborate with FE & PM; cloud experience preferred."
        ),
        "doc_type": "job_description",
    },
    {
        "title": "Case Study Brief",
        "text": (
            "Build backend service to auto-screen candidates by comparing CV and Project Report "
            "to Job Description and Case Study guidelines. Use RAG over internal docs (job desc, brief, rubrics). "
            "Pipeline must be asynchronous and resilient; output cv_match_rate, project_score, feedbacks, and summary."
        ),
        "doc_type": "case_brief",
    },
    {
        "title": "CV Rubric",
        "text": (
            "CV evaluation: Technical skills match (40), Experience level (25), Achievements (20), Cultural fit (15). "
            "All scored 1-5; emphasize backend, databases, APIs, cloud, and AI/LLM exposure."
        ),
        "doc_type": "cv_rubric",
    },
    {
        "title": "Project Rubric",
        "text": (
            "Project evaluation: Correctness (prompting/chaining/RAG) 30, Code quality 25, "
            "Resilience & error handling 20, Documentation 15, Creativity 10. Score 1-5."
        ),
        "doc_type": "project_rubric",
    },
]


# ---------- index mgmt ----------
def ensure_index_and_seed() -> None:
    # create index if missing
    try:
        r.ft(INDEX_NAME).info()
    except Exception:
        schema = (
            TextField("title"),
            TextField("text"),
            TagField("doc_type"),
            VectorField(
                "embedding",
                "HNSW",
                {"TYPE": "FLOAT32", "DIM": EMBED_DIM, "DISTANCE_METRIC": "COSINE"},
            ),
        )
        r.ft(INDEX_NAME).create_index(schema)
        try:
            r.execute_command("FT.CONFIG", "SET", "DEFAULT_DIALECT", "2")
        except Exception:
            pass

    # seed minimal (idempotent)
    has_any = False
    for _ in r.scan_iter(f"{DOC_PREFIX}*"):
        has_any = True
        break
    if not has_any:
        for doc in SEED_DOCS:
            emb = embed_texts([doc["text"]])[0]
            r.hset(
                f"{DOC_PREFIX}{uuid.uuid4()}",
                mapping={
                    "title": doc["title"],
                    "text": doc["text"],
                    "doc_type": doc["doc_type"],
                    "embedding": f32(emb),
                },
            )


# ---------- public search api ----------
def knn_search(query: str, k: int = 3, types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Vector KNN search with optional @doc_type tag filter.
    Make sure ensure_index_and_seed() has been called at least once.
    """
    qvec = embed_texts([query])[0]
    if types:
        tags = "|".join(types)
        base = f"(@doc_type:{{{tags}}})=>[KNN {k} @embedding $vec AS score]"
    else:
        base = f"*=>[KNN {k} @embedding $vec AS score]"

    q = (
        Query(base)
        .return_fields("title", "text", "doc_type", "score")
        .sort_by("score")
        .dialect(2)
    )
    res = r.ft(INDEX_NAME).search(q, query_params={"vec": f32(qvec)})
    return [
        {"title": d.title, "text": d.text, "doc_type": d.doc_type, "score": float(d.score)}
        for d in res.docs
    ]
