"""Application configuration from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """App settings loaded from env."""

    app_name: str = "rag-chatbot"
    debug: bool = False
    api_prefix: str = "/api/v1"

    database_url: str = "sqlite+aiosqlite:///./data/rag.db"

    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    openai_api_key: str = ""

    vector_store_path: str = "./data/chroma"
    sentence_transformer_model: str = "all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
