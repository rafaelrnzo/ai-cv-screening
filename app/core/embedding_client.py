import array
from typing import List
from sentence_transformers import SentenceTransformer
from app.core.config import settings

embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
EMBED_DIM: int = embedder.get_sentence_embedding_dimension()

def embed_texts(texts: List[str]) -> List[List[float]]:
    emb = embedder.encode(texts, normalize_embeddings=True)
    return emb.tolist()

def f32(v: List[float]) -> bytes:
    arr = array.array("f", v)
    return arr.tobytes()
