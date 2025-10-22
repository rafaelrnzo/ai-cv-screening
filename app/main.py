from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import api_router
from app.core.config import settings
from app.db.models import Base
from app.db.session import engine


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)

    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.get("/", tags=["Health"])
    def root():
        return {
            "ok": True,
            "app_name": settings.APP_NAME,
            "api_base": settings.API_V1_STR,
            "gemini_model": settings.GEMINI_MODEL,
            "embedding_model": settings.EMBEDDING_MODEL,
            "upload_dir": settings.UPLOAD_DIR,
            "redis_index": settings.INDEX_NAME,
        }

    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.on_event("startup")
    async def on_startup():
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized")
        print(f"🚀 {settings.APP_NAME} running at {settings.SERVER_HOST}:{settings.SERVER_PORT}")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
    )
