from typing import Optional, List, Dict, Any
import time
import redis
from redis.commands.search.field import TextField, TagField, VectorField
from redis.commands.search.query import Query

from app.core.config import settings
from app.core.embedding_client import EMBED_DIM, embed_texts, f32

r = redis.from_url(settings.REDIS_URL, decode_responses=False)

def _set_dialect2():
    try:
        r.execute_command("FT.CONFIG", "SET", "DEFAULT_DIALECT", "2")
    except Exception:
        pass

def ensure_index(force: bool = False) -> bool:
    created = False
    try:
        if not force:
            r.ft(settings.INDEX_NAME).info()
            _set_dialect2()
            return False
    except Exception:
        pass

    if force:
        try:
            r.ft(settings.INDEX_NAME).dropindex(delete_documents=False)
        except Exception:
            pass

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
    r.ft(settings.INDEX_NAME).create_index(schema)
    _set_dialect2()
    created = True
    return created

try:
    ensure_index()
except Exception:
    pass

def knn_search(query: str, k: int = 3, types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    try:
        r.ft(settings.INDEX_NAME).info()
    except Exception:
        ensure_index()

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

    for attempt in range(2):
        try:
            res = r.ft(settings.INDEX_NAME).search(q, query_params={"vec": f32(qvec)})
            return [
                {"title": d.title, "text": d.text, "doc_type": d.doc_type, "score": float(d.score)}
                for d in res.docs
            ]
        except redis.ResponseError as e:
            if "No such index" in str(e) and attempt == 0:
                ensure_index(force=False)
                time.sleep(0.2)
                continue
            raise
