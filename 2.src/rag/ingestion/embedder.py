"""Local embedding generation adapter using Ollama (S06)."""

import asyncio
import logging
from typing import Any, Protocol

import httpx

from providers.config import OllamaSettings

logger = logging.getLogger(__name__)

DEFAULT_EMBEDDING_MODEL = "nomic-embed-text:latest"


class Embedder(Protocol):
    """Protocol defining the embedding provider interface."""

    async def embed_query(self, text: str) -> list[float]:
        """Generate embedding vector for a single search query."""
        ...

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for a list of document chunks."""
        ...


class OllamaEmbedder:
    """Local embedding generator using Ollama nomic-embed-text."""

    def __init__(
        self,
        settings: OllamaSettings | None = None,
        model: str = DEFAULT_EMBEDDING_MODEL,
        batch_size: int = 16,
        timeout_seconds: float = 60.0,
    ) -> None:
        """Initialize the Ollama embedder.

        Args:
            settings: Ollama configuration settings (host, timeout, retries).
            model: Embedding model name in Ollama (default: nomic-embed-text:latest).
            batch_size: Number of texts to embed in a single batch request.
            timeout_seconds: Per-request HTTP timeout in seconds.
        """
        self.settings = settings or OllamaSettings(timeout_seconds=timeout_seconds)
        self.model = model
        self.batch_size = batch_size
        self.timeout_seconds = timeout_seconds

    async def _post(self, endpoint: str, payload: dict[str, Any]) -> httpx.Response:
        """Execute HTTP POST with retries."""
        url = f"{self.settings.host.rstrip('/')}/{endpoint.lstrip('/')}"
        max_retries = self.settings.max_retries

        async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout_seconds)) as client:
            for attempt in range(max_retries + 1):
                try:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    return response
                except (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError) as exc:
                    if attempt == max_retries:
                        logger.error(
                            "Failed to generate embeddings from Ollama after %d retries: %s",
                            max_retries + 1,
                            exc,
                        )
                        raise
                    delay = 0.5 * (2**attempt)
                    await asyncio.sleep(delay)

        raise RuntimeError("Unreachable retry loop exit in OllamaEmbedder")

    async def embed_query(self, text: str) -> list[float]:
        """Embed a single query string."""
        payload = {
            "model": self.model,
            "prompt": text,
        }
        response = await self._post("/api/embeddings", payload)
        data = response.json()
        embedding: list[float] = data.get("embedding", [])
        return embedding

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple document passages in batches using /api/embed or /api/embeddings."""
        if not texts:
            return []

        all_embeddings: list[list[float]] = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            try:
                # Try batch /api/embed endpoint first
                payload = {
                    "model": self.model,
                    "input": batch,
                }
                response = await self._post("/api/embed", payload)
                data = response.json()
                embeddings: list[list[float]] = data.get("embeddings", [])
                if embeddings:
                    all_embeddings.extend(embeddings)
                    continue
            except Exception as exc:
                logger.debug(
                    "Batch /api/embed failed, falling back to sequential /api/embeddings: %s",
                    exc,
                )

            # Fallback to per-item /api/embeddings if batch endpoint is not supported
            for item in batch:
                single_emb = await self.embed_query(item)
                all_embeddings.append(single_emb)

        return all_embeddings
