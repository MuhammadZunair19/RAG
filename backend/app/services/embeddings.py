"""Embedding generation: local sentence-transformers only."""

from typing import Callable

from app.config import get_settings

settings = get_settings()


def get_embedding_function() -> Callable[[list[str]], list[list[float]]]:
    """Return a function that embeds a list of texts using local sentence-transformers."""
    return _local_embed


def _local_embed(texts: list[str]) -> list[list[float]]:
    """Use sentence-transformers (no API key required)."""
    from sentence_transformers import SentenceTransformer  # type: ignore
    model = SentenceTransformer(settings.sentence_transformer_model)
    embeddings = model.encode(texts, convert_to_numpy=True)
    return [e.tolist() for e in embeddings]
