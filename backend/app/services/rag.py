"""RAG: embed query -> retrieve chunks -> LLM with context -> response + sources."""

from __future__ import annotations

from app.config import get_settings
from app.services.embeddings import get_embedding_function
from app.services.vector_store import similarity_search

RAG_PROMPT = """You are an AI assistant.
Answer ONLY using the provided context.
If the answer is not found in the context, respond with: "I don't know based on the provided documents."

Context:
{context}

Question:
{question}
"""


def get_llm_response(question: str, context: str) -> str:
    """Call OpenAI to generate answer from context and question."""
    settings = get_settings()
    if not settings.openai_api_key:
        return "OpenAI API key is not configured. Set OPENAI_API_KEY to enable RAG responses."
    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key)
    prompt = RAG_PROMPT.format(context=context, question=question)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )
    return (resp.choices[0].message.content or "").strip()


def rag_query(question: str, top_k: int = 5) -> tuple[str, list[dict]]:
    """
    Run RAG: embed question, retrieve top_k chunks, build context, call LLM.
    Returns (response_text, sources) where sources are list of {document, metadata}.
    """
    embed_fn = get_embedding_function()
    query_embedding = embed_fn([question])[0]
    chunks = similarity_search(query_embedding, top_k=top_k)
    if not chunks:
        context = "(No relevant documents found.)"
        sources = []
    else:
        context = "\n\n---\n\n".join(c.get("document", "") for c in chunks)
        sources = []
        for c in chunks:
            doc = c.get("document", "")
            text = (doc[:200] + "...") if len(doc) > 200 else doc
            sources.append({"text": text, "metadata": c.get("metadata", {})})
    response = get_llm_response(question, context)
    return response, sources
