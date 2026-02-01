"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings, DATA_DIR
from app.api import router as api_router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create data dir and DB tables on startup."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    await init_db()
    yield
    # shutdown if needed


settings = get_settings()

app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
    description="AI-Powered Knowledge Chatbot using RAG",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}
