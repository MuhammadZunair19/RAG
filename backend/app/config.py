"""Application configuration from environment variables."""

from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache

# Project root: RAG/ (parent of backend/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"


class Settings(BaseSettings):
    """App settings loaded from env."""

    app_name: str = "rag-chatbot"
    debug: bool = False
    api_prefix: str = "/api/v1"

    database_url: str = ""

    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Local LLM (Ollama)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    vector_store_path: str = ""
    sentence_transformer_model: str = "all-MiniLM-L6-v2"

    class Config:
        # Load .env from project root (RAG/) so it works when running from backend/
        env_file = str(PROJECT_ROOT / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

    @field_validator("database_url", mode="before")
    @classmethod
    def resolve_database_url(cls, v: str) -> str:
        raw = (v or "").strip()
        # Resolve relative paths to project root so rag.db is always in RAG/data/
        if not raw or "./data/rag.db" in raw or raw == "sqlite+aiosqlite:///./data/rag.db":
            path = DATA_DIR / "rag.db"
            return f"sqlite+aiosqlite:///{path.as_posix()}"
        return raw

    @field_validator("vector_store_path", mode="before")
    @classmethod
    def resolve_vector_store_path(cls, v: str) -> str:
        raw = (v or "").strip()
        if not raw or raw.startswith("./data"):
            return str(DATA_DIR / "chroma")
        return raw


@lru_cache
def get_settings() -> Settings:
    return Settings()
