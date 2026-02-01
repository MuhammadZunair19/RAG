"""RAG: embed query -> retrieve chunks -> local LLM (Ollama) with context -> response + sources."""

from __future__ import annotations

import httpx

from app.config import get_settings
from app.services.embeddings import get_embedding_function
from app.services.vector_store import similarity_search, get_collection_count

RAG_PROMPT = """You are an AI assistant.
Answer ONLY using the provided context.
If the answer is not found in the context, respond with: "I don't know based on the provided documents."

Context:
{context}

Question:
{question}
"""

OLLAMA_NOT_RUNNING_MSG = (
    "Local LLM (Ollama) is not running or the model is not pulled. "
    "Install Ollama from https://ollama.com, then run: ollama run llama3.2 "
    "(or set OLLAMA_MODEL in .env to a model you have)."
)


def get_llm_response(question: str, context: str) -> str:
    """Call local Ollama to generate answer from context and question."""
    settings = get_settings()
    prompt = RAG_PROMPT.format(context=context, question=question)
    url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
    }
    try:
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
        return (data.get("response") or "").strip()
    except httpx.ConnectError:
        return OLLAMA_NOT_RUNNING_MSG
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return (
                f"Ollama model '{settings.ollama_model}' not found. "
                f"Run: ollama run {settings.ollama_model}"
            )
        return f"Ollama error: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Local LLM error: {e}"


def rag_query(question: str, top_k: int = 5) -> tuple[str, list[dict]]:
    """
    Run RAG: embed question, retrieve top_k chunks, build context, call local LLM.
    Returns (response_text, sources) where sources are list of {document, metadata}.
    """
    try:
        embed_fn = get_embedding_function()
        query_embedding = embed_fn([question])[0]
    except Exception as e:
        return (f"Embedding error: {e}", [])

    chunks = similarity_search(query_embedding, top_k=top_k)
    if not chunks:
        total_chunks = get_collection_count()
        if total_chunks == 0:
            return (
                "No documents have been uploaded yet. "
                "Upload PDFs in the Documents page (admin) to get started, then ask questions about their content.",
                [],
            )
        return (
            "No relevant passages found for your question. "
            "Try asking something that relates to your uploaded documents, or rephrase your question.",
            [],
        )

    context = "\n\n---\n\n".join(c.get("document", "") or "" for c in chunks)
    sources = []
    for c in chunks:
        doc = c.get("document") or ""
        text = (doc[:200] + "...") if len(doc) > 200 else doc
        sources.append({"text": text, "metadata": c.get("metadata") or {}})
    response = get_llm_response(question, context)
    return response, sources
