"""Embedding generation: OpenAI or local HuggingFace."""

from typing import Callable

from app.config import get_settings

settings = get_settings()


def get_embedding_function() -> Callable[[list[str]], list[list[float]]]:
    """Return a function that embeds a list of texts. Prefer OpenAI if key set."""
    if settings.openai_api_key:
        return _openai_embed
    return _local_embed


def _openai_embed(texts: list[str]) -> list[list[float]]:
    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key)
    batch_size = 100
    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.embeddings.create(
            model="text-embedding-3-small",
            input=batch,
        )
        ordered = [item.embedding for item in sorted(resp.data, key=lambda x: x.index)]
        all_embeddings.extend(ordered)
    return all_embeddings


def _local_embed(texts: list[str]) -> list[list[float]]:
    """Use sentence-transformers (no API key required)."""
    from sentence_transformers import SentenceTransformer  # type: ignore
    model = SentenceTransformer(settings.sentence_transformer_model)
    embeddings = model.encode(texts, convert_to_numpy=True)
    return [e.tolist() for e in embeddings]
