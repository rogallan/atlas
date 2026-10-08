"""Unit and contract tests for MCP Customer Server (S08)."""

import contextlib
import json
from pathlib import Path

import pytest

from mcp.customer.auth import AuthContext, SecurityManager
from mcp.customer.models import (
    CustomerNotFoundError,
    CustomerProfileResponse,
    CustomerSummaryResponse,
    UnauthorizedError,
)
from mcp.customer.repository import CustomerRepository
from mcp.customer.server import CustomerMCPServer, create_customer_server
from mcp.customer.tools import CustomerTools


@pytest.fixture
def repository() -> CustomerRepository:
    """Fixture providing initialized CustomerRepository."""
    return CustomerRepository()


@pytest.fixture
def security_manager() -> SecurityManager:
    """Fixture providing clean SecurityManager instance."""
    return SecurityManager()


@pytest.fixture
def tools(repository: CustomerRepository, security_manager: SecurityManager) -> CustomerTools:
    """Fixture providing CustomerTools."""
    return CustomerTools(repository=repository, security_manager=security_manager)


@pytest.fixture
def server(repository: CustomerRepository, security_manager: SecurityManager) -> CustomerMCPServer:
    """Fixture providing CustomerMCPServer."""
    return CustomerMCPServer(repository=repository, security_manager=security_manager)


# ---------------------------------------------------------------------------
# 1. MCP Protocol & Contract Tests
# ---------------------------------------------------------------------------


def test_mcp_initialize(server: CustomerMCPServer) -> None:
    """JSON-RPC initialize returns protocol version and server capabilities."""
    req = {
        "jsonrpc": "2.0",
        "id": "req-1",
        "method": "initialize",
        "params": {"protocolVersion": "2024-11-05"},
    }
    resp = server.handle_jsonrpc(req)

    assert resp is not None
    assert resp["jsonrpc"] == "2.0"
    assert resp["id"] == "req-1"
    assert resp["result"]["protocolVersion"] == "2024-11-05"
    assert resp["result"]["serverInfo"]["name"] == "atlas-customer-mcp"
    assert "tools" in resp["result"]["capabilities"]


def test_mcp_ping(server: CustomerMCPServer) -> None:
    """JSON-RPC ping returns empty result."""
    req = {"jsonrpc": "2.0", "id": "req-2", "method": "ping"}
    resp = server.handle_jsonrpc(req)

    assert resp is not None
    assert resp["id"] == "req-2"
    assert resp["result"] == {}


def test_mcp_tools_list_contract(server: CustomerMCPServer) -> None:
    """tools/list advertises all 4 required customer tools with valid JSON Schemas."""
    req = {"jsonrpc": "2.0", "id": "req-3", "method": "tools/list"}
    resp = server.handle_jsonrpc(req)

    assert resp is not None
    tools = resp["result"]["tools"]
    tool_names = {t["name"] for t in tools}

    expected_tools = {
        "get_customer_profile",
        "get_customer_accounts",
        "get_financial_history",
        "get_customer_summary",
    }
    assert expected_tools.issubset(tool_names)

    for tool in tools:
        assert "description" in tool
        assert "inputSchema" in tool
        schema = tool["inputSchema"]
        assert schema.get("type") == "object"
        assert "customer_id" in schema.get("properties", {})


def test_mcp_unknown_method(server: CustomerMCPServer) -> None:
    """Invoking an unregistered method returns standard JSON-RPC -32601 error."""
    req = {"jsonrpc": "2.0", "id": "req-err", "method": "invalid/method"}
    resp = server.handle_jsonrpc(req)

    assert resp is not None
    assert "error" in resp
    assert resp["error"]["code"] == -32601


# ---------------------------------------------------------------------------
# 2. Tool Execution Tests (Synthetic Customer CUST-0001 - Dave Weckl)
# ---------------------------------------------------------------------------


