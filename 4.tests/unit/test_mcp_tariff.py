"""Unit, contract, consistency, and HTTP tests for MCP Tariff Server (S12)."""

import json

import pytest
from fastapi.testclient import TestClient

from mcp.tariff.catalog import get_package_info, get_tariff_item, list_packages
from mcp.tariff.http_server import app
from mcp.tariff.models import (
    ChannelType,
    InvalidTariffParameterError,
    QuotaCheckResult,
    ServiceNotFoundError,
)
from mcp.tariff.server import TariffMCPServer, create_tariff_server
from mcp.tariff.sync import verify_tariff_rag_consistency
from mcp.tariff.tools import TariffTools


@pytest.fixture
def tariff_tools() -> TariffTools:
    return TariffTools()


@pytest.fixture
def tariff_server() -> TariffMCPServer:
    return create_tariff_server()


@pytest.fixture
def http_client() -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------------------
# 1. Catalog & Channel Differentiation Tests
# ---------------------------------------------------------------------------


def test_tariff_catalog_channel_differentiation() -> None:
    atm_item = get_tariff_item("withdrawal", ChannelType.ATM)
    counter_item = get_tariff_item("withdrawal", ChannelType.BRANCH_COUNTER)

    assert atm_item.unit_price == 2.90
    assert counter_item.unit_price == 3.80
    assert counter_item.unit_price > atm_item.unit_price
    assert atm_item.is_essential_service is True
    assert atm_item.monthly_free_quota == 4


def test_tariff_catalog_pix_zero_fee() -> None:
    pix_digital = get_tariff_item("pix_transfer", ChannelType.DIGITAL)
    assert pix_digital.unit_price == 0.00
    assert pix_digital.is_essential_service is True
    assert "Resolução BCB" in pix_digital.regulatory_basis


def test_tariff_catalog_service_not_found() -> None:
    with pytest.raises(ServiceNotFoundError):
        get_tariff_item("non_existent_service", ChannelType.ATM)


# ---------------------------------------------------------------------------
# 2. Essential Services Quota Tests (BACEN Res. 3.919)
# ---------------------------------------------------------------------------


def test_check_essential_quota_within_limit(tariff_tools: TariffTools) -> None:
    # 3 withdrawals done, 4th is still free
    result = tariff_tools.check_essential_services_quota(
        service_code="withdrawal",
        used_count=3,
        channel=ChannelType.ATM,
    )
    assert isinstance(result, QuotaCheckResult)
    assert result.is_within_free_quota is True
    assert result.chargeable_units == 0
    assert result.total_charge == 0.0


def test_check_essential_quota_exceeded(tariff_tools: TariffTools) -> None:
    # 4 withdrawals done, 5th is chargeable
    result = tariff_tools.check_essential_services_quota(
        service_code="withdrawal",
        used_count=4,
        channel=ChannelType.ATM,
    )
    assert result.is_within_free_quota is False
    assert result.chargeable_units == 1
    assert result.total_charge == 2.90
    assert result.unit_fee == 2.90


def test_check_essential_quota_statements(tariff_tools: TariffTools) -> None:
    # 1 statement done, 2nd is free
    res_free = tariff_tools.check_essential_services_quota(
        service_code="statement_30d",
        used_count=1,
        channel=ChannelType.ATM,
    )
    assert res_free.is_within_free_quota is True

    # 2 statements done, 3rd is chargeable at R$ 2.20
    res_paid = tariff_tools.check_essential_services_quota(
        service_code="statement_30d",
        used_count=2,
        channel=ChannelType.ATM,
    )
    assert res_paid.is_within_free_quota is False
    assert res_paid.total_charge == 2.20


def test_check_essential_quota_invalid_count(tariff_tools: TariffTools) -> None:
    with pytest.raises(InvalidTariffParameterError):
        tariff_tools.check_essential_services_quota(
            service_code="withdrawal",
            used_count=-1,
            channel=ChannelType.ATM,
        )


# ---------------------------------------------------------------------------
# 3. Packages & Waivers Tests
# ---------------------------------------------------------------------------


