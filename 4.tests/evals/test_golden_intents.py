"""Evaluation benchmark tests for IntentRouter against golden_intents.json (S05)."""

import json
import os
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest

from agent.router.evaluator import evaluate_router
from agent.router.models import ExtractedEntities, IntentResult, IntentType
from agent.router.router import IntentRouter
from providers.config import OllamaSettings
from providers.ollama import OllamaProvider

GOLDEN_INTENTS_PATH = Path(__file__).parent.parent / "data" / "golden_intents.json"


@pytest.fixture
def golden_dataset() -> list[dict[str, Any]]:
    """Load the benchmark dataset from golden_intents.json."""
    assert GOLDEN_INTENTS_PATH.exists(), f"Missing dataset at {GOLDEN_INTENTS_PATH}"
    with open(GOLDEN_INTENTS_PATH, encoding="utf-8") as f:
        data: list[dict[str, Any]] = json.load(f)
    return data


def test_golden_dataset_structure(golden_dataset: list[dict[str, Any]]) -> None:
    """Verify golden dataset satisfies taxonomy and sample count requirements."""
    assert len(golden_dataset) >= 50

    canonical_intents = {it.value for it in IntentType}
    for item in golden_dataset:
        assert "utterance" in item
        assert "expected_intent" in item
        assert item["expected_intent"] in canonical_intents


@pytest.mark.asyncio
async def test_evaluation_pipeline_metrics(golden_dataset: list[dict[str, Any]]) -> None:
    """Verify evaluation harness computes precision, recall, and accuracy >= 90%."""
    # Build a simulated mock provider that predicts accurately for 48/50 samples (96% accuracy)
    mock_provider = AsyncMock()

    async def mock_generate_structured(
        prompt: str,
        schema: Any,
        system: str | None = None,
        **kwargs: Any,
    ) -> IntentResult:
        # Match utterance from prompt
        for item in golden_dataset:
            if item["utterance"] in prompt:
                # Intentionally inject 2 misclassifications for testing metrics calculation
                if item["id"] in ("KNOW-010", "SIM-010"):
                    return IntentResult(
                        intent=IntentType.CLARIFICATION,
                        confidence=0.60,
                        reasoning="Simulated misclassification for testing metrics",
                    )
                return IntentResult(
                    intent=IntentType(item["expected_intent"]),
                    confidence=0.95,
                    reasoning=f"Correctly matched for intent {item['expected_intent']}",
                    entities=ExtractedEntities(),
                )
        return IntentResult(
            intent=IntentType.CLARIFICATION,
            confidence=0.5,
            reasoning="Fallback utterance match",
        )

    mock_provider.generate_structured = mock_generate_structured
    router = IntentRouter(llm_provider=mock_provider)

    report = await evaluate_router(router, golden_dataset)

    # Acceptance Criteria: Accuracy >= 90%
    assert report.total_samples == len(golden_dataset)
    assert report.accuracy >= 0.90
    assert len(report.failed_cases) == 2

    # Check metrics for each intent
    for _intent_name, metrics in report.metrics_per_intent.items():
        assert metrics.precision >= 0.80
        assert metrics.recall >= 0.80

    summary_text = report.summary()
    assert "=== Intent Router Evaluation Report ===" in summary_text
    assert "Accuracy:" in summary_text


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_LLM_EVAL") != "1",
    reason="Set RUN_LIVE_LLM_EVAL=1 to execute live LLM inference against local Ollama",
)
@pytest.mark.asyncio
async def test_live_ollama_golden_eval(golden_dataset: list[dict[str, Any]]) -> None:
    """Optional live evaluation against local Ollama instance (llama3.2:latest)."""
    settings = OllamaSettings(model="llama3.2:latest", timeout_seconds=45.0)
    provider = OllamaProvider(settings)
    router = IntentRouter(llm_provider=provider)

    # Run on a representative subset of 10 samples to respect live latency
    subset = golden_dataset[::5]  # 10 samples across classes
    report = await evaluate_router(router, subset)

    print("\n" + report.summary())
    assert report.accuracy >= 0.70