def test_get_customer_profile(tools: CustomerTools) -> None:
    """get_customer_profile returns accurate synthetic profile for Dave Weckl."""
    profile = tools.get_customer_profile("CUST-0001")

    assert isinstance(profile, CustomerProfileResponse)
    assert profile.customer_id == "CUST-0001"
    assert profile.full_name == "Dave Weckl"
    assert "weckl" in profile.email.lower()
    assert profile.segment.value == "retail"
    assert profile.monthly_income > 0
    assert profile.relationship_years >= 1
    assert 0 <= profile.credit_score <= 1000
    assert profile.risk_rating in {"LOW", "MEDIUM", "HIGH"}


def test_get_customer_accounts(tools: CustomerTools) -> None:
    """get_customer_accounts returns checking and other active accounts."""
    accounts = tools.get_customer_accounts("CUST-0001")

    assert len(accounts) >= 1
    acc = accounts[0]
    assert acc.account_id == "ACC-0001"
    assert acc.account_type == "checking"
    assert acc.currency == "BRL"
    assert acc.balance > 0
    assert acc.status == "active"


def test_get_financial_history(tools: CustomerTools) -> None:
    """get_financial_history returns chronological financial transactions."""
    events = tools.get_financial_history("CUST-0001", limit=10)

    assert len(events) >= 1
    assert len(events) <= 10
    evt = events[0]
    assert evt.event_id.startswith("EVT-")
    assert evt.account_id == "ACC-0001"
    assert evt.amount > 0
    assert len(evt.description) > 0


def test_get_customer_summary(tools: CustomerTools) -> None:
    """get_customer_summary aggregates profile, accounts, total balance, and briefing note."""
    summary = tools.get_customer_summary("CUST-0001")

    assert isinstance(summary, CustomerSummaryResponse)
    assert summary.profile.customer_id == "CUST-0001"
    assert summary.profile.full_name == "Dave Weckl"
    assert len(summary.accounts) >= 1
    assert summary.total_balance > 0
    assert summary.active_contracts_count >= 0
    assert summary.relationship_notes is not None
    assert "Dave Weckl" in summary.relationship_notes


# ---------------------------------------------------------------------------
# 3. JSON-RPC Protocol tools/call Execution Tests
# ---------------------------------------------------------------------------


def test_mcp_tools_call_profile_success(server: CustomerMCPServer) -> None:
    """tools/call successfully executes get_customer_profile over JSON-RPC."""
    req = {
        "jsonrpc": "2.0",
        "id": "req-call-1",
        "method": "tools/call",
        "params": {
            "name": "get_customer_profile",
            "arguments": {"customer_id": "CUST-0001"},
        },
    }
    resp = server.handle_jsonrpc(req)

    assert resp is not None
    assert resp["id"] == "req-call-1"
    assert resp["result"]["isError"] is False
    content = resp["result"]["content"]
    assert len(content) == 1
    payload = json.loads(content[0]["text"])
    assert payload["customer_id"] == "CUST-0001"
    assert payload["full_name"] == "Dave Weckl"


def test_mcp_tools_call_summary_success(server: CustomerMCPServer) -> None:
    """tools/call successfully executes get_customer_summary over JSON-RPC."""
    req = {
        "jsonrpc": "2.0",
        "id": "req-call-2",
        "method": "tools/call",
        "params": {
            "name": "get_customer_summary",
            "arguments": {"customer_id": "CUST-0001"},
        },
    }
    resp = server.handle_jsonrpc(req)

    assert resp is not None
    assert resp["result"]["isError"] is False
    payload = json.loads(resp["result"]["content"][0]["text"])
    assert payload["profile"]["full_name"] == "Dave Weckl"
    assert "accounts" in payload
    assert payload["total_balance"] > 0


# ---------------------------------------------------------------------------
# 4. Error Handling & Validation Edge Cases
# ---------------------------------------------------------------------------


def test_customer_not_found_exception(tools: CustomerTools) -> None:
    """Non-existent customer_id raises CustomerNotFoundError."""
    with pytest.raises(CustomerNotFoundError) as exc_info:
        tools.get_customer_profile("CUST-9999")
    assert "CUST-9999" in str(exc_info.value)