def test_list_tariff_packages_includes_essential_free() -> None:
    packages = list_packages()
    assert len(packages) >= 4
    pkg_map = {p.package_id: p for p in packages}
    assert "essential_free" in pkg_map
    assert pkg_map["essential_free"].monthly_price == 0.00
    waiver = pkg_map["essential_free"].waiver_conditions
    assert waiver is not None and "Resolução CMN" in waiver


def test_compare_packages_filtering(tariff_tools: TariffTools) -> None:
    prime_pkgs = tariff_tools.compare_packages(customer_segment="prime")
    assert any(p.package_id == "package_prime" for p in prime_pkgs)
    # essential_free has target_segment="all", so it must be included
    assert any(p.package_id == "essential_free" for p in prime_pkgs)


def test_get_package_info_success() -> None:
    pkg = get_package_info("package_classic")
    assert pkg.name == "Pacote Clássico Padronizado I"
    assert pkg.monthly_price == 29.90


# ---------------------------------------------------------------------------
# 4. RAG Document Consistency Test
# ---------------------------------------------------------------------------


def test_tariff_rag_consistency_audit() -> None:
    audit = verify_tariff_rag_consistency()
    assert audit["is_consistent"] is True
    assert len(audit["mismatches"]) == 0
    assert len(audit["checked_rules"]) == 5


# ---------------------------------------------------------------------------
# 5. JSON-RPC Protocol Server Tests
# ---------------------------------------------------------------------------


def test_server_initialize(tariff_server: TariffMCPServer) -> None:
    resp = tariff_server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert resp["id"] == 1
    assert resp["result"]["serverInfo"]["name"] == "atlas-mcp-tariff"


def test_server_ping(tariff_server: TariffMCPServer) -> None:
    resp = tariff_server.handle_request({"jsonrpc": "2.0", "id": 2, "method": "ping"})
    assert resp["result"] == {}


def test_server_tools_list(tariff_server: TariffMCPServer) -> None:
    resp = tariff_server.handle_request({"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
    tools = resp["result"]["tools"]
    names = {t["name"] for t in tools}
    assert "get_service_fee" in names
    assert "list_tariff_packages" in names
    assert "check_essential_services_quota" in names
    assert "compare_packages" in names


def test_server_tools_call_get_fee(tariff_server: TariffMCPServer) -> None:
    resp = tariff_server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "get_service_fee",
                "arguments": {"service_code": "withdrawal", "channel": "atm"},
            },
        }
    )
    assert "error" not in resp
    content = resp["result"]["content"][0]["text"]
    data = json.loads(content)
    assert data["service_code"] == "withdrawal"
    assert data["unit_price"] == 2.90


def test_server_tools_call_check_quota(tariff_server: TariffMCPServer) -> None:
    resp = tariff_server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "check_essential_services_quota",
                "arguments": {"service_code": "withdrawal", "used_count": 2, "channel": "atm"},
            },
        }
    )
    assert "error" not in resp
    content = resp["result"]["content"][0]["text"]
    data = json.loads(content)
    assert data["is_within_free_quota"] is True
    assert data["total_charge"] == 0.0


def test_server_tools_call_unknown(tariff_server: TariffMCPServer) -> None:
    resp = tariff_server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {"name": "invalid_tariff_tool", "arguments": {}},
        }
    )
    assert "error" in resp
    assert resp["error"]["code"] == -32601


# ---------------------------------------------------------------------------
# 6. HTTP & SSE Server Tests
# ---------------------------------------------------------------------------


def test_http_health(http_client: TestClient) -> None:
    resp = http_client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "atlas-mcp-tariff"


def test_http_tools_list(http_client: TestClient) -> None:
    resp = http_client.get("/tools")
    assert resp.status_code == 200
    assert len(resp.json()["tools"]) == 4


def test_http_tool_rest_get_fee(http_client: TestClient) -> None:
    resp = http_client.post(
        "/tools/get_service_fee",
        json={"service_code": "ted_transfer", "channel": "branch_counter"},
    )
    assert resp.status_code == 200
    data = resp.json()["result"]
    assert data["service_code"] == "ted_transfer"
    assert data["unit_price"] == 19.50


def test_http_tool_rest_error(http_client: TestClient) -> None:
    resp = http_client.post(
        "/tools/get_service_fee",
        json={"service_code": "unknown_service_code"},
    )
    assert resp.status_code == 400
    assert "não encontrado" in resp.json()["detail"]["message"]
