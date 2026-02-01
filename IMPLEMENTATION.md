# Implementation Progress

Implementation follows the README spec module by module.

## Module 1: Project Setup & Backend Foundation ✅

- **Backend**: FastAPI app under `backend/`
- **Config**: `app/config.py` (pydantic-settings from `.env`)
- **API structure**: `/api/v1/auth`, `/api/v1/users`, `/api/v1/documents`, `/api/v1/chat`
- **CORS**: Allowed for `localhost:3000` (frontend)
- **Run**: From project root, `cd backend && pip install -r requirements.txt && python run.py` (or `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`)

## Module 2: Database Models ✅

- **Models**: `app/models/user.py`, `document.py`, `chat.py` (User, Document, EmbeddingMeta, Chat)
- **DB**: Async SQLAlchemy in `app/db/session.py`, `get_db()` dependency
- **Migrations**: Alembic under `backend/alembic/`, initial migration `001_initial_schema.py`
- **Run migrations**: From project root, `cd backend && alembic upgrade head` (ensure `data/` exists)

## Module 3: User Authentication ✅

- **JWT**: `app/core/security.py` (create_access_token, decode_token, bcrypt hash)
- **Dependencies**: `app/core/dependencies.py` (get_current_user, require_role)
- **Auth API**: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`
- **Users API**: `GET /api/v1/users/` (admin only)
- **Schemas**: `app/schemas/auth.py`, `app/schemas/user.py`

## Module 4: Document Ingestion

- PDF upload, text extraction, chunking, embeddings, ChromaDB/FAISS

## Module 5: RAG & Chat API

- Query embedding, retrieval, LLM prompt, source attribution

## Module 6: Frontend

- React, Tailwind, auth UI, chat UI, admin document upload
