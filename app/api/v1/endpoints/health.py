from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health")
def health():
    return {
        "ok": True,
        "app": settings.APP_NAME,
        "llm_model": settings.GEMINI_MODEL,
        "embed_model": settings.EMBEDDING_MODEL,
        "index": settings.INDEX_NAME,
    }
