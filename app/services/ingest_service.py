import uuid
from app.core.redis_client import ensure_index, hset_doc
from app.core.embedding_client import embed_texts

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

def ingest_seed() -> None:
    ensure_index()
    for d in SEED_DOCS:
        emb = embed_texts([d["text"]])[0]
        hset_doc({"id": str(uuid.uuid4()), "title": d["title"], "text": d["text"], "doc_type": d["doc_type"], "embedding": emb})