def test_customer_not_found_jsonrpc(server: CustomerMCPServer) -> None:
    """Non-existent customer_id returns isError=True over JSON-RPC."""
    req = {
        "jsonrpc": "2.0",
        "id": "req-404",
        "method": "tools/call",
        "params": {
            "name": "get_customer_profile",
            "arguments": {"customer_id": "CUST-9999"},
        },
    }
    resp = server.handle_jsonrpc(req)

    assert resp is not None
    assert resp["result"]["isError"] is True
    assert "não encontrado" in resp["result"]["content"][0]["text"].lower()


def test_invalid_customer_id_pattern(server: CustomerMCPServer) -> None:
    """Malformed customer_id triggers validation error."""
    req = {
        "jsonrpc": "2.0",
        "id": "req-val",
        "method": "tools/call",
        "params": {
            "name": "get_customer_profile",
            "arguments": {"customer_id": "INVALID-ID"},
        },
    }
    resp = server.handle_jsonrpc(req)

    assert resp is not None
    assert resp["result"]["isError"] is True
    assert "validação" in resp["result"]["content"][0]["text"].lower()


def test_financial_history_limit_validation(tools: CustomerTools) -> None:
    """Invalid limits (< 1 or > 50) raise ValueError."""
    with pytest.raises(ValueError):
        tools.get_financial_history("CUST-0001", limit=0)

    with pytest.raises(ValueError):
        tools.get_financial_history("CUST-0001", limit=100)


def test_unknown_tool_execution(server: CustomerMCPServer) -> None:
    """Unknown tool name returns validation error."""
    req = {
        "jsonrpc": "2.0",
        "id": "req-unknown",
        "method": "tools/call",
        "params": {
            "name": "unknown_tool",
            "arguments": {"customer_id": "CUST-0001"},
        },
    }
    resp = server.handle_jsonrpc(req)

    assert resp is not None
    assert resp["result"]["isError"] is True


# ---------------------------------------------------------------------------
# 5. Simulated Authorization & Security Tests
# ---------------------------------------------------------------------------


def test_authorization_granted(tools: CustomerTools) -> None:
    """Allowed roles (manager, analyst, admin) succeed without error."""
    for role in ["relationship_manager", "manager", "analyst", "admin"]:
        ctx = AuthContext(operator_id="OP-01", role=role)
        profile = tools.get_customer_profile("CUST-0001", auth_context=ctx)
        assert profile.customer_id == "CUST-0001"


def test_authorization_denied(tools: CustomerTools) -> None:
    """Disallowed roles raise UnauthorizedError."""
    ctx = AuthContext(operator_id="OP-BAD", role="intern")
    with pytest.raises(UnauthorizedError) as exc_info:
        tools.get_customer_profile("CUST-0001", auth_context=ctx)
    assert "Acesso negado" in str(exc_info.value)


def test_authorization_denied_jsonrpc(server: CustomerMCPServer) -> None:
    """Unauthorized role returns isError=True over JSON-RPC."""
    bad_ctx = AuthContext(operator_id="OP-BAD", role="teller")
    req = {
        "jsonrpc": "2.0",
        "id": "req-auth-denied",
        "method": "tools/call",
        "params": {
            "name": "get_customer_profile",
            "arguments": {"customer_id": "CUST-0001"},
        },
    }
    resp = server.handle_jsonrpc(req, auth_context=bad_ctx)

    assert resp is not None
    assert resp["result"]["isError"] is True
    assert "Acesso negado" in resp["result"]["content"][0]["text"]


# ---------------------------------------------------------------------------
# 6. Audit Logging Verification Tests
# ---------------------------------------------------------------------------


