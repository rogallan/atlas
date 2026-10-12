"""Contract tests for LLM provider abstraction (S04)."""

import inspect

from providers.base import LLMProvider
from providers.ollama import OllamaProvider


def test_ollama_provider_implements_protocol() -> None:
    """Verify that OllamaProvider fulfills the LLMProvider protocol specification."""
    provider = OllamaProvider()

    assert isinstance(provider, LLMProvider)
    assert hasattr(provider, "generate")
    assert hasattr(provider, "generate_structured")
    assert hasattr(provider, "stream_generate")

    assert inspect.iscoroutinefunction(provider.generate)
    assert inspect.iscoroutinefunction(provider.generate_structured)
    assert inspect.isasyncgenfunction(provider.stream_generate)
