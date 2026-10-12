"""Data models and custom exceptions for ATLAS MCP Ticket Server (S13)."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class TicketCategory(StrEnum):
    """Categorization taxonomy for synthetic customer service tickets."""

    CONTESTATION = "contestation"
    CARD_MAINTENANCE = "card_maintenance"
    LIMIT_INCREASE = "limit_increase"
    TARIFF_REVIEW = "tariff_review"
    GENERAL_INQUIRY = "general_inquiry"


class TicketPriority(StrEnum):
    """Priority levels for service tickets."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketStatus(StrEnum):
    """Lifecycle status of a ticket."""

    PENDING_APPROVAL = "pending_approval"
    OPEN = "open"
    IN_ANALYSIS = "in_analysis"
    REJECTED = "rejected"
    CLOSED = "closed"


class TicketDraft(BaseModel):
    """Pending ticket draft emitted during Phase 1 (Preparation) awaiting human approval."""

    confirmation_token: str = Field(
        ...,
        description="Cryptographic single-use token required to authorize ticket creation.",
    )
    customer_id: str = Field(
        ...,
        description="Target synthetic customer ID (e.g. CUST-001).",
    )
    category: TicketCategory = Field(
        ...,
        description="Ticket category taxonomy.",
    )
    title: str = Field(
        ...,
        description="Brief subject/title of the ticket.",
    )
    description: str = Field(
        ...,
        description="Detailed description of the customer request or issue.",
    )
    priority: TicketPriority = Field(
        default=TicketPriority.MEDIUM,
        description="Operational urgency level.",
    )
    created_at: datetime = Field(
        ...,
        description="Draft creation timestamp (UTC).",
    )
    expires_at: datetime = Field(
        ...,
        description="Token expiration timestamp (UTC) after which the draft is invalid.",
    )
    summary_for_human: str = Field(
        ...,
        description="Human-readable summary presented to relationship manager for confirmation.",
    )
    status: TicketStatus = Field(
        default=TicketStatus.PENDING_APPROVAL,
        description="Initial draft status.",
    )
    idempotency_key: str | None = Field(
        default=None,
        description="Client-provided idempotency key for deduplication.",
    )


class TicketRecord(BaseModel):
    """Committed ticket record created upon affirmative human approval (Phase 2)."""

    ticket_id: str = Field(
        ...,
        description="Unique identifier of the committed ticket (e.g. TCK-2026-00001).",
    )
    customer_id: str = Field(
        ...,
        description="Target customer ID.",
    )
    category: TicketCategory = Field(
        ...,
        description="Category taxonomy.",
    )
    title: str = Field(
        ...,
        description="Ticket title.",
    )
    description: str = Field(
        ...,
        description="Ticket detailed description.",
    )
    priority: TicketPriority = Field(
        ...,
        description="Priority level.",
    )
    status: TicketStatus = Field(
        ...,
        description="Current ticket status.",
    )
    created_at: datetime = Field(
        ...,
        description="Commit timestamp (UTC).",
    )
    approved_by_user: bool = Field(
        ...,
        description="Flag indicating explicit human confirmation occurred.",
    )
    operator_id: str = Field(
        ...,
        description="Identity of the operator / relationship manager who confirmed the action.",
    )
    idempotency_key: str | None = Field(
        default=None,
        description="Associated idempotency key if supplied.",
    )
    resolution_notes: str | None = Field(
        default=None,
        description="Optional operational or resolution notes.",
    )


class PrepareTicketInput(BaseModel):
    """Input payload for prepare_ticket tool."""

    customer_id: str = Field(
        ...,
        description="Target customer ID (e.g. CUST-001).",
    )
    category: TicketCategory = Field(
        ...,
        description=(
            "Ticket category (contestation, card_maintenance, "
            "limit_increase, tariff_review, general_inquiry)."
        ),
    )
    title: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Concise summary title of the ticket.",
    )
    description: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Detailed description of the issue or operational request.",
    )
    priority: TicketPriority = Field(
        default=TicketPriority.MEDIUM,
        description="Priority level (low, medium, high, urgent).",
    )
    operator_id: str = Field(
        default="manager_001",
        description="Identifier of the operator initiating the draft.",
    )
    idempotency_key: str | None = Field(
        default=None,
        description="Optional client idempotency key for deduplication.",
    )


class ConfirmAndCreateTicketInput(BaseModel):
    """Input payload for confirm_and_create_ticket tool."""

    confirmation_token: str = Field(
        ...,
        description="Cryptographic confirmation token received from prepare_ticket.",
    )
    approved_by_user: bool = Field(
        ...,
        description="Mandatory flag indicating whether the human operator approved the action.",
    )
    idempotency_key: str | None = Field(
        default=None,
        description="Optional client idempotency key to prevent duplicate creation.",
    )
    operator_id: str = Field(
        default="manager_001",
        description="Identifier of the operator confirming the action.",
    )


class GetTicketInput(BaseModel):
    """Input payload for get_ticket tool."""

    ticket_id: str = Field(
        ...,
        description="Identifier of the ticket to retrieve (e.g. TCK-2026-00001).",
    )


class ListCustomerTicketsInput(BaseModel):
    """Input payload for list_customer_tickets tool."""

    customer_id: str = Field(
        ...,
        description="Customer ID whose tickets should be retrieved.",
    )


# ---------------------------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------------------------


class MCPTicketError(Exception):
    """Base exception for all MCP Ticket Server errors."""

    def __init__(self, message: str, code: int = -32000, data: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data


class TicketNotFoundError(MCPTicketError):
    """Raised when a requested ticket ID does not exist."""

    def __init__(self, ticket_id: str) -> None:
        super().__init__(
            message=f"Ticket not found: '{ticket_id}'.",
            code=-32001,
            data={"ticket_id": ticket_id},
        )


class InvalidTokenError(MCPTicketError):
    """Raised when a confirmation token is invalid, missing, or already consumed."""

    def __init__(self, token: str) -> None:
        super().__init__(
            message=f"Confirmation token is invalid or has already been used: '{token}'.",
            code=-32002,
            data={"confirmation_token": token},
        )


class TokenExpiredError(MCPTicketError):
    """Raised when a confirmation token has exceeded its Time-To-Live (TTL)."""

    def __init__(self, token: str, expired_at: str) -> None:
        super().__init__(
            message=f"Confirmation token expired at {expired_at}: '{token}'.",
            code=-32003,
            data={"confirmation_token": token, "expired_at": expired_at},
        )


class ActionRejectedError(MCPTicketError):
    """Raised when ticket creation is rejected by the human operator."""

    def __init__(self, token: str, operator_id: str) -> None:
        super().__init__(
            message=(
                f"Ticket creation was explicitly rejected by human operator '{operator_id}'. "
                "State not mutated."
            ),
            code=-32004,
            data={"confirmation_token": token, "operator_id": operator_id},
        )


class InvalidTicketParameterError(MCPTicketError):
    """Raised when input parameters fail semantic validation."""

    def __init__(self, reason: str) -> None:
        super().__init__(
            message=f"Invalid ticket parameters: {reason}",
            code=-32005,
            data={"reason": reason},
        )