def test_audit_logging_lifecycle(tools: CustomerTools, security_manager: SecurityManager) -> None:
    """SecurityManager records audit logs for success, denied, and not_found events."""
    # 1. Success event
    ctx = AuthContext(operator_id="MGR-100", role="relationship_manager")
    tools.get_customer_profile("CUST-0001", auth_context=ctx)

    # 2. Not found event
    with contextlib.suppress(CustomerNotFoundError):
        tools.get_customer_profile("CUST-9999", auth_context=ctx)

    # 3. Denied event
    bad_ctx = AuthContext(operator_id="MGR-999", role="visitor")
    with contextlib.suppress(UnauthorizedError):
        tools.get_customer_profile("CUST-0001", auth_context=bad_ctx)

    logs = security_manager.audit_log
    assert len(logs) >= 3

    statuses = [evt.status for evt in logs]
    assert "success" in statuses
    assert "not_found" in statuses
    assert "denied" in statuses

    # Verify event structure
    for evt in logs:
        assert evt.event == "customer_data_access"
        assert evt.timestamp is not None
        assert evt.correlation_id is not None
        assert evt.operator_id in {"MGR-100", "MGR-999"}
        assert evt.tool == "get_customer_profile"


def test_create_customer_server_helper() -> None:
    """create_customer_server helper instantiates a ready-to-run server."""
    srv = create_customer_server()
    assert isinstance(srv, CustomerMCPServer)
    assert len(srv.get_tool_definitions()) == 4


def test_server_execute_tool_all_endpoints(server: CustomerMCPServer) -> None:
    """Directly test execute_tool across all 4 customer tools."""
    # 1. Accounts
    accs = server.execute_tool("get_customer_accounts", {"customer_id": "CUST-0001"})
    assert len(accs) >= 1

    # 2. History
    evts = server.execute_tool("get_financial_history", {"customer_id": "CUST-0001", "limit": 5})
    assert len(evts) <= 5

    # 3. Summary
    summ = server.execute_tool("get_customer_summary", {"customer_id": "CUST-0001"})
    assert summ.profile.customer_id == "CUST-0001"

    # 4. Unknown tool
    with pytest.raises(ValueError):
        server.execute_tool("unknown_tool", {})


def test_mcp_notifications_initialized(server: CustomerMCPServer) -> None:
    """notifications/initialized notification returns None without response."""
    req = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    assert server.handle_jsonrpc(req) is None


def test_repository_list_and_fallback(tmp_path: Path) -> None:
    """CustomerRepository lists customer IDs and falls back to generator if fixture missing."""
    repo = CustomerRepository()
    ids = repo.list_customer_ids()
    assert len(ids) == 25
    assert "CUST-0001" in ids

    # Test fallback when path does not exist
    empty_file = tmp_path / "missing.json"
    fallback_repo = CustomerRepository(fixture_path=empty_file)
    fallback_ids = fallback_repo.list_customer_ids()
    assert len(fallback_ids) == 25


def test_compute_score_range_categories() -> None:
    """_compute_score_range handles each credit bracket properly."""
    from mcp.customer.tools import _compute_score_range

    assert "Baixo" in _compute_score_range(400)
    assert "Médio" in _compute_score_range(600)
    assert "Bom" in _compute_score_range(750)
    assert "Excelente" in _compute_score_range(900)


def test_mcp_http_server_endpoints() -> None:
    """Test MCP HTTP server endpoints (/health, /tools, REST invocation)."""
    from fastapi.testclient import TestClient

    from mcp.customer.http_server import app

    client = TestClient(app)

    # 1. Health
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    # 2. Tools
    res_tools = client.get("/tools")
    assert res_tools.status_code == 200
    assert len(res_tools.json()["tools"]) == 4

    # 3. Call tool via REST
    res_call = client.post(
        "/tools/get_customer_profile",
        json={"customer_id": "CUST-0001"},
    )
    assert res_call.status_code == 200
    assert res_call.json()["result"]["full_name"] == "Dave Weckl"

    # 4. JSON-RPC over HTTP
    rpc_req = {
        "jsonrpc": "2.0",
        "id": "http-1",
        "method": "tools/call",
        "params": {
            "name": "get_customer_profile",
            "arguments": {"customer_id": "CUST-0001"},
        },
    }
    res_rpc = client.post("/mcp/jsonrpc", json=rpc_req)
    assert res_rpc.status_code == 200
    assert res_rpc.json()["result"]["isError"] is False
