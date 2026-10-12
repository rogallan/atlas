"""Simulated authorization and structured audit logging for MCP Customer Server (S08)."""

import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from mcp.customer.models import UnauthorizedError

logger = logging.getLogger("atlas.mcp.customer.audit")

ALLOWED_ROLES: set[str] = {
    "relationship_manager",
    "manager",
    "analyst",
    "admin",
    "system",
}


class AuthContext(BaseModel):
    """Simulated security context identifying the operator calling the MCP tool."""

    model_config = ConfigDict(extra="ignore")

    operator_id: str = Field(
        default="SIM-MGR-001",
        description="Operator/Manager unique identifier",
    )
    role: str = Field(
        default="relationship_manager",
        description="Assigned role (e.g. relationship_manager, analyst)",
    )
    branch_id: str = Field(
        default="0001",
        description="Bank branch identifier",
    )


class AuditEvent(BaseModel):
    """Structured audit log entry recording customer data access."""

    model_config = ConfigDict(extra="ignore")

    event: str = "customer_data_access"
    timestamp: str = Field(description="ISO 8601 UTC timestamp")
    correlation_id: str = Field(description="Unique correlation ID for request tracing")
    operator_id: str = Field(description="Identifier of the operator performing the lookup")
    role: str = Field(description="Role of the operator")
    customer_id: str = Field(description="Target synthetic customer ID accessed")
    tool: str = Field(description="MCP tool name executed")
    status: str = Field(description="success, denied, or not_found")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional audit metadata")


class SecurityManager:
    """Manages simulated role authorization and emits structured audit logs."""

    def __init__(self, allowed_roles: set[str] | None = None) -> None:
        """Initialize security manager.

        Args:
            allowed_roles: Set of roles permitted to invoke customer tools.
        """
        self.allowed_roles = allowed_roles or set(ALLOWED_ROLES)
        self.audit_log: list[AuditEvent] = []

    def verify_authorization(
        self,
        auth_context: AuthContext | None,
        tool: str,
        customer_id: str,
    ) -> AuthContext:
        """Verify the caller has a valid relationship manager role.

        Args:
            auth_context: Provided operator credentials (defaults to simulated manager if None).
            tool: Name of the invoked tool.
            customer_id: Queried customer identifier.

        Returns:
            Resolved AuthContext.

        Raises:
            UnauthorizedError: If role is not permitted.
        """
        context = auth_context or AuthContext()
        role_normalized = context.role.strip().lower()

        if role_normalized not in self.allowed_roles:
            self.record_audit(
                operator_id=context.operator_id,
                role=context.role,
                customer_id=customer_id,
                tool=tool,
                status="denied",
                details={"reason": f"Role '{context.role}' is not in permitted roles"},
            )
            raise UnauthorizedError(
                f"Acesso negado: o perfil '{context.role}' não tem permissão "
                f"para a ferramenta '{tool}'."
            )

        return context

    def record_audit(
        self,
        operator_id: str,
        role: str,
        customer_id: str,
        tool: str,
        status: str,
        correlation_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """Record a structured audit log entry."""
        event = AuditEvent(
            timestamp=datetime.now(UTC).isoformat(),
            correlation_id=correlation_id or str(uuid.uuid4()),
            operator_id=operator_id,
            role=role,
            customer_id=customer_id,
            tool=tool,
            status=status,
            details=details or {},
        )

        self.audit_log.append(event)
        logger.info("AUDIT_LOG %s", json.dumps(event.model_dump()))
        return event
