from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    APP_NAME: str = "AI Screening Service"
    API_V1_STR: str = "/api/v1"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8004

    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "BAAI/bge-m3"

    REDIS_URL: str = "redis://redis-stack:6379/0"
    INDEX_NAME: str = "gt_idx"
    DOC_PREFIX: str = "gt:"

    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "admin.admin"
    POSTGRES_DB: str = "ai_screening"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = (
        "postgresql+psycopg2://admin:admin.admin@postgres:5432/ai_screening"
    )

    UPLOAD_DIR: str = "./data/uploads"
    GROUND_DIR: str = "./data/ground_truth"

    BACKEND_CORS_ORIGINS: List[str] = []

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")] if v else []
        return v


settings = Settings()
