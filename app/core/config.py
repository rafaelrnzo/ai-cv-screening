from typing import List, Union, ClassVar
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AI Microservice"
    API_V1_STR: str = "/api/v1"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8004

    MODEL_CTX_WINDOW: int = 8192
    SAFETY_BUFFER: int = 512
    HARD_CAP_MAX_NEW: int = 1024

    MAX_CHARS_TEMPLATE: ClassVar[int] = 6000
    MAX_CHARS_CONTEXT: ClassVar[int] = 12000

    INDEX_NAME: str = "ac_index"
    REDIS_URL: str = "redis://192.168.100.136:6379"

    VLLM_URL: str = "http://192.168.100.136:8006/v1"
    VLLM_MODEL: str = "gemma4b-4bit"
    VLLM_EMBEDDING: str = "gemma4b-4bit"
    SAFETENSOR_EMBEDDING: str = "BAAI/bge-m3"

    BACKEND_CORS_ORIGINS: List[str] = []
    VLLM_MAX_CONCURRENT_REQUESTS: int = 10

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")] if v else []
        return v


settings = Settings()
