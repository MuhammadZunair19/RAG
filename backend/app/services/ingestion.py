"""Orchestrate document ingestion: PDF -> extract -> chunk -> embed -> store."""

from __future__ import annotations

from app.services.pdf_extractor import extract_text_from_pdf
from app.services.chunker import chunk_pages
from app.services.embeddings import get_embedding_function
from app.services.vector_store import add_chunks


def ingest_pdf(
    file_content: bytes,
    document_id: int,
    filename: str,
) -> list[tuple[str, int | None, int]]:
    """
    Process PDF: extract text, chunk, embed, store in Chroma.
    Returns list of (chunk_text, page_number, chunk_index) for caller to insert EmbeddingMeta.
    """
    pages = extract_text_from_pdf(file_content)
    chunks_with_pages = chunk_pages(pages)
    if not chunks_with_pages:
        return []

    chunk_texts = [c[0] for c in chunks_with_pages]
    page_numbers = [c[1] for c in chunks_with_pages]

    embed_fn = get_embedding_function()
    embeddings = embed_fn(chunk_texts)

    ids = [f"{document_id}_{i}" for i in range(len(chunk_texts))]
    metadatas = [
        {
            "document_id": document_id,
            "chunk_index": i,
            "page_number": page_numbers[i] if page_numbers[i] is not None else 0,
            "filename": filename,
        }
        for i in range(len(chunk_texts))
    ]
    add_chunks(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=chunk_texts,
    )
    return [(chunk_texts[i], page_numbers[i] or 0, i) for i in range(len(chunk_texts))]
