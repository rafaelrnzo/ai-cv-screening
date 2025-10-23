from typing import List, Union, Optional
import os
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

    REDIS_URL: str = "redis://localhost:6379/0"
    INDEX_NAME: str = "gt_idx"
    DOC_PREFIX: str = "gt:"

    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "admin.admin"
    POSTGRES_DB: str = "ai_screening"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    DATABASE_URL: Optional[str] = None

    UPLOAD_DIR: str = "./data/uploads"
    GROUND_DIR: str = "./data/ground_truth"

    BACKEND_CORS_ORIGINS: List[str] = []

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, list):
            return v
        if not v:
            return []
        v = v.strip()
        if v.startswith("["):
            import json
            try:
                parsed = json.loads(v)
                return [s.strip() for s in parsed]
            except Exception:
                pass
        return [s.strip() for s in v.split(",") if s.strip()]

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        user = os.getenv("POSTGRES_USER", self.POSTGRES_USER)
        pwd = os.getenv("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        db = os.getenv("POSTGRES_DB", self.POSTGRES_DB)
        host = os.getenv("POSTGRES_HOST", self.POSTGRES_HOST)
        port = os.getenv("POSTGRES_PORT", str(self.POSTGRES_PORT))
        return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"


settings = Settings()
