"""Abstract base protocols and typed exceptions for LLM providers (S04)."""

from collections.abc import AsyncGenerator
from typing import Any, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProviderError(Exception):
    """Base exception for all LLM provider errors."""

    def __init__(self, message: str, details: Any | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class LLMTimeoutError(LLMProviderError):
    """Raised when an LLM provider request exceeds the configured timeout."""


class StructuredOutputError(LLMProviderError):
    """Raised when the LLM output fails schema validation after retries."""


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol defining the stable contract for LLM providers in ATLAS."""

    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate a complete text response for a given prompt."""
        ...

    async def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        system: str | None = None,
        **kwargs: Any,
    ) -> T:
        """Generate and validate a structured response against a Pydantic schema."""
        ...

    def stream_generate(
        self,
        prompt: str,
        system: str | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Stream generated response tokens asynchronously."""
        ...
