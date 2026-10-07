"""Data contracts and Pydantic models for Intent Routing (S05)."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IntentType(StrEnum):
    """Canonical banking intent taxonomy."""

    KNOWLEDGE = "knowledge"
    QUERY = "query"
    SIMULATION = "simulation"
    ACTION = "action"
    CLARIFICATION = "clarification"


class ExtractedEntities(BaseModel):
    """Domain entities extracted from customer relationship manager requests."""

    model_config = ConfigDict(extra="ignore")

    customer_id: str | None = Field(
        default=None,
        description="Synthetic customer identifier or CPF",
    )
    customer_name: str | None = Field(
        default=None,
        description="Customer full or partial name if mentioned",
    )
    product_type: str | None = Field(
        default=None,
        description="Banking product category: loan, insurance, consortium, tariff, ticket, etc.",
    )
    amount: float | None = Field(
        default=None,
        description="Monetary transaction, loan or quote value if mentioned",
    )
    term_months: int | None = Field(
        default=None,
        description="Number of installment months or investment duration",
    )
    raw_entities: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional domain-specific key-value pairs extracted from utterance",
    )


class IntentResult(BaseModel):
    """Strictly validated structured classification result."""

    model_config = ConfigDict(extra="ignore")

    intent: IntentType = Field(
        description="Classified canonical intent from taxonomy",
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Model confidence score between 0.0 and 1.0",
    )
    reasoning: str = Field(
        description="Concise rationale explaining the classification decision",
    )
    entities: ExtractedEntities = Field(
        default_factory=ExtractedEntities,
        description="Extracted domain entities and parameters",
    )
    suggested_clarification: str | None = Field(
        default=None,
        description="Follow-up clarification question if the request is ambiguous or incomplete",
    )
