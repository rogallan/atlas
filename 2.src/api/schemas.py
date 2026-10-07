"""Typed OpenAPI request and response models for the FastAPI Gateway (S03)."""

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="ok", description="Liveness and readiness status")
    version: str = Field(..., description="API version")
    uptime_seconds: float = Field(..., ge=0.0, description="Uptime in seconds")


class CreateSessionRequest(BaseModel):
    """Payload to initialize a conversation session."""

    manager_id: str = Field(
        default="MGR-001",
        description="Simulated bank relationship manager ID",
    )
    branch_id: str = Field(
        default="BR-0101",
        description="Simulated bank branch ID",
    )


class SessionResponse(BaseModel):
    """Response returned upon session creation."""

    session_id: str = Field(..., description="Unique UUID for conversation correlation")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")
    manager_id: str = Field(..., description="Manager ID owning the session")


class ChatRequest(BaseModel):
    """Incoming chat message from the relationship manager."""

    session_id: str = Field(..., min_length=1, description="Correlated conversation session ID")
    message: str = Field(..., min_length=1, description="User prompt or query")
    customer_id: str | None = Field(
        default=None,
        description="Optional active customer context (e.g. CUST-0001 Dave Weckl)",
    )


class ChatEvent(BaseModel):
    """Individual Server-Sent Event (SSE) payload."""

    event: str = Field(..., description="Event type: token, citation, tool_call, or done")
    data: dict[str, Any] = Field(default_factory=dict, description="Event payload data")


class ErrorDetail(BaseModel):
    """Standardized error details body."""

    code: str = Field(..., description="Machine-readable error code, e.g. UNAUTHORIZED")
    message: str = Field(..., description="Human-readable error description")
    details: Any | None = Field(default=None, description="Optional extra error context")


class ErrorEnvelope(BaseModel):
    """Top-level error response envelope required by S03 architecture."""

    error: ErrorDetail
