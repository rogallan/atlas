"""Unit, contract, and mathematical tests for MCP Insurance Server (S10)."""

import json
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from mcp.customer.repository import CustomerRepository
from mcp.insurance.calculator import calculate_customer_risk_factor, calculate_insurance_premium
from mcp.insurance.catalog import get_all_products, get_product_info, validate_insurance_request
from mcp.insurance.http_server import app
from mcp.insurance.models import (
    DEFAULT_INSURANCE_DISCLAIMER,
    CoverageNotFoundError,
    InsuranceCategory,
    InsuranceQuoteResult,
    InvalidInsuranceParameterError,
    ProductNotFoundError,
)
from mcp.insurance.server import InsuranceMCPServer, create_insurance_server
from mcp.insurance.tools import InsuranceTools


@pytest.fixture
def insurance_tools() -> InsuranceTools:
    return InsuranceTools(customer_repository=CustomerRepository())


@pytest.fixture
def insurance_server() -> InsuranceMCPServer:
    return create_insurance_server(customer_repository=CustomerRepository())


@pytest.fixture
def http_client() -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------------------
# 1. Catalog & Validation Tests
# ---------------------------------------------------------------------------


def test_catalog_all_products_valid() -> None:
    products = get_all_products()
    assert len(products) >= 4
    categories = {p.category for p in products}
    assert InsuranceCategory.LIFE in categories
    assert InsuranceCategory.HOME in categories
    assert InsuranceCategory.CREDIT_LIFE in categories
    assert InsuranceCategory.CARD_PROTECTION in categories


def test_get_product_info_success() -> None:
    product = get_product_info("life_individual")
    assert product.product_id == "life_individual"
    assert product.min_capital == 20000.0
    assert product.max_capital == 1500000.0
    assert len(product.available_coverages) > 0


def test_get_product_info_not_found() -> None:
    with pytest.raises(ProductNotFoundError):
        get_product_info("non_existent_insurance")


def test_validate_insurance_request_boundaries() -> None:
    # Valid
    info = validate_insurance_request("life_individual", 100000.0)
    assert info.product_id == "life_individual"

    # Below minimum
    with pytest.raises(InvalidInsuranceParameterError) as exc_min:
        validate_insurance_request("life_individual", 5000.0)
    assert "inferior ao mínimo" in str(exc_min.value)

    # Above maximum
    with pytest.raises(InvalidInsuranceParameterError) as exc_max:
        validate_insurance_request("life_individual", 2000000.0)
    assert "excede o limite máximo" in str(exc_max.value)


# ---------------------------------------------------------------------------
# 2. Actuarial Math & Risk Multiplier Tests
# ---------------------------------------------------------------------------


def test_calculate_customer_risk_factor_brackets() -> None:
    # Young, Retail
    factor_young, premises_young = calculate_customer_risk_factor(age=28, segment="retail")
    assert factor_young == Decimal("1.00")
    assert "Jovem" in premises_young["age_factor"]

    # Adult, Prime (-5% rel discount)
    factor_adult, premises_adult = calculate_customer_risk_factor(age=45, segment="prime")
    assert factor_adult == Decimal("1.25") * Decimal("0.95")
    assert "Adulta" in premises_adult["age_factor"]

    # Senior, Private (-10% rel discount)
    factor_senior, premises_senior = calculate_customer_risk_factor(age=62, segment="private")
    assert factor_senior == Decimal("1.60") * Decimal("0.90")
    assert "Senior" in premises_senior["age_factor"]


def test_calculate_insurance_premium_precision() -> None:
    product = get_product_info("life_individual")
    # Select mandatory death coverage (rate = 0.00035)
    death_cov = [c for c in product.available_coverages if c.code == "death"]

    calc = calculate_insurance_premium(
        insured_capital=100000.0,
        selected_coverages=death_cov,
        product_info=product,
        customer_age=30,
        customer_segment="retail",
    )

    assert calc["net_monthly_premium"] == 35.00
    assert calc["estimated_iof"] == 0.13
    assert calc["monthly_premium"] == 35.13
    assert calc["annual_premium"] == 400.52


def test_calculate_insurance_premium_home_iof_738() -> None:
    product = get_product_info("home_complete")
    # mandatory fire (rate = 0.00020)
    fire_cov = [c for c in product.available_coverages if c.code == "fire_lightning_explosion"]

    calc = calculate_insurance_premium(
        insured_capital=500000.0,
        selected_coverages=fire_cov,
        product_info=product,
        customer_age=40,
        customer_segment="retail",
    )

    assert calc["net_monthly_premium"] == 125.00
    assert calc["estimated_iof"] == 9.23
    assert calc["monthly_premium"] == 134.23


