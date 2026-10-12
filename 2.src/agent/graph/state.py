"""Agent state models and step enumerations for Agent Graph (S14)."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from agent.router.models import IntentResult


class AgentStep(StrEnum):
    """Execution step states for the Agent Graph state machine."""

    ROUTER = "router"
    RAG = "rag"
    MCP = "mcp"
    CLARIFICATION = "clarification"
    VALIDATOR = "validator"
    SYNTHESIZER = "synthesizer"
    CONFIRMATION_CARD = "confirmation_card"
    FALLBACK = "fallback"
    END = "end"


class AgentState(BaseModel):
    """Central state passed across all nodes in the Agent Graph orchestrator."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    session_id: str = Field(..., description="Unique conversational session identifier.")
    user_message: str = Field(..., description="Current user/manager prompt text.")
    history: list[dict[str, str]] = Field(
        default_factory=list,
        description="Prior conversational turns in session: [{'role': ..., 'content': ...}].",
    )
    step_count: int = Field(default=0, description="Counter of graph transitions in this turn.")
    max_steps: int = Field(default=5, description="Maximum allowed graph transitions before abort.")
    node_history: list[str] = Field(
        default_factory=list,
        description="Chronological audit list of visited graph nodes.",
    )
    current_step: AgentStep = Field(
        default=AgentStep.ROUTER,
        description="Current execution step in state graph.",
    )

    # Intermediate node outputs
    intent_decision: IntentResult | None = Field(
        default=None,
        description="Result produced by Router Node (intent, confidence, entities).",
    )
    retrieved_context: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Retrieved chunks and text passages from RAG node.",
    )
    tool_outputs: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Structured outputs from MCP domain tools.",
    )

    # Critic & Guardrails status
    is_grounded: bool = Field(
        default=True,
        description="Validation flag indicating factual claims are anchored in context.",
    )
    requires_human_confirmation: bool = Field(
        default=False,
        description="Flag indicating an action tool requires explicit human approval.",
    )
    confirmation_payload: dict[str, Any] | None = Field(
        default=None,
        description="Draft parameters and token presented for human approval.",
    )
    security_blocked: bool = Field(
        default=False,
        description="Flag indicating request was blocked by prompt injection/guardrails.",
    )

    # Final outputs
    final_response: str | None = Field(
        default=None,
        description="Final synthesized response to return to the user.",
    )
    citations: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Document citations attached to final response.",
    )
    error_message: str | None = Field(
        default=None,
        description="Error detail or fallback explanation if execution failed.",
    )
    operator_id: str = Field(
        default="manager_001",
        description="Identifier of current relationship manager.",
    )
