"""Structured security audit trail logger for ATLAS MCP Ticket Server (S13)."""

import json
import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger("atlas.mcp.ticket.audit")


class TicketAuditLogger:
    """Security audit logger capturing lifecycle events and human authorizations."""

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def log_event(
        self,
        event_type: str,
        *,
        operator_id: str,
        customer_id: str,
        ticket_id: str | None = None,
        confirmation_token: str | None = None,
        approved_by_human: bool | None = None,
        category: str | None = None,
        priority: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Record and log a structured audit event."""
        payload: dict[str, Any] = {
            "event": event_type,
            "timestamp": datetime.now(UTC).isoformat(),
            "operator_id": operator_id,
            "customer_id": customer_id,
            "ticket_id": ticket_id,
            "confirmation_token": confirmation_token,
            "approved_by_human": approved_by_human,
            "category": category,
            "priority": priority,
            "details": details or {},
        }
        self._events.append(payload)
        logger.info("AUDIT_EVENT: %s", json.dumps(payload, ensure_ascii=False))
        return payload

    def log_draft_prepared(
        self,
        *,
        operator_id: str,
        customer_id: str,
        confirmation_token: str,
        category: str,
        priority: str,
        expires_at: str,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Record draft preparation awaiting human approval."""
        return self.log_event(
            "ticket_draft_prepared",
            operator_id=operator_id,
            customer_id=customer_id,
            confirmation_token=confirmation_token,
            approved_by_human=None,
            category=category,
            priority=priority,
            details={"expires_at": expires_at, "idempotency_key": idempotency_key},
        )

    def log_action_executed(
        self,
        *,
        operator_id: str,
        customer_id: str,
        ticket_id: str,
        confirmation_token: str,
        category: str,
        priority: str,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Record ticket creation executed after explicit human approval."""
        return self.log_event(
            "ticket_action_executed",
            operator_id=operator_id,
            customer_id=customer_id,
            ticket_id=ticket_id,
            confirmation_token=confirmation_token,
            approved_by_human=True,
            category=category,
            priority=priority,
            details={"idempotency_key": idempotency_key},
        )

    def log_action_rejected(
        self,
        *,
        operator_id: str,
        customer_id: str,
        confirmation_token: str,
        category: str,
        priority: str,
        reason: str = "Operator declined approval",
    ) -> dict[str, Any]:
        """Record blocked ticket creation attempt due to operator rejection."""
        return self.log_event(
            "ticket_action_rejected",
            operator_id=operator_id,
            customer_id=customer_id,
            confirmation_token=confirmation_token,
            approved_by_human=False,
            category=category,
            priority=priority,
            details={"reason": reason},
        )

    def log_token_expired(
        self,
        *,
        operator_id: str,
        customer_id: str,
        confirmation_token: str,
        category: str | None = None,
    ) -> dict[str, Any]:
        """Record blocked ticket creation due to expired token."""
        return self.log_event(
            "ticket_token_expired",
            operator_id=operator_id,
            customer_id=customer_id,
            confirmation_token=confirmation_token,
            approved_by_human=None,
            category=category,
            details={"reason": "Token TTL expired"},
        )

    def get_events(self) -> list[dict[str, Any]]:
        """Return all recorded audit events."""
        return list(self._events)

    def clear(self) -> None:
        """Clear recorded in-memory events (useful for tests)."""
        self._events.clear()
