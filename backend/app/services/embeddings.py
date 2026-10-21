"""Cost-optimized embeddings via any OpenAI-compatible endpoint.

Defaults to OpenAI text-embedding-3-small ($0.02 / M tokens). Point embedding_base_url
at Gemini's OpenAI-compatible endpoint for a free-tier alternative. Returns None when
no key is set so seeding still works without embeddings.
"""

import logging

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_TIMEOUT_SECONDS = 30


def _has_key() -> bool:
    return bool(settings.embedding_api_key)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=1, max=15),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def embed_texts(texts: list[str]) -> list[list[float]] | None:
    if not _has_key() or not texts:
        return None
    from openai import OpenAI

    client = OpenAI(
        api_key=settings.embedding_api_key,
        base_url=settings.embedding_base_url,
        timeout=_TIMEOUT_SECONDS,
    )
    resp = client.embeddings.create(model=settings.embedding_model, input=texts)
    return [d.embedding for d in resp.data]


def embed_text(text: str) -> list[float] | None:
    result = embed_texts([text[:8000]])
    return result[0] if result else None
