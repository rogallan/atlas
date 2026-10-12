"""Tool implementations for ATLAS MCP Ticket Server (S13)."""

import logging
from datetime import UTC, datetime

from mcp.ticket.audit import TicketAuditLogger
from mcp.ticket.models import (
    ActionRejectedError,
    InvalidTicketParameterError,
    InvalidTokenError,
    TicketCategory,
    TicketDraft,
    TicketNotFoundError,
    TicketPriority,
    TicketRecord,
    TicketStatus,
    TokenExpiredError,
)
from mcp.ticket.store import TicketStore

logger = logging.getLogger("atlas.mcp.ticket.tools")


class TicketTools:
    """Business logic for two-phase Human-in-the-Loop ticket creation and queries."""

    def __init__(
        self,
        store: TicketStore | None = None,
        audit: TicketAuditLogger | None = None,
    ) -> None:
        self.store = store or TicketStore()
        self.audit = audit or TicketAuditLogger()

    def prepare_ticket(
        self,
        customer_id: str,
        category: TicketCategory | str,
        title: str,
        description: str,
        priority: TicketPriority | str = TicketPriority.MEDIUM,
        operator_id: str = "manager_001",
        idempotency_key: str | None = None,
    ) -> TicketDraft:
        """Phase 1: Validates ticket payload and emits a signed, time-limited confirmation token."""
        if not customer_id or not customer_id.strip():
            raise InvalidTicketParameterError("customer_id cannot be empty.")
        if not title or len(title.strip()) < 3:
            raise InvalidTicketParameterError("title must be at least 3 characters.")
        if not description or len(description.strip()) < 5:
            raise InvalidTicketParameterError("description must be at least 5 characters.")

        try:
            cat_enum = TicketCategory(category) if isinstance(category, str) else category
        except ValueError as err:
            valid_cats = [c.value for c in TicketCategory]
            raise InvalidTicketParameterError(
                f"Invalid category '{category}'. Valid options: {valid_cats}"
            ) from err

        try:
            prio_enum = TicketPriority(priority) if isinstance(priority, str) else priority
        except ValueError as err:
            valid_prios = [p.value for p in TicketPriority]
            raise InvalidTicketParameterError(
                f"Invalid priority '{priority}'. Valid options: {valid_prios}"
            ) from err

        draft = self.store.create_draft(
            customer_id=customer_id.strip(),
            category=cat_enum,
            title=title.strip(),
            description=description.strip(),
            priority=prio_enum,
            idempotency_key=idempotency_key,
        )

        self.audit.log_draft_prepared(
            operator_id=operator_id,
            customer_id=draft.customer_id,
            confirmation_token=draft.confirmation_token,
            category=draft.category.value,
            priority=draft.priority.value,
            expires_at=draft.expires_at.isoformat(),
            idempotency_key=idempotency_key,
        )

        return draft

    def confirm_and_create_ticket(
        self,
        confirmation_token: str,
        approved_by_user: bool,
        idempotency_key: str | None = None,
        operator_id: str = "manager_001",
    ) -> TicketRecord:
        """Phase 2: Executes ticket creation only when explicit human approval is granted."""
        token = confirmation_token.strip() if confirmation_token else ""
        if not token:
            raise InvalidTokenError("")

        if self.store.is_token_consumed(token):
            raise InvalidTokenError(token)

        draft = self.store.get_draft(token)
        if draft is None:
            raise InvalidTokenError(token)

        # Check token expiration
        now = datetime.now(UTC)
        if draft.expires_at <= now:
            self.store.consume_draft(token)
            self.audit.log_token_expired(
                operator_id=operator_id,
                customer_id=draft.customer_id,
                confirmation_token=token,
                category=draft.category.value,
            )
            raise TokenExpiredError(token, expired_at=draft.expires_at.isoformat())

        # Guardrail: Rejection by human operator
        if not approved_by_user:
            self.store.reject_draft(token)
            self.audit.log_action_rejected(
                operator_id=operator_id,
                customer_id=draft.customer_id,
                confirmation_token=token,
                category=draft.category.value,
                priority=draft.priority.value,
                reason="Operator declined approval explicitly",
            )
            raise ActionRejectedError(token, operator_id=operator_id)

        # Check idempotency
        effective_key = idempotency_key or draft.idempotency_key
        if effective_key:
            existing = self.store.get_ticket_by_idempotency_key(effective_key)
            if existing is not None:
                self.store.consume_draft(token)
                logger.info(
                    "Idempotent ticket hit for key '%s': returning ticket %s",
                    effective_key,
                    existing.ticket_id,
                )
                return existing

        # Commit ticket
        ticket_id = self.store.generate_ticket_id()
        ticket = TicketRecord(
            ticket_id=ticket_id,
            customer_id=draft.customer_id,
            category=draft.category,
            title=draft.title,
            description=draft.description,
            priority=draft.priority,
            status=TicketStatus.OPEN,
            created_at=now,
            approved_by_user=True,
            operator_id=operator_id,
            idempotency_key=effective_key,
            resolution_notes=None,
        )

        self.store.save_ticket(ticket)
        self.store.consume_draft(token)

        self.audit.log_action_executed(
            operator_id=operator_id,
            customer_id=ticket.customer_id,
            ticket_id=ticket.ticket_id,
            confirmation_token=token,
            category=ticket.category.value,
            priority=ticket.priority.value,
            idempotency_key=effective_key,
        )

        return ticket

    def get_ticket(self, ticket_id: str) -> TicketRecord:
        """Retrieve ticket details by ID."""
        cleaned_id = ticket_id.strip() if ticket_id else ""
        ticket = self.store.get_ticket(cleaned_id)
        if ticket is None:
            raise TicketNotFoundError(cleaned_id)
        return ticket

    def list_customer_tickets(self, customer_id: str) -> list[TicketRecord]:
        """List all historical and active tickets for a customer."""
        cleaned_id = customer_id.strip() if customer_id else ""
        if not cleaned_id:
            raise InvalidTicketParameterError("customer_id cannot be empty.")
        return self.store.list_customer_tickets(cleaned_id)
