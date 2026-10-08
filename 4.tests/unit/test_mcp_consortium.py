"""Unit, contract, and accounting tests for MCP Consortium Server (S11)."""

import json

import pytest
from fastapi.testclient import TestClient

from mcp.consortium.calculator import calculate_consortium_quota
from mcp.consortium.catalog import (
    get_all_modalities,
    get_group_rules,
    validate_consortium_request,
)
from mcp.consortium.http_server import app
from mcp.consortium.models import (
    DEFAULT_CONSORTIUM_DISCLAIMER,
    ConsortiumSegment,
    ConsortiumSimulationResult,
    InvalidConsortiumParameterError,
    ModalityNotFoundError,
)
from mcp.consortium.server import ConsortiumMCPServer, create_consortium_server
from mcp.consortium.tools import ConsortiumTools


@pytest.fixture
def consortium_tools() -> ConsortiumTools:
    return ConsortiumTools()


@pytest.fixture
def consortium_server() -> ConsortiumMCPServer:
    return create_consortium_server()


@pytest.fixture
def http_client() -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------------------
# 1. Catalog & Validation Tests
# ---------------------------------------------------------------------------


def test_consortium_catalog_segments() -> None:
    modalities = get_all_modalities()
    assert len(modalities) == 3
    segments = {m.segment for m in modalities}
    assert ConsortiumSegment.REAL_ESTATE in segments
    assert ConsortiumSegment.AUTOMOTIVE in segments
    assert ConsortiumSegment.SERVICES in segments


def test_get_group_rules_valid() -> None:
    rules = get_group_rules(ConsortiumSegment.AUTOMOTIVE)
    assert rules.display_name == "Consórcio de Veículos"
    assert rules.min_credit == 30000.0
    assert rules.max_credit == 250000.0
    assert 60 in rules.allowed_terms_months
    assert rules.total_admin_fee_pct == 0.14


def test_get_group_rules_not_found() -> None:
    with pytest.raises(ModalityNotFoundError):
        get_group_rules("invalid_modality_type")


def test_validate_consortium_request_boundaries() -> None:
    # Valid
    rules = validate_consortium_request(ConsortiumSegment.AUTOMOTIVE, 80000.0, 60, 0.10)
    assert rules.segment == ConsortiumSegment.AUTOMOTIVE

    # Credit below min
    with pytest.raises(InvalidConsortiumParameterError) as exc_min:
        validate_consortium_request(ConsortiumSegment.AUTOMOTIVE, 10000.0, 60)
    assert "inferior ao mínimo" in str(exc_min.value)

    # Credit above max
    with pytest.raises(InvalidConsortiumParameterError) as exc_max:
        validate_consortium_request(ConsortiumSegment.AUTOMOTIVE, 300000.0, 60)
    assert "excede o limite máximo" in str(exc_max.value)

    # Invalid term
    with pytest.raises(InvalidConsortiumParameterError) as exc_term:
        validate_consortium_request(ConsortiumSegment.AUTOMOTIVE, 80000.0, 50)
    assert "não permitido" in str(exc_term.value)

    # Bid exceeding limit
    with pytest.raises(InvalidConsortiumParameterError) as exc_bid:
        validate_consortium_request(ConsortiumSegment.AUTOMOTIVE, 80000.0, 60, 0.50)
    assert "excede o limite máximo" in str(exc_bid.value)


# ---------------------------------------------------------------------------
# 2. Accounting Math & Bid Simulation Tests
# ---------------------------------------------------------------------------


def test_calculate_consortium_quota_automotive() -> None:
    rules = get_group_rules(ConsortiumSegment.AUTOMOTIVE)
    calc = calculate_consortium_quota(
        credit_amount=80000.0,
        term_months=60,
        rules=rules,
        embedded_bid_pct=0.0,
    )

    inst = calc["installments"]
    assert inst.common_fund_amount == 1333.33
    assert inst.admin_fee_amount == 186.67
    assert inst.reserve_fund_amount == 26.67
    assert inst.monthly_total == 1546.67
    assert calc["total_cost_percentage"] == 16.0
    assert calc["simulated_bid_amount"] is None


def test_calculate_consortium_quota_with_bid() -> None:
    rules = get_group_rules(ConsortiumSegment.REAL_ESTATE)
    calc = calculate_consortium_quota(
        credit_amount=300000.0,
        term_months=180,
        rules=rules,
        embedded_bid_pct=0.20,
    )

    assert calc["simulated_bid_amount"] == 60000.0
    assert calc["net_credit_with_embedded_bid"] == 240000.0
    assert calc["post_bid_installment_estimate"] is not None
    assert calc["post_bid_installment_estimate"] < calc["installments"].monthly_total


