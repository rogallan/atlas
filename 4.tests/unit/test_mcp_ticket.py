"""Unit, guardrail, idempotency, and HTTP tests for MCP Ticket Server (S13)."""

import json
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from mcp.ticket.audit import TicketAuditLogger
from mcp.ticket.http_server import app
from mcp.ticket.models import (
    ActionRejectedError,
    InvalidTicketParameterError,
    InvalidTokenError,
    TicketCategory,
    TicketNotFoundError,
    TicketPriority,
    TicketStatus,
    TokenExpiredError,
)
from mcp.ticket.server import TicketMCPServer, create_ticket_server
from mcp.ticket.store import TicketStore
from mcp.ticket.tools import TicketTools


@pytest.fixture
def ticket_store() -> TicketStore:
    return TicketStore(default_ttl_seconds=600)


@pytest.fixture
def audit_logger() -> TicketAuditLogger:
    return TicketAuditLogger()


@pytest.fixture
def ticket_tools(ticket_store: TicketStore, audit_logger: TicketAuditLogger) -> TicketTools:
    return TicketTools(store=ticket_store, audit=audit_logger)


@pytest.fixture
def ticket_server(ticket_tools: TicketTools) -> TicketMCPServer:
    return create_ticket_server(tools=ticket_tools)


@pytest.fixture
def http_client() -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------------------
# 1. Happy Path Workflow Tests
# ---------------------------------------------------------------------------


def test_prepare_ticket_draft_creation(ticket_tools: TicketTools) -> None:
    draft = ticket_tools.prepare_ticket(
        customer_id="CUST-001",
        category=TicketCategory.CARD_MAINTENANCE,
        title="Desbloqueio de Cartão",
        description="Solicitação para desbloqueio do novo cartão de crédito físico entregue.",
        priority=TicketPriority.MEDIUM,
    )

    assert draft.confirmation_token.startswith("tkn_")
    assert draft.customer_id == "CUST-001"
    assert draft.category == TicketCategory.CARD_MAINTENANCE
    assert draft.status == TicketStatus.PENDING_APPROVAL
    assert draft.expires_at > datetime.now(UTC)
    assert "Desbloqueio de Cartão" in draft.summary_for_human


def test_confirm_ticket_happy_path(ticket_tools: TicketTools) -> None:
    draft = ticket_tools.prepare_ticket(
        customer_id="CUST-001",
        category=TicketCategory.CONTESTATION,
        title="Cobrança Indevida",
        description="Cliente contesta tarifa avulsa cobrada erroneamente.",
        priority=TicketPriority.HIGH,
    )

    ticket = ticket_tools.confirm_and_create_ticket(
        confirmation_token=draft.confirmation_token,
        approved_by_user=True,
        operator_id="manager_001",
    )

    assert ticket.ticket_id.startswith("TCK-")
    assert ticket.customer_id == "CUST-001"
    assert ticket.status == TicketStatus.OPEN
    assert ticket.approved_by_user is True
    assert ticket.operator_id == "manager_001"
    assert ticket.title == "Cobrança Indevida"


# ---------------------------------------------------------------------------
# 2. Security Guardrails & Rejection Tests
# ---------------------------------------------------------------------------


def test_confirm_ticket_rejected_by_user_guardrail(
    ticket_tools: TicketTools,
    ticket_store: TicketStore,
    audit_logger: TicketAuditLogger,
) -> None:
    initial_ticket_count = len(ticket_store._tickets)

    draft = ticket_tools.prepare_ticket(
        customer_id="CUST-001",
        category=TicketCategory.LIMIT_INCREASE,
        title="Aumento R$ 10.000",
        description="Solicitação de aumento de limite sem comprovação de renda.",
        priority=TicketPriority.URGENT,
    )

    with pytest.raises(ActionRejectedError) as exc_info:
        ticket_tools.confirm_and_create_ticket(
            confirmation_token=draft.confirmation_token,
            approved_by_user=False,
            operator_id="manager_002",
        )

    assert "explicitly rejected" in exc_info.value.message
    # Assert store state was NOT mutated
    assert len(ticket_store._tickets) == initial_ticket_count
    # Token was consumed/invalidated
    assert ticket_store.is_token_consumed(draft.confirmation_token)

    # Check audit trail
    events = audit_logger.get_events()
    rejected_events = [e for e in events if e["event"] == "ticket_action_rejected"]
    assert len(rejected_events) == 1
    assert rejected_events[0]["approved_by_human"] is False
    assert rejected_events[0]["operator_id"] == "manager_002"


