"""Unit and resilience tests for the Ollama LLM provider (S04)."""

import json
from collections.abc import Callable

import httpx
import pytest
from pydantic import BaseModel

from providers.base import (
    LLMTimeoutError,
    StructuredOutputError,
)
from providers.config import OllamaSettings
from providers.ollama import OllamaProvider


class MockIntentSchema(BaseModel):
    intent: str
    confidence: float
    reasoning: str


def make_mock_client(
    handler: Callable[[httpx.Request], httpx.Response],
    base_url: str = "http://localhost:11434",
) -> httpx.AsyncClient:
    """Helper to create an AsyncClient with a mock transport and valid base URL."""
    return httpx.AsyncClient(
        base_url=base_url,
        transport=httpx.MockTransport(handler),
    )


@pytest.mark.asyncio
async def test_ollama_generate_success() -> None:
    """Test successful text generation call."""

    def handler(request: httpx.Request) -> httpx.Response:
        data = json.loads(request.content)
        assert data["model"] == "llama3.2:latest"
        assert "prompt" in data
        return httpx.Response(200, json={"response": "Simulação de taxa aprovada."})

    client = make_mock_client(handler)
    provider = OllamaProvider(client=client)

    result = await provider.generate("Simular taxa para crédito")
    assert result == "Simulação de taxa aprovada."


@pytest.mark.asyncio
async def test_ollama_configuration_driven() -> None:
    """Test that model name and host are strictly driven by configuration."""
    custom_settings = OllamaSettings(
        host="http://custom-ollama:11434",
        model="qwen2.5:7b",
        timeout_seconds=15.0,
        max_retries=1,
    )

    recorded_models: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url).startswith("http://custom-ollama:11434")
        data = json.loads(request.content)
        recorded_models.append(data["model"])
        return httpx.Response(200, json={"response": "OK"})

    client = make_mock_client(handler, base_url=custom_settings.host)
    provider = OllamaProvider(settings=custom_settings, client=client)

    await provider.generate("Hello")
    assert recorded_models == ["qwen2.5:7b"]


@pytest.mark.asyncio
async def test_ollama_timeout_and_retry_exhaustion() -> None:
    """Test that timeouts trigger retries and raise LLMTimeoutError when exhausted."""
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ReadTimeout("Mocked read timeout")

    client = make_mock_client(handler)
    settings = OllamaSettings(max_retries=2, timeout_seconds=1.0)
    provider = OllamaProvider(settings=settings, client=client)

    with pytest.raises(LLMTimeoutError) as exc_info:
        await provider.generate("Testing timeout")

    # 1 initial call + 2 retries = 3 attempts
    assert attempts == 3
    assert "timed out after 1.0s" in str(exc_info.value)


@pytest.mark.asyncio
async def test_ollama_transient_failure_recovery() -> None:
    """Test that a transient error recovers on the next retry attempt."""
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise httpx.ConnectError("Mocked transient network drop")
        return httpx.Response(200, json={"response": "Recuperado com sucesso"})

    client = make_mock_client(handler)
    settings = OllamaSettings(max_retries=2)
    provider = OllamaProvider(settings=settings, client=client)

    result = await provider.generate("Ping")
    assert result == "Recuperado com sucesso"
    assert attempts == 2


@pytest.mark.asyncio
async def test_ollama_generate_structured_success() -> None:
    """Test valid structured output parsing against Pydantic schema."""

    def handler(request: httpx.Request) -> httpx.Response:
        data = json.loads(request.content)
        assert data["format"] == "json"
        body = {
            "intent": "loan_simulation",
            "confidence": 0.98,
            "reasoning": "O cliente pediu simulação de crédito",
        }
        return httpx.Response(200, json={"response": json.dumps(body)})

    client = make_mock_client(handler)
    provider = OllamaProvider(client=client)

    structured = await provider.generate_structured(
        "Classifique a intenção",
        schema=MockIntentSchema,
    )
    assert isinstance(structured, MockIntentSchema)
    assert structured.intent == "loan_simulation"
    assert structured.confidence == 0.98


@pytest.mark.asyncio
async def test_ollama_structured_corrective_retry() -> None:
    """Test that a malformed JSON output is corrected via the second retry attempt."""
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            # Attempt 1 returns broken JSON
            return httpx.Response(200, json={"response": "not-valid-json { broken"})

        # Attempt 2 (corrective prompt) returns valid JSON
        body = {
            "intent": "tariff_consultation",
            "confidence": 0.85,
            "reasoning": "Corrigido após feedback",
        }
        return httpx.Response(200, json={"response": json.dumps(body)})

    client = make_mock_client(handler)
    provider = OllamaProvider(client=client)

    structured = await provider.generate_structured(
        "Classifique a intenção",
        schema=MockIntentSchema,
    )
    assert isinstance(structured, MockIntentSchema)
    assert structured.intent == "tariff_consultation"
    assert attempts == 2


@pytest.mark.asyncio
async def test_ollama_structured_output_exhausted_failure() -> None:
    """Test that unrecoverable invalid JSON raises StructuredOutputError."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"response": "{ invalid-json-both-times }"})

    client = make_mock_client(handler)
    provider = OllamaProvider(client=client)

    with pytest.raises(StructuredOutputError) as exc_info:
        await provider.generate_structured(
            "Prompt",
            schema=MockIntentSchema,
        )
    assert "MockIntentSchema" in str(exc_info.value)


@pytest.mark.asyncio
async def test_ollama_streaming() -> None:
    """Test streaming token generator from NDJSON response."""
    ndjson_lines = [
        json.dumps({"response": "Olá, ", "done": False}) + "\n",
        json.dumps({"response": "gerente!", "done": True}) + "\n",
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content="".join(ndjson_lines).encode("utf-8"),
            headers={"content-type": "application/x-ndjson"},
        )

    client = make_mock_client(handler)
    provider = OllamaProvider(client=client)

    tokens: list[str] = []
    async for token in provider.stream_generate("Diga olá"):
        tokens.append(token)

    assert tokens == ["Olá, ", "gerente!"]
