"""Intent Router service integrating LLMProvider for banking classification (S05)."""

import logging
from typing import Any

from agent.router.models import IntentResult, IntentType
from agent.router.prompts import build_classification_prompt
from providers.base import LLMProvider, LLMProviderError, LLMTimeoutError, StructuredOutputError
from providers.config import OllamaSettings
from providers.ollama import OllamaProvider

logger = logging.getLogger(__name__)

DEFAULT_CONFIDENCE_THRESHOLD = 0.70
DEFAULT_CLARIFICATION_QUESTION = (
    "Sua solicitação parece um pouco vaga. Você gostaria de consultar dados de um cliente, "
    "fazer uma simulação financeira ou abrir um chamado?"
)


class IntentRouter:
    """Classifies user queries into canonical banking intents with structured entity extraction."""

    def __init__(
        self,
        llm_provider: LLMProvider | None = None,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        fallback_intent: IntentType = IntentType.CLARIFICATION,
    ) -> None:
        """Initialize the Intent Router.

        Args:
            llm_provider: Concrete LLMProvider implementation (defaults to OllamaProvider).
            confidence_threshold: Minimum confidence score required before clarification.
            fallback_intent: Default intent when provider fails or timeout occurs.
        """
        self.llm_provider: LLMProvider = (
            llm_provider if llm_provider is not None else OllamaProvider(OllamaSettings())
        )
        self.confidence_threshold = confidence_threshold
        self.fallback_intent = fallback_intent

    async def route(
        self,
        message: str,
        context: list[dict[str, str]] | None = None,
        **kwargs: Any,
    ) -> IntentResult:
        """Route an incoming message to a canonical banking intent.

        Args:
            message: User query string.
            context: Optional conversation history.
            **kwargs: Extra parameters passed to the LLM provider.

        Returns:
            Validated IntentResult instance.
        """
        clean_message = message.strip()
        if not clean_message:
            return IntentResult(
                intent=IntentType.CLARIFICATION,
                confidence=1.0,
                reasoning="Empty input message received.",
                suggested_clarification="Como posso ajudar você hoje?",
            )

        system_prompt, user_prompt = build_classification_prompt(
            message=clean_message,
            context=context,
        )

        try:
            result = await self.llm_provider.generate_structured(
                prompt=user_prompt,
                schema=IntentResult,
                system=system_prompt,
                **kwargs,
            )
        except (LLMTimeoutError, LLMProviderError, StructuredOutputError) as exc:
            logger.warning("LLM provider failure during intent classification: %s", exc)
            return IntentResult(
                intent=self.fallback_intent,
                confidence=0.0,
                reasoning=f"Falha de comunicação ou estruturação com o modelo: {exc}",
                suggested_clarification=(
                    "Não consegui compreender sua solicitação no momento devido a uma "
                    "indisponibilidade temporária. Poderia tentar novamente ou detalhar "
                    "o que precisa?"
                ),
            )
        except Exception as exc:
            logger.error("Unexpected error in intent router: %s", exc, exc_info=True)
            return IntentResult(
                intent=self.fallback_intent,
                confidence=0.0,
                reasoning=f"Erro inesperado no roteador de intenções: {exc}",
                suggested_clarification=(
                    "Ocorreu uma instabilidade inesperada. Poderia repetir sua solicitação?"
                ),
            )

        # Post-processing: confidence threshold check & ambiguity enforcement
        if result.confidence < self.confidence_threshold:
            logger.info(
                "Confidence (%.2f) below threshold (%.2f). Overriding to clarification.",
                result.confidence,
                self.confidence_threshold,
            )
            result.intent = IntentType.CLARIFICATION
            if not result.suggested_clarification:
                result.suggested_clarification = DEFAULT_CLARIFICATION_QUESTION

        if result.intent == IntentType.CLARIFICATION and not result.suggested_clarification:
            result.suggested_clarification = DEFAULT_CLARIFICATION_QUESTION

        return result
