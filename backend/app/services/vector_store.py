"""ChromaDB vector store: add chunks and similarity search."""

from __future__ import annotations

import os
# Disable Chroma telemetry before import (avoids capture() argument errors)
os.environ.setdefault("ANONYMIZED_TELEMETRY", "FALSE")

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings
from app.services.embeddings import get_embedding_function

COLLECTION_NAME = "rag_chunks"


def _get_client():
    settings = get_settings()
    return chromadb.PersistentClient(
        path=settings.vector_store_path,
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def get_collection():
    """Get or create the RAG collection with our embedding function."""
    client = _get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "RAG document chunks"},
    )


def get_collection_count() -> int:
    """Return number of chunks in the RAG collection (0 if empty or error)."""
    try:
        coll = get_collection()
        return coll.count()
    except Exception:
        return 0


def add_chunks(
    ids: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict],
    documents: list[str],
) -> None:
    """Add chunk embeddings and text to Chroma. ids unique (e.g. doc_id_chunk_idx)."""
    coll = get_collection()
    coll.add(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)


def similarity_search(
    query_embedding: list[float],
    top_k: int = 5,
    document_id: int | None = None,
) -> list[dict]:
    """
    Return top_k most similar chunks. Each dict has id, metadata, document (chunk text).
    If document_id is set, filter to that document only.
    """
    coll = get_collection()
    where = {"document_id": document_id} if document_id is not None else None
    # Chroma returns lists of lists: one list per query; we pass a single query
    results = coll.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, max(1, coll.count())),  # avoid asking for more than exist
        where=where,
        include=["metadatas", "documents"],
    )
    ids_list = results.get("ids") or []
    if not ids_list or not ids_list[0]:
        return []
    first_ids = ids_list[0]
    metadatas_list = results.get("metadatas") or [[]]
    documents_list = results.get("documents") or [[]]
    first_metas = metadatas_list[0] if metadatas_list else []
    first_docs = documents_list[0] if documents_list else []
    out: list[dict] = []
    for i, chunk_id in enumerate(first_ids):
        meta = first_metas[i] if i < len(first_metas) else {}
        doc = first_docs[i] if i < len(first_docs) else ""
        if not isinstance(doc, str):
            doc = str(doc) if doc is not None else ""
        out.append({"id": chunk_id, "metadata": meta, "document": doc})
    return out