def test_token_expiration_guardrail(
    ticket_tools: TicketTools,
    ticket_store: TicketStore,
    audit_logger: TicketAuditLogger,
) -> None:
    draft = ticket_tools.prepare_ticket(
        customer_id="CUST-003",
        category=TicketCategory.GENERAL_INQUIRY,
        title="Dúvida de Investimentos",
        description="Esclarecimento sobre prazo de resgate de CDB pós-fixado.",
    )

    # Artificially expire token by moving expires_at to past
    ticket_store._drafts[draft.confirmation_token].expires_at = datetime.now(
        UTC
    ) - timedelta(minutes=1)

    with pytest.raises(TokenExpiredError) as exc_info:
        ticket_tools.confirm_and_create_ticket(
            confirmation_token=draft.confirmation_token,
            approved_by_user=True,
        )

    assert "expired" in exc_info.value.message.lower()

    # Verify audit event
    events = audit_logger.get_events()
    expired_events = [e for e in events if e["event"] == "ticket_token_expired"]
    assert len(expired_events) == 1
    assert expired_events[0]["customer_id"] == "CUST-003"


def test_replay_token_prevented(ticket_tools: TicketTools) -> None:
    draft = ticket_tools.prepare_ticket(
        customer_id="CUST-001",
        category=TicketCategory.TARIFF_REVIEW,
        title="Revisão de Pacote",
        description="Cliente solicita migração para pacote essencial gratuito.",
    )

    # First consumption succeeds
    ticket_tools.confirm_and_create_ticket(
        confirmation_token=draft.confirmation_token,
        approved_by_user=True,
    )

    # Replay attempt must fail with InvalidTokenError
    with pytest.raises(InvalidTokenError):
        ticket_tools.confirm_and_create_ticket(
            confirmation_token=draft.confirmation_token,
            approved_by_user=True,
        )


# ---------------------------------------------------------------------------
# 3. Idempotency Protection Tests
# ---------------------------------------------------------------------------


def test_idempotency_key_prevents_duplicate_tickets(
    ticket_tools: TicketTools,
    ticket_store: TicketStore,
) -> None:
    idempotency_key = "idemp-trans-uuid-999"

    # Step 1: create draft with key
    draft1 = ticket_tools.prepare_ticket(
        customer_id="CUST-002",
        category=TicketCategory.CONTESTATION,
        title="Estorno de Tarifa",
        description="Solicitação de devolução de tarifa de TED duplicada.",
        idempotency_key=idempotency_key,
    )
    ticket1 = ticket_tools.confirm_and_create_ticket(
        confirmation_token=draft1.confirmation_token,
        approved_by_user=True,
        idempotency_key=idempotency_key,
    )

    # Step 2: create new draft, confirm with the SAME idempotency key
    draft2 = ticket_tools.prepare_ticket(
        customer_id="CUST-002",
        category=TicketCategory.CONTESTATION,
        title="Estorno de Tarifa",
        description="Solicitação de devolução de tarifa de TED duplicada.",
        idempotency_key=idempotency_key,
    )
    ticket2 = ticket_tools.confirm_and_create_ticket(
        confirmation_token=draft2.confirmation_token,
        approved_by_user=True,
        idempotency_key=idempotency_key,
    )

    assert ticket1.ticket_id == ticket2.ticket_id
    assert ticket2.idempotency_key == idempotency_key


# ---------------------------------------------------------------------------
# 4. Validation and Query Tests
# ---------------------------------------------------------------------------


def test_prepare_ticket_input_validation(ticket_tools: TicketTools) -> None:
    with pytest.raises(InvalidTicketParameterError):
        ticket_tools.prepare_ticket(
            customer_id="",
            category=TicketCategory.CONTESTATION,
            title="Ok Title",
            description="Valid description here",
        )

    with pytest.raises(InvalidTicketParameterError):
        ticket_tools.prepare_ticket(
            customer_id="CUST-001",
            category="invalid_category",
            title="Ok Title",
            description="Valid description here",
        )

    with pytest.raises(InvalidTicketParameterError):
        ticket_tools.prepare_ticket(
            customer_id="CUST-001",
            category=TicketCategory.CARD_MAINTENANCE,
            title="Ab",  # too short
            description="Valid description here",
        )


def test_get_ticket_and_list_customer_tickets(ticket_tools: TicketTools) -> None:
    # CUST-001 has 1 seeded ticket TCK-2026-00010
    seed_ticket = ticket_tools.get_ticket("TCK-2026-00010")
    assert seed_ticket.customer_id == "CUST-001"
    assert seed_ticket.status == TicketStatus.CLOSED

    with pytest.raises(TicketNotFoundError):
        ticket_tools.get_ticket("TCK-9999-99999")

    # List customer tickets
    tickets_cust1 = ticket_tools.list_customer_tickets("CUST-001")
    assert len(tickets_cust1) >= 1
    assert all(t.customer_id == "CUST-001" for t in tickets_cust1)


# ---------------------------------------------------------------------------
# 5. Audit Trail Verification
# ---------------------------------------------------------------------------


