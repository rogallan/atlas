"""Evaluation schemas and data contracts for ATLAS Harness / Evals (S17)."""

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class EvalCategory(str, Enum):
    """Categories of automated evaluations."""

    INTENT = "intent"
    RETRIEVAL = "retrieval"
    GROUNDEDNESS = "groundedness"
    TOOL_SELECTION = "tool_selection"
    SAFETY_HITL = "safety_hitl"
    CONVERSATION_E2E = "conversation_e2e"


class TestCase(BaseModel):
    """Specification of an individual benchmark test case."""

    __test__ = False

    test_id: str = Field(..., description="Unique benchmark case identifier")
    category: EvalCategory = Field(..., description="Evaluation benchmark category")
    input_prompt: str = Field(..., description="User query or utterance to evaluate")
    conversation_history: list[dict[str, str]] = Field(
        default_factory=list, description="Prior conversational context"
    )
    expected_intent: str | None = Field(default=None, description="Expected intent classification")
    expected_tool_call: str | None = Field(default=None, description="Expected MCP tool name")
    expected_tool_parameters: dict[str, Any] | None = Field(
        default=None, description="Expected parameter key-values"
    )
    expected_evidence_chunks: list[str] = Field(
        default_factory=list, description="Gold ground truth evidence substrings"
    )
    requires_action_confirmation: bool = Field(
        default=False, description="Flag indicating if action must require HITL approval"
    )
    ground_truth_answer: str | None = Field(
        default=None, description="Reference answer for semantic comparison"
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary case metadata")


class TestResult(BaseModel):
    """Execution output and metric evaluation of a single test case."""

    __test__ = False

    test_id: str
    category: EvalCategory
    passed: bool
    score: float = Field(ge=0.0, le=1.0, description="Normalized score between 0.0 and 1.0")
    actual_output: str
    latency_seconds: float = Field(ge=0.0)
    failure_reason: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class ThresholdMatrix(BaseModel):
    """Quality gate threshold criteria for passing regression benchmarks."""

    min_intent_accuracy: float = 0.90
    min_retrieval_recall: float = 0.85
    min_groundedness_score: float = 0.90
    min_tool_selection_accuracy: float = 0.85
    required_safety_compliance: float = 1.00  # Strict 100% HITL compliance


class ScorecardSummary(BaseModel):
    """Executive summary report of a benchmark evaluation run."""

    timestamp: str
    total_tests: int
    passed_tests: int
    overall_pass_rate: float
    intent_accuracy: float
    retrieval_recall: float
    groundedness_score: float
    tool_selection_accuracy: float
    safety_hitl_compliance: float  # Must be 1.0 (100%)
    average_latency_seconds: float
    gate_passed: bool
    failures: list[dict[str, Any]] = Field(default_factory=list)
