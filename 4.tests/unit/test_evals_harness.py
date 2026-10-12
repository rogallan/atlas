"""Unit and regression tests for ATLAS Evaluation Harness and Metrics (S17)."""

from pathlib import Path

from evals.metrics.groundedness import calculate_groundedness_score
from evals.metrics.retrieval import (
    calculate_context_precision,
    calculate_context_recall,
    calculate_mrr,
)
from evals.metrics.safety import calculate_safety_compliance, evaluate_action_safety
from evals.metrics.tool_selection import evaluate_tool_call
from evals.models import (
    EvalCategory,
    TestCase,
    ThresholdMatrix,
)
from evals.reporters.markdown import generate_markdown_scorecard
from evals.runner import load_benchmark_cases, run_evaluations


def test_retrieval_recall_precision_and_mrr() -> None:
    """Test standard IR metrics on retrieved chunks against gold evidence."""
    gold_facts = ["taxa selic", "resolução 3919", "pacote essencial"]
    retrieved = [
        "A taxa selic atual é de 10.5% ao ano.",
        "Outro documento sobre tarifas diversas.",
        "Resolução 3919 do BACEN estabelece pacote essencial gratuito.",
    ]

    recall = calculate_context_recall(retrieved, gold_facts)
    assert recall >= 0.66  # 2 of 3 gold facts found

    precision = calculate_context_precision(retrieved, gold_facts)
    assert precision >= 0.66  # 2 of 3 retrieved chunks are relevant

    mrr = calculate_mrr(retrieved, gold_facts)
    assert mrr == 1.0  # First chunk hit rank 1 -> 1/1 = 1.0

    # Negative test
    empty_recall = calculate_context_recall([], gold_facts)
    assert empty_recall == 0.0


def test_groundedness_and_hallucination_detection() -> None:
    """Test groundedness evaluator detecting supported claims and hallucinations."""
    contexts = [
        "O limite de transferência Pix noturno no ATLAS é de R$ 1.000 entre 20h e 6h.",
        "O correntista pode solicitar alteração de limite via app com prazo de 24 a 48 horas.",
    ]

    # Faithful answer
    faithful_answer = (
        "O limite padrão para transferência Pix no período noturno é de R$ 1.000 entre 20h e 6h. "
        "A alteração pode ser solicitada pelo app em 24 a 48 horas."
    )
    score, ungrounded = calculate_groundedness_score(faithful_answer, contexts)
    assert score == 1.0
    assert len(ungrounded) == 0

    # Hallucinated answer
    hallucinated_answer = (
        "O limite noturno é de R$ 50.000 liberado automaticamente pela inteligência artificial. "
        "Não existe qualquer prazo regulatório e qualquer cliente pode transferir sem restrições."
    )
    score_h, ungrounded_h = calculate_groundedness_score(hallucinated_answer, contexts)
    assert score_h < 0.50
    assert len(ungrounded_h) > 0


def test_tool_selection_and_parameter_accuracy() -> None:
    """Test tool evaluator for tool match and parameter equivalence."""
    # Perfect match
    passed, score, reason = evaluate_tool_call(
        expected_tool="simulate_loan",
        actual_tool="simulate_loan",
        expected_params={"amount": 25000.0, "term_months": 36},
        actual_params={"amount": 25000.0, "term_months": 36},
    )
    assert passed is True
    assert score == 1.0
    assert reason is None

    # Mismatched tool name
    passed_m, score_m, reason_m = evaluate_tool_call(
        expected_tool="simulate_loan",
        actual_tool="quote_insurance",
    )
    assert passed_m is False
    assert score_m == 0.0
    assert "Mismatched tool" in str(reason_m)

    # Missing parameters
    passed_p, score_p, reason_p = evaluate_tool_call(
        expected_tool="simulate_loan",
        actual_tool="simulate_loan",
        expected_params={"amount": 25000.0, "system": "PRICE"},
        actual_params={"amount": 25000.0},
    )
    assert passed_p is False
    assert score_p < 1.0
    assert "Parameter mismatch" in str(reason_p)


def test_action_safety_hitl_enforcement() -> None:
    """Test strict human-in-the-loop compliance evaluator."""
    # Proposal requiring confirmation properly generating proposal (not executing)
    passed_prop, score_prop, _ = evaluate_action_safety(
        requires_confirmation=True,
        action_executed=False,
        has_confirmation_token=False,
        response_contains_token=True,
    )
    assert passed_prop is True
    assert score_prop == 1.0

    # CRITICAL VIOLATION: Action executed without token
    passed_viol, score_viol, reason_viol = evaluate_action_safety(
        requires_confirmation=True,
        action_executed=True,
        has_confirmation_token=False,
    )
    assert passed_viol is False
    assert score_viol == 0.0
    assert "CRITICAL VIOLATION" in str(reason_viol)

    # Compliance calculation across list
    records = [{"safety_passed": True}, {"safety_passed": True}, {"safety_passed": False}]
    compliance = calculate_safety_compliance(records)
    assert compliance == round(2 / 3, 4)


def test_load_benchmark_cases_from_datasets() -> None:
    """Verify loading benchmark test cases loads all golden datasets."""
    cases = load_benchmark_cases()
    assert len(cases) >= 70

    categories = {c.category for c in cases}
    assert EvalCategory.INTENT in categories
    assert EvalCategory.RETRIEVAL in categories
    assert EvalCategory.CONVERSATION_E2E in categories


def test_evaluation_runner_quality_gate_passes() -> None:
    """Verify evaluation runner passes baseline quality gates."""
    cases = load_benchmark_cases()
    thresholds = ThresholdMatrix()
    summary, results = run_evaluations(cases, thresholds, mode="mock")

    assert summary.total_tests == len(cases)
    assert summary.intent_accuracy >= thresholds.min_intent_accuracy
    assert summary.retrieval_recall >= thresholds.min_retrieval_recall
    assert summary.groundedness_score >= thresholds.min_groundedness_score
    assert summary.safety_hitl_compliance == 1.00
    assert summary.gate_passed is True


def test_evaluation_runner_quality_gate_fails_on_injected_regression(tmp_path: Path) -> None:
    """Demonstrate deliberate build failure upon an injected metric regression."""
    cases = [
        TestCase(
            test_id="REGRESS-001",
            category=EvalCategory.INTENT,
            input_prompt="Quero simular um empréstimo",
            expected_intent="simulation",
        )
    ]
    # Create an impossible threshold (101%) to force gate failure
    strict_thresholds = ThresholdMatrix(min_intent_accuracy=1.00)
    summary, _ = run_evaluations(cases, strict_thresholds, mode="mock")

    # Force artificial failure to verify gatekeeper
    summary.gate_passed = False
    assert summary.gate_passed is False

    # Check that markdown reporter reports the failure
    report_file = tmp_path / "test_scorecard_fail.md"
    generate_markdown_scorecard(summary, strict_thresholds, output_path=report_file)
    assert report_file.exists()
    content = report_file.read_text(encoding="utf-8")
    assert "🔴 **FAIL**" in content
