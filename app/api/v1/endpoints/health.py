from fastapi import APIRouter, HTTPException, status 
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
def health_check():
    return {
        "app": settings.APP_NAME,
        "api_version": settings.API_V1_STR,
        "status": "ok",
        "version": "1.0.0",
        "redis": "connected",
        "model": "loaded"
    }