# ---------------------------------------------------------------------------
# 3. Tool Handler Tests
# ---------------------------------------------------------------------------


def test_tools_list_consortium_modalities(consortium_tools: ConsortiumTools) -> None:
    modalities = consortium_tools.list_consortium_modalities()
    assert len(modalities) == 3


def test_tools_get_consortium_group_rules(consortium_tools: ConsortiumTools) -> None:
    rules = consortium_tools.get_consortium_group_rules(ConsortiumSegment.SERVICES)
    assert rules.display_name == "Consórcio de Serviços & Reformas"
    assert rules.min_credit == 10000.0


def test_tools_simulate_consortium(consortium_tools: ConsortiumTools) -> None:
    result = consortium_tools.simulate_consortium(
        modality=ConsortiumSegment.AUTOMOTIVE,
        credit_amount=90000.0,
        term_months=60,
        embedded_bid_pct=0.15,
    )

    assert isinstance(result, ConsortiumSimulationResult)
    assert result.credit_amount == 90000.0
    assert result.term_months == 60
    assert result.installments.monthly_total > 0
    assert result.simulated_bid_amount == 13500.0
    assert result.net_credit_with_embedded_bid == 76500.0
    assert result.disclaimer == DEFAULT_CONSORTIUM_DISCLAIMER


# ---------------------------------------------------------------------------
# 4. JSON-RPC Server Protocol Tests
# ---------------------------------------------------------------------------


def test_server_initialize(consortium_server: ConsortiumMCPServer) -> None:
    resp = consortium_server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert resp["id"] == 1
    assert resp["result"]["serverInfo"]["name"] == "atlas-mcp-consortium"


def test_server_ping(consortium_server: ConsortiumMCPServer) -> None:
    resp = consortium_server.handle_request({"jsonrpc": "2.0", "id": 2, "method": "ping"})
    assert resp["result"] == {}


def test_server_tools_list(consortium_server: ConsortiumMCPServer) -> None:
    resp = consortium_server.handle_request({"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
    tools = resp["result"]["tools"]
    names = {t["name"] for t in tools}
    assert "list_consortium_modalities" in names
    assert "get_consortium_group_rules" in names
    assert "simulate_consortium" in names


def test_server_tools_call_simulate(consortium_server: ConsortiumMCPServer) -> None:
    resp = consortium_server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "simulate_consortium",
                "arguments": {
                    "modality": "services",
                    "credit_amount": 30000.0,
                    "term_months": 36,
                    "embedded_bid_pct": 0.10,
                },
            },
        }
    )
    assert "error" not in resp
    content = resp["result"]["content"][0]["text"]
    data = json.loads(content)
    assert data["segment"] == "services"
    assert data["credit_amount"] == 30000.0
    assert data["disclaimer"] == DEFAULT_CONSORTIUM_DISCLAIMER


def test_server_tools_call_unknown(consortium_server: ConsortiumMCPServer) -> None:
    resp = consortium_server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "unknown_tool", "arguments": {}},
        }
    )
    assert "error" in resp
    assert resp["error"]["code"] == -32601


# ---------------------------------------------------------------------------
# 5. HTTP & SSE Server Tests
# ---------------------------------------------------------------------------


def test_http_health(http_client: TestClient) -> None:
    resp = http_client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "atlas-mcp-consortium"


def test_http_tools_list(http_client: TestClient) -> None:
    resp = http_client.get("/tools")
    assert resp.status_code == 200
    assert len(resp.json()["tools"]) == 3


def test_http_tool_rest_simulation(http_client: TestClient) -> None:
    resp = http_client.post(
        "/tools/simulate_consortium",
        json={"modality": "automotive", "credit_amount": 70000.0, "term_months": 48},
    )
    assert resp.status_code == 200
    data = resp.json()["result"]
    assert data["segment"] == "automotive"
    assert data["installments"]["monthly_total"] > 0
    assert data["disclaimer"] == DEFAULT_CONSORTIUM_DISCLAIMER


def test_http_tool_rest_error(http_client: TestClient) -> None:
    resp = http_client.post(
        "/tools/simulate_consortium",
        json={"modality": "automotive", "credit_amount": 5000.0, "term_months": 48},
    )
    assert resp.status_code == 400
    assert "inferior ao mínimo" in resp.json()["detail"]["message"]
