import redis
import numpy as np
from typing import List, Dict, Any
from app.core.config import settings
from app.core.embedding_client import get_embed_model

_redis = None

def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.REDIS_URL)
    return _redis

def search_similar_context(query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
    if not query_text:
        return []

    r = get_redis()
    model = get_embed_model()
    vec = model.encode(query_text, normalize_embeddings=True).astype(np.float32).tobytes()

    base = f"*=>[KNN {top_k} @embedding $vec AS score]"
    res = r.execute_command(
        "FT.SEARCH", settings.INDEX_NAME, base,
        "PARAMS", "2", "vec", vec,
        "RETURN", "4", "name", "subject", "user_stories", "score",
        "SORTBY", "score",
        "DIALECT", "2"
    )

    out = []
    if isinstance(res, list) and len(res) >= 3:
        for i in range(1, len(res), 2):
            fields = res[i+1]
            def _get(k):
                v = fields.get(k.encode()) if isinstance(fields, dict) else None
                return v.decode("utf-8", "ignore") if isinstance(v, bytes) else (v or "")
            out.append({
                "name": _get("name"),
                "subject": _get("subject"),
                "user_stories": _get("user_stories"),
                "score": float(_get("score") or 0.0),
            })
    return out