# ---------------------------------------------------------------------------
# 3. Tool Handler Tests
# ---------------------------------------------------------------------------


def test_tools_list_insurance_products(insurance_tools: InsuranceTools) -> None:
    products = insurance_tools.list_insurance_products()
    assert len(products) >= 4


def test_tools_get_coverage_details(insurance_tools: InsuranceTools) -> None:
    coverages = insurance_tools.get_coverage_details("life_individual")
    codes = {c.code for c in coverages}
    assert "death" in codes
    assert "critical_illness" in codes


def test_tools_simulate_insurance_quote_mandatory_and_optional(
    insurance_tools: InsuranceTools,
) -> None:
    result = insurance_tools.simulate_insurance_quote(
        customer_id="CUST-0001",
        product_id="life_individual",
        insured_capital=150000.0,
        optional_coverages=["critical_illness", "accidental_disability"],
    )

    assert isinstance(result, InsuranceQuoteResult)
    assert result.customer_id == "CUST-0001"
    assert result.insured_capital == 150000.0
    assert len(result.included_coverages) == 3
    assert result.monthly_premium > 0
    assert result.annual_premium > 0
    assert result.disclaimer == DEFAULT_INSURANCE_DISCLAIMER
    assert "Faixa" in result.underwriting_premises["age_factor"]


def test_tools_simulate_insurance_quote_invalid_coverage(
    insurance_tools: InsuranceTools,
) -> None:
    with pytest.raises(CoverageNotFoundError):
        insurance_tools.simulate_insurance_quote(
            product_id="life_individual",
            insured_capital=100000.0,
            optional_coverages=["invalid_coverage_xyz"],
        )


def test_tools_simulate_insurance_quote_unknown_customer(
    insurance_tools: InsuranceTools,
) -> None:
    result = insurance_tools.simulate_insurance_quote(
        customer_id="CUST-9999",
        product_id="life_individual",
        insured_capital=50000.0,
    )
    assert result.monthly_premium > 0
    assert result.disclaimer == DEFAULT_INSURANCE_DISCLAIMER


# ---------------------------------------------------------------------------
# 4. JSON-RPC Protocol Server Tests
# ---------------------------------------------------------------------------


def test_server_initialize(insurance_server: InsuranceMCPServer) -> None:
    resp = insurance_server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert resp["id"] == 1
    assert resp["result"]["serverInfo"]["name"] == "atlas-mcp-insurance"


def test_server_ping(insurance_server: InsuranceMCPServer) -> None:
    resp = insurance_server.handle_request({"jsonrpc": "2.0", "id": 2, "method": "ping"})
    assert resp["result"] == {}


def test_server_tools_list(insurance_server: InsuranceMCPServer) -> None:
    resp = insurance_server.handle_request({"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
    tools = resp["result"]["tools"]
    names = {t["name"] for t in tools}
    assert "list_insurance_products" in names
    assert "get_coverage_details" in names
    assert "simulate_insurance_quote" in names


def test_server_tools_call_simulate(insurance_server: InsuranceMCPServer) -> None:
    resp = insurance_server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "simulate_insurance_quote",
                "arguments": {
                    "product_id": "life_individual",
                    "insured_capital": 200000.0,
                    "optional_coverages": ["funeral_assist"],
                },
            },
        }
    )
    assert "error" not in resp
    content = resp["result"]["content"][0]["text"]
    data = json.loads(content)
    assert data["product_id"] == "life_individual"
    assert data["insured_capital"] == 200000.0
    assert data["disclaimer"] == DEFAULT_INSURANCE_DISCLAIMER


def test_server_tools_call_unknown_tool(insurance_server: InsuranceMCPServer) -> None:
    resp = insurance_server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "invalid_tool", "arguments": {}},
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
    assert resp.json()["service"] == "atlas-mcp-insurance"


def test_http_tools_list(http_client: TestClient) -> None:
    resp = http_client.get("/tools")
    assert resp.status_code == 200
    assert len(resp.json()["tools"]) == 3


def test_http_tool_rest_simulation(http_client: TestClient) -> None:
    resp = http_client.post(
        "/tools/simulate_insurance_quote",
        json={"product_id": "home_complete", "insured_capital": 300000.0},
    )
    assert resp.status_code == 200
    data = resp.json()["result"]
    assert data["product_id"] == "home_complete"
    assert data["monthly_premium"] > 0
    assert data["disclaimer"] == DEFAULT_INSURANCE_DISCLAIMER


def test_http_tool_rest_error_handling(http_client: TestClient) -> None:
    resp = http_client.post(
        "/tools/simulate_insurance_quote",
        json={"product_id": "home_complete", "insured_capital": 1000.0},
    )
    assert resp.status_code == 400
    assert "inferior ao mínimo" in resp.json()["detail"]["message"]
