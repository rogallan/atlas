"""In-memory ticket repository with idempotency index and draft TTL tracking (S13)."""

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from mcp.ticket.models import (
    TicketCategory,
    TicketDraft,
    TicketPriority,
    TicketRecord,
    TicketStatus,
)


class TicketStore:
    """Repository managing drafts, committed tickets, and idempotency guarantees."""

    DEFAULT_TTL_SECONDS = 600  # 10 minutes

    def __init__(self, default_ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        self.default_ttl_seconds = default_ttl_seconds
        self._tickets: dict[str, TicketRecord] = {}
        self._drafts: dict[str, TicketDraft] = {}
        self._consumed_tokens: set[str] = set()
        self._idempotency_map: dict[str, str] = {}  # idempotency_key -> ticket_id
        self._ticket_sequence: int = 100
        self._seed_initial_data()

    def _seed_initial_data(self) -> None:
        """Seed initial synthetic customer service tickets for historical context."""
        seed_tickets: list[dict[str, Any]] = [
            {
                "ticket_id": "TCK-2026-00010",
                "customer_id": "CUST-001",
                "category": TicketCategory.CARD_MAINTENANCE,
                "title": "Desbloqueio de cartão virtual",
                "description": (
                    "Cliente solicitou reativação do cartão virtual após bloqueio temporário "
                    "por segurança."
                ),
                "priority": TicketPriority.LOW,
                "status": TicketStatus.CLOSED,
                "created_at": datetime(2026, 9, 15, 14, 30, tzinfo=UTC),
                "approved_by_user": True,
                "operator_id": "manager_001",
                "resolution_notes": "Cartão reativado via aplicativo com sucesso.",
            },
            {
                "ticket_id": "TCK-2026-00025",
                "customer_id": "CUST-002",
                "category": TicketCategory.LIMIT_INCREASE,
                "title": "Solicitação de aumento de limite emergencial",
                "description": (
                    "Cliente solicitou aumento temporário de R$ 5.000 para viagem ao exterior."
                ),
                "priority": TicketPriority.HIGH,
                "status": TicketStatus.IN_ANALYSIS,
                "created_at": datetime(2026, 10, 1, 9, 15, tzinfo=UTC),
                "approved_by_user": True,
                "operator_id": "manager_002",
                "resolution_notes": "Encaminhado para mesa de crédito.",
            },
        ]
        for item in seed_tickets:
            rec = TicketRecord(**item)
            self._tickets[rec.ticket_id] = rec

    def generate_ticket_id(self) -> str:
        """Generate sequential, standardized ticket identifier."""
        self._ticket_sequence += 1
        year = datetime.now(UTC).year
        return f"TCK-{year}-{self._ticket_sequence:05d}"

    def create_draft(
        self,
        *,
        customer_id: str,
        category: TicketCategory,
        title: str,
        description: str,
        priority: TicketPriority = TicketPriority.MEDIUM,
        idempotency_key: str | None = None,
        ttl_seconds: int | None = None,
    ) -> TicketDraft:
        """Stage a pending ticket draft and issue a time-limited confirmation token."""
        token = f"tkn_{secrets.token_urlsafe(24)}"
        now = datetime.now(UTC)
        effective_ttl = ttl_seconds or self.default_ttl_seconds
        expires_at = now + timedelta(seconds=effective_ttl)

        category_labels = {
            TicketCategory.CONTESTATION: "Contestação de Transação",
            TicketCategory.CARD_MAINTENANCE: "Manutenção de Cartão",
            TicketCategory.LIMIT_INCREASE: "Aumento de Limite",
            TicketCategory.TARIFF_REVIEW: "Revisão de Tarifas",
            TicketCategory.GENERAL_INQUIRY: "Dúvida / Atendimento Geral",
        }
        human_category = category_labels.get(category, str(category))

        summary = (
            f"Abertura de Chamado: [{human_category}] '{title}' para o cliente {customer_id}. "
            f"Prioridade: {priority.value.upper()}. Expira em {effective_ttl // 60} minutos. "
            "Requer autorização explícita do gerente."
        )

        draft = TicketDraft(
            confirmation_token=token,
            customer_id=customer_id,
            category=category,
            title=title,
            description=description,
            priority=priority,
            created_at=now,
            expires_at=expires_at,
            summary_for_human=summary,
            status=TicketStatus.PENDING_APPROVAL,
            idempotency_key=idempotency_key,
        )
        self._drafts[token] = draft
        return draft

    def get_draft(self, token: str) -> TicketDraft | None:
        """Retrieve pending draft by token."""
        return self._drafts.get(token)

    def is_token_consumed(self, token: str) -> bool:
        """Check if token was already used or consumed."""
        return token in self._consumed_tokens

    def consume_draft(self, token: str) -> None:
        """Mark draft token as consumed to prevent replay attacks."""
        self._consumed_tokens.add(token)
        if token in self._drafts:
            del self._drafts[token]

    def reject_draft(self, token: str) -> None:
        """Invalidate draft upon explicit human rejection."""
        self._consumed_tokens.add(token)
        if token in self._drafts:
            self._drafts[token].status = TicketStatus.REJECTED
            del self._drafts[token]

    def save_ticket(self, ticket: TicketRecord) -> None:
        """Persist ticket in store and record idempotency mapping if applicable."""
        self._tickets[ticket.ticket_id] = ticket
        if ticket.idempotency_key:
            self._idempotency_map[ticket.idempotency_key] = ticket.ticket_id

    def get_ticket(self, ticket_id: str) -> TicketRecord | None:
        """Find ticket by ID."""
        return self._tickets.get(ticket_id)

    def get_ticket_by_idempotency_key(self, idempotency_key: str) -> TicketRecord | None:
        """Retrieve existing ticket if idempotency key was previously processed."""
        ticket_id = self._idempotency_map.get(idempotency_key)
        if ticket_id:
            return self._tickets.get(ticket_id)
        return None

    def list_customer_tickets(self, customer_id: str) -> list[TicketRecord]:
        """List all tickets associated with a given customer ID."""
        matched = [ticket for ticket in self._tickets.values() if ticket.customer_id == customer_id]
        return sorted(matched, key=lambda t: t.created_at, reverse=True)

    def clean_expired_drafts(self) -> int:
        """Evict expired drafts from memory."""
        now = datetime.now(UTC)
        expired_tokens = [token for token, draft in self._drafts.items() if draft.expires_at <= now]
        for token in expired_tokens:
            del self._drafts[token]
        return len(expired_tokens)
