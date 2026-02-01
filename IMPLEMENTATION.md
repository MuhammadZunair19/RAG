# Implementation Progress

Implementation follows the README spec module by module.

## Quick start

1. **Backend** (from project root):
   - Copy `.env.example` to `.env` and set `SECRET_KEY`, `OPENAI_API_KEY` (optional for local embeddings).
   - `cd backend && pip install -r requirements.txt`
   - Ensure `data/` exists (e.g. `mkdir data`).
   - `alembic upgrade head` (from `backend/`).
   - `python run.py` (or `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`).

2. **Frontend**:
   - `cd frontend && npm install && npm run dev` (runs on port 3000, proxies `/api` to backend).

3. **Use**: Register (choose admin for upload), upload PDFs at `/admin/documents`, then ask questions at `/chat`.

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

## Module 4: Document Ingestion ✅

- **PDF**: `app/services/pdf_extractor.py` (PyPDF2, text per page)
- **Chunking**: `app/services/chunker.py` (LangChain RecursiveCharacterTextSplitter, ~1000 chars)
- **Embeddings**: `app/services/embeddings.py` (OpenAI if key set, else sentence-transformers)
- **Vector store**: `app/services/vector_store.py` (ChromaDB persistent at `data/chroma`)
- **Ingestion**: `app/services/ingestion.py` (orchestrate extract → chunk → embed → Chroma + DB metadata)
- **API**: `POST /api/v1/documents/upload` (admin, PDF), `GET /api/v1/documents/` (admin)
- **Schemas**: `app/schemas/document.py`. Ensure `data/` exists for Chroma path.

## Module 5: RAG & Chat API ✅

- **RAG**: `app/services/rag.py` (embed query → similarity_search → prompt → OpenAI gpt-4o-mini)
- **Prompt**: Answer only from context; "I don't know based on the provided documents." if not found
- **API**: `POST /api/v1/chat/` (body: `{ "question" }`, auth required) → `{ "response", "sources" }`
- **History**: `GET /api/v1/chat/history?limit=50` (auth required)
- **Schemas**: `app/schemas/chat.py`. Requires `OPENAI_API_KEY` for LLM.

## Module 6: Frontend ✅

- **Stack**: Vite + React 18 + Tailwind CSS + React Router + Axios + react-markdown
- **Auth**: Login, Register (role: user/admin); token in localStorage; axios interceptor; AuthContext
- **Chat**: `/chat` – question input, RAG response with markdown, source attribution
- **Admin**: `/admin/documents` – upload PDF, list documents (admin only)
- **Layout**: Header with Chat / Documents (admin) / Logout
- **Run**: `cd frontend && npm install && npm run dev` (port 3000; proxy `/api` → backend 8000)