def test_audit_trail_captures_complete_lifecycle(
    ticket_tools: TicketTools,
    audit_logger: TicketAuditLogger,
) -> None:
    draft = ticket_tools.prepare_ticket(
        customer_id="CUST-004",
        category=TicketCategory.CARD_MAINTENANCE,
        title="2ª Via de Cartão",
        description="Cliente solicita emissão de segunda via do cartão de crédito.",
    )
    ticket_tools.confirm_and_create_ticket(
        confirmation_token=draft.confirmation_token,
        approved_by_user=True,
        operator_id="manager_999",
    )

    events = audit_logger.get_events()
    event_names = [e["event"] for e in events]
    assert "ticket_draft_prepared" in event_names
    assert "ticket_action_executed" in event_names

    executed_ev = next(e for e in events if e["event"] == "ticket_action_executed")
    assert executed_ev["operator_id"] == "manager_999"
    assert executed_ev["customer_id"] == "CUST-004"
    assert executed_ev["approved_by_human"] is True
    assert executed_ev["ticket_id"].startswith("TCK-")


# ---------------------------------------------------------------------------
# 6. JSON-RPC 2.0 Server Tests
# ---------------------------------------------------------------------------


def test_mcp_server_initialize_and_tools_list(ticket_server: TicketMCPServer) -> None:
    init_res = ticket_server.handle_request(
        {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
    )
    assert init_res["result"]["serverInfo"]["name"] == "atlas-mcp-ticket"
    assert init_res["result"]["protocolVersion"] == "2024-11-05"

    list_res = ticket_server.handle_request(
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    )
    tool_names = [t["name"] for t in list_res["result"]["tools"]]
    assert "prepare_ticket" in tool_names
    assert "confirm_and_create_ticket" in tool_names
    assert "get_ticket" in tool_names
    assert "list_customer_tickets" in tool_names


def test_mcp_server_tools_call_flow(ticket_server: TicketMCPServer) -> None:
    # 1. prepare
    prep_res = ticket_server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "name": "prepare_ticket",
                "arguments": {
                    "customer_id": "CUST-001",
                    "category": "contestation",
                    "title": "Compra Desconhecida",
                    "description": "Cliente contesta compra de R$ 500 no cartão.",
                },
            },
        }
    )
    assert "result" in prep_res
    text_content = prep_res["result"]["content"][0]["text"]
    draft_data = json.loads(text_content)
    token = draft_data["confirmation_token"]
    assert token.startswith("tkn_")

    # 2. confirm
    conf_res = ticket_server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {
                "name": "confirm_and_create_ticket",
                "arguments": {
                    "confirmation_token": token,
                    "approved_by_user": True,
                },
            },
        }
    )
    assert "result" in conf_res
    conf_data = json.loads(conf_res["result"]["content"][0]["text"])
    assert conf_data["status"] == "open"
    assert conf_data["ticket_id"].startswith("TCK-")


# ---------------------------------------------------------------------------
# 7. HTTP & SSE Transport Tests
# ---------------------------------------------------------------------------


def test_http_health_and_tools_endpoints(http_client: TestClient) -> None:
    resp = http_client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "atlas-mcp-ticket"

    tools_resp = http_client.get("/tools")
    assert tools_resp.status_code == 200
    tools = tools_resp.json()["tools"]
    assert len(tools) == 4


def test_http_rest_tool_call(http_client: TestClient) -> None:
    # Phase 1 via REST
    prep_resp = http_client.post(
        "/tools/prepare_ticket",
        json={
            "customer_id": "CUST-002",
            "category": "limit_increase",
            "title": "Aumento de limite CUST-002",
            "description": "Aumento temporário solicitado pelo cliente.",
        },
    )
    assert prep_resp.status_code == 200
    token = prep_resp.json()["result"]["confirmation_token"]

    # Phase 2 via REST
    conf_resp = http_client.post(
        "/tools/confirm_and_create_ticket",
        json={
            "confirmation_token": token,
            "approved_by_user": True,
        },
    )
    assert conf_resp.status_code == 200
    assert conf_resp.json()["result"]["status"] == "open"


def test_http_jsonrpc_and_sse_endpoints(http_client: TestClient) -> None:
    # JSON-RPC endpoint
    rpc_resp = http_client.post(
        "/mcp/jsonrpc",
        json={"jsonrpc": "2.0", "id": 99, "method": "initialize"},
    )
    assert rpc_resp.status_code == 200
    assert rpc_resp.json()["result"]["serverInfo"]["name"] == "atlas-mcp-ticket"

    # SSE endpoint
    sse_resp = http_client.get("/sse")
    assert sse_resp.status_code == 200
    assert "text/event-stream" in sse_resp.headers["content-type"]
    assert "endpoint" in sse_resp.text
