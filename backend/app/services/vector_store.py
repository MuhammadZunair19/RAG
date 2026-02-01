"""ChromaDB vector store: add chunks and similarity search."""

from __future__ import annotations

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
    # Chroma 0.4.x: we pass embeddings when adding; no embedding_function needed for add
    # For query we need to compute embeddings ourselves and use query(embedding=...)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "RAG document chunks"},
    )


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
    results = coll.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where,
        include=["metadatas", "documents"],
    )
    if not results or not results["ids"] or not results["ids"][0]:
        return []
    out: list[dict] = []
    for i, chunk_id in enumerate(results["ids"][0]):
        meta = (results["metadatas"][0] or [])[i] if results.get("metadatas") else {}
        doc = (results["documents"][0] or [])[i] if results.get("documents") else ""
        out.append({"id": chunk_id, "metadata": meta, "document": doc})
    return out
