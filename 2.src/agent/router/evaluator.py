"""Evaluation harness for measuring IntentRouter performance against benchmark datasets (S05)."""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from agent.router.models import IntentType
from agent.router.router import IntentRouter


@dataclass
class IntentMetrics:
    """Precision, recall, and F1 score for a single intent category."""

    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0

    @property
    def precision(self) -> float:
        total = self.true_positives + self.false_positives
        return self.true_positives / total if total > 0 else 0.0

    @property
    def recall(self) -> float:
        total = self.true_positives + self.false_negatives
        return self.true_positives / total if total > 0 else 0.0

    @property
    def f1_score(self) -> float:
        p, r = self.precision, self.recall
        return (2 * p * r) / (p + r) if (p + r) > 0 else 0.0


@dataclass
class IntentEvaluationReport:
    """Comprehensive evaluation metrics and confusion analysis."""

    total_samples: int = 0
    correct_count: int = 0
    accuracy: float = 0.0
    metrics_per_intent: dict[str, IntentMetrics] = field(default_factory=dict)
    confusion_matrix: dict[str, dict[str, int]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(int))
    )
    failed_cases: list[dict[str, Any]] = field(default_factory=list)

    def summary(self) -> str:
        """Format an evaluation summary table."""
        lines = [
            "=== Intent Router Evaluation Report ===",
            f"Total Samples: {self.total_samples}",
            f"Correct:       {self.correct_count}",
            f"Accuracy:      {self.accuracy * 100:.2f}%",
            "",
            f"{'Intent':<15} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}",
            "-" * 55,
        ]
        for intent_name, metrics in sorted(self.metrics_per_intent.items()):
            p, r, f1 = metrics.precision, metrics.recall, metrics.f1_score
            lines.append(f"{intent_name:<15} | {p:<10.2f} | {r:<10.2f} | {f1:<10.2f}")
        return "\n".join(lines)


async def evaluate_router(
    router: IntentRouter,
    dataset: list[dict[str, Any]],
) -> IntentEvaluationReport:
    """Evaluate an IntentRouter instance against a dataset of labeled queries.

    Args:
        router: The IntentRouter instance to evaluate.
        dataset: List of dicts with 'utterance' (or 'query') and 'expected_intent'.

    Returns:
        IntentEvaluationReport containing accuracy, per-intent metrics, and confusion matrix.
    """
    report = IntentEvaluationReport(total_samples=len(dataset))
    all_intents = [it.value for it in IntentType]
    for intent_name in all_intents:
        report.metrics_per_intent[intent_name] = IntentMetrics()

    correct = 0

    for sample in dataset:
        utterance = sample.get("utterance") or sample.get("query", "")
        expected_intent = sample["expected_intent"]
        context = sample.get("context")

        result = await router.route(utterance, context=context)
        actual_intent = result.intent.value

        report.confusion_matrix[expected_intent][actual_intent] += 1

        if actual_intent == expected_intent:
            correct += 1
            if expected_intent in report.metrics_per_intent:
                report.metrics_per_intent[expected_intent].true_positives += 1
        else:
            if actual_intent in report.metrics_per_intent:
                report.metrics_per_intent[actual_intent].false_positives += 1
            if expected_intent in report.metrics_per_intent:
                report.metrics_per_intent[expected_intent].false_negatives += 1

            report.failed_cases.append(
                {
                    "utterance": utterance,
                    "expected": expected_intent,
                    "predicted": actual_intent,
                    "confidence": result.confidence,
                    "reasoning": result.reasoning,
                }
            )

    report.correct_count = correct
    report.accuracy = correct / len(dataset) if dataset else 0.0
    return report
