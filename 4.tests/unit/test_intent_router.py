"""Unit tests for IntentRouter and domain models (S05)."""

from typing import Any
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from agent.router.models import ExtractedEntities, IntentResult, IntentType
from agent.router.prompts import build_classification_prompt
from agent.router.router import IntentRouter
from providers.base import LLMProviderError, LLMTimeoutError, StructuredOutputError


class MockLLMProvider:
    """Mock implementation of LLMProvider protocol for fast deterministic testing."""

    def __init__(self, return_value: Any = None, side_effect: Exception | None = None) -> None:
        self.generate_structured = AsyncMock(
            return_value=return_value,
            side_effect=side_effect,
        )
        self.generate = AsyncMock()
        self.stream_generate = AsyncMock()


def test_intent_result_validation() -> None:
    """Verify IntentResult model schema constraints."""
    result = IntentResult(
        intent=IntentType.QUERY,
        confidence=0.95,
        reasoning="Consulta de saldo para cliente Dave Weckl.",
        entities=ExtractedEntities(customer_name="Dave Weckl"),
    )
    assert result.intent == IntentType.QUERY
    assert result.confidence == 0.95
    assert result.entities.customer_name == "Dave Weckl"

    # Confidence must be between 0.0 and 1.0
    with pytest.raises(ValidationError):
        IntentResult(
            intent=IntentType.QUERY,
            confidence=1.5,
            reasoning="Invalid confidence",
        )

    with pytest.raises(ValidationError):
        IntentResult(
            intent=IntentType.QUERY,
            confidence=-0.1,
            reasoning="Invalid confidence",
        )


@pytest.mark.asyncio
async def test_route_empty_message() -> None:
    """Empty or whitespace message should return clarification without invoking LLM."""
    mock_provider = MockLLMProvider()
    router = IntentRouter(llm_provider=mock_provider)

    result = await router.route("   ")
    assert result.intent == IntentType.CLARIFICATION
    assert result.confidence == 1.0
    assert result.suggested_clarification is not None
    mock_provider.generate_structured.assert_not_called()


@pytest.mark.asyncio
async def test_route_successful_query() -> None:
    """Successful classification returns parsed IntentResult."""
    expected_result = IntentResult(
        intent=IntentType.QUERY,
        confidence=0.98,
        reasoning="Pergunta de leitura sobre saldo bancário.",
        entities=ExtractedEntities(customer_name="Dave Weckl"),
    )
    mock_provider = MockLLMProvider(return_value=expected_result)
    router = IntentRouter(llm_provider=mock_provider)

    result = await router.route("Qual o saldo de Dave Weckl?")
    assert result.intent == IntentType.QUERY
    assert result.confidence == 0.98
    assert result.entities.customer_name == "Dave Weckl"
    mock_provider.generate_structured.assert_called_once()


@pytest.mark.asyncio
async def test_route_low_confidence_override() -> None:
    """Classification with confidence below threshold overrides to CLARIFICATION."""
    low_confidence_result = IntentResult(
        intent=IntentType.SIMULATION,
        confidence=0.50,  # below default 0.70
        reasoning="Possível pedido de cálculo, mas pouco claro.",
        entities=ExtractedEntities(),
    )
    mock_provider = MockLLMProvider(return_value=low_confidence_result)
    router = IntentRouter(
        llm_provider=mock_provider,
        confidence_threshold=0.70,
    )

    result = await router.route("Faz uma conta aí de empréstimo talvez")
    assert result.intent == IntentType.CLARIFICATION
    assert result.suggested_clarification is not None
    assert "Sua solicitação parece um pouco vaga" in result.suggested_clarification


@pytest.mark.asyncio
async def test_route_clarification_populates_missing_question() -> None:
    """If model classifies as CLARIFICATION without suggested question, router provides default."""
    clarification_result = IntentResult(
        intent=IntentType.CLARIFICATION,
        confidence=0.85,
        reasoning="Mensagem ambígua.",
        suggested_clarification=None,
    )
    mock_provider = MockLLMProvider(return_value=clarification_result)
    router = IntentRouter(llm_provider=mock_provider)

    result = await router.route("Quero ver aquele assunto")
    assert result.intent == IntentType.CLARIFICATION
    assert result.suggested_clarification is not None


@pytest.mark.asyncio
async def test_route_handles_timeout_gracefully() -> None:
    """LLMTimeoutError results in fallback CLARIFICATION without throwing."""
    mock_provider = MockLLMProvider(
        side_effect=LLMTimeoutError("Request timed out", details={"timeout": 30.0})
    )
    router = IntentRouter(llm_provider=mock_provider)

    result = await router.route("Simule um consórcio de 200 mil")
    assert result.intent == IntentType.CLARIFICATION
    assert result.confidence == 0.0
    assert "Falha de comunicação" in result.reasoning
    assert result.suggested_clarification is not None


@pytest.mark.asyncio
async def test_route_handles_provider_error_gracefully() -> None:
    """LLMProviderError results in fallback CLARIFICATION without crashing."""
    mock_provider = MockLLMProvider(side_effect=LLMProviderError("Connection refused by Ollama"))
    router = IntentRouter(llm_provider=mock_provider)

    result = await router.route("Qual o extrato de Buddy Rich?")
    assert result.intent == IntentType.CLARIFICATION
    assert result.confidence == 0.0
    assert "Falha de comunicação" in result.reasoning


@pytest.mark.asyncio
async def test_route_handles_structured_output_error_gracefully() -> None:
    """StructuredOutputError results in fallback CLARIFICATION without crashing."""
    mock_provider = MockLLMProvider(
        side_effect=StructuredOutputError("Failed to parse JSON response")
    )
    router = IntentRouter(llm_provider=mock_provider)

    result = await router.route("Abra um chamado")
    assert result.intent == IntentType.CLARIFICATION
    assert result.confidence == 0.0
    assert "Falha de comunicação" in result.reasoning


@pytest.mark.asyncio
async def test_route_handles_unexpected_error_gracefully() -> None:
    """Generic unexpected exception results in fallback CLARIFICATION."""
    mock_provider = MockLLMProvider(side_effect=RuntimeError("Unexpected OS level glitch"))
    router = IntentRouter(llm_provider=mock_provider)

    result = await router.route("Qualquer pergunta")
    assert result.intent == IntentType.CLARIFICATION
    assert result.confidence == 0.0
    assert "Erro inesperado" in result.reasoning


def test_build_classification_prompt() -> None:
    """Verify prompt formatting includes system prompt, context, and user message."""
    context = [
        {"role": "user", "content": "Olá"},
        {"role": "assistant", "content": "Olá, como posso ajudar?"},
    ]
    sys_prompt, user_prompt = build_classification_prompt("Qual a Selic?", context=context)

    assert "Roteador de Intenções" in sys_prompt
    assert "Histórico recente de mensagens:" in user_prompt
    assert "Qual a Selic?" in user_prompt
