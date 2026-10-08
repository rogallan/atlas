"""Unit, contract, and mathematical tests for MCP Loan Server (S09)."""

import json
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from mcp.customer.models import CustomerNotFoundError
from mcp.customer.repository import CustomerRepository
from mcp.loan.calculator import (
    calculate_annual_cet,
    calculate_iof,
    calculate_pmt,
    generate_amortization_schedule,
)
from mcp.loan.catalog import (
    get_all_modalities,
    get_modality_info,
    validate_loan_request,
)
from mcp.loan.http_server import app
from mcp.loan.models import (
    DEFAULT_LOAN_DISCLAIMER,
    InvalidLoanParameterError,
    LoanModality,
    LoanSimulationResult,
)
from mcp.loan.server import LoanMCPServer, create_loan_server
from mcp.loan.tools import LoanTools


@pytest.fixture
def repository() -> CustomerRepository:
    """Fixture providing initialized CustomerRepository."""
    return CustomerRepository()


@pytest.fixture
def tools(repository: CustomerRepository) -> LoanTools:
    """Fixture providing LoanTools."""
    return LoanTools(customer_repository=repository)


@pytest.fixture
def server(repository: CustomerRepository) -> LoanMCPServer:
    """Fixture providing LoanMCPServer."""
    return LoanMCPServer(customer_repository=repository)


# ---------------------------------------------------------------------------
# 1. Financial Math Engine Tests (Tabela Price, IOF, CET)
# ---------------------------------------------------------------------------


def test_calculate_iof_formula() -> None:
    """calculate_iof computes exact regulatory IOF (0.38% + daily rate capped at 365 days)."""
    principal = Decimal("10000.00")
    # 24 months = 720 days, capped at 365 days
    # IOF = 10000 * (0.0038 + 365 * 0.000082) = 10000 * 0.03373 = 337.30
    iof_24m = calculate_iof(principal, term_months=24)
    assert iof_24m == Decimal("337.30")

    # 6 months = 180 days
    # IOF = 10000 * (0.0038 + 180 * 0.000082) = 10000 * 0.01856 = 185.60
    iof_6m = calculate_iof(principal, term_months=6)
    assert iof_6m == Decimal("185.60")


def test_calculate_pmt_tabela_price_benchmark() -> None:
    """calculate_pmt matches standard Price formula benchmark down to the cent."""
    # PV = 10000.00, i = 2.0% (0.02), n = 12
    # PMT benchmark = 945.60
    pmt = calculate_pmt(Decimal("10000.00"), Decimal("0.02"), 12)
    assert pmt == Decimal("945.60")

    # Zero interest rate case
    pmt_zero = calculate_pmt(Decimal("12000.00"), Decimal("0.00"), 12)
    assert pmt_zero == Decimal("1000.00")


def test_calculate_annual_cet() -> None:
    """calculate_annual_cet produces an annualized effective rate higher than nominal."""
    principal = Decimal("10000.00")
    nominal_rate = Decimal("0.0219")  # 2.19% a.m.
    pmt = Decimal("550.00")
    n = 24

    cet = calculate_annual_cet(principal, pmt, n, nominal_rate)
    assert cet > Decimal("0.25")  # Must be > 25% a.a.


def test_generate_amortization_schedule() -> None:
    """Amortization schedule amortizes full balance to exactly zero."""
    financed = Decimal("10337.30")
    rate = Decimal("0.0219")
    n = 12
    pmt = calculate_pmt(financed, rate, n)

    schedule = generate_amortization_schedule(financed, rate, pmt, n)

    assert len(schedule) == 12
    assert schedule[0].month == 1
    assert schedule[-1].month == 12
    assert schedule[-1].remaining_balance == 0.0

    total_amortized = sum(item.amortization for item in schedule)
    assert round(total_amortized, 2) == float(financed)


# ---------------------------------------------------------------------------
# 2. Catalog and Boundary Validation Tests
# ---------------------------------------------------------------------------


def test_modalities_catalog_completeness() -> None:
    """Catalog contains all 3 required credit modalities."""
    modalities = get_all_modalities()
    assert len(modalities) == 3
    mod_keys = {m.modality for m in modalities}
    assert mod_keys == {
        LoanModality.PERSONAL_CREDIT,
        LoanModality.PAYROLL_LOAN,
        LoanModality.WORKING_CAPITAL,
    }


def test_validate_loan_request_boundaries() -> None:
    """validate_loan_request rejects out-of-bounds amounts and terms."""
    # 1. Amount below minimum
    with pytest.raises(InvalidLoanParameterError) as exc:
        validate_loan_request(LoanModality.PERSONAL_CREDIT, amount=100.0, term_months=12)
    assert "abaixo do mínimo" in str(exc.value)

    # 2. Amount above maximum
    with pytest.raises(InvalidLoanParameterError) as exc:
        validate_loan_request(LoanModality.PERSONAL_CREDIT, amount=100000.0, term_months=12)
    assert "acima do teto" in str(exc.value)

    # 3. Term below minimum
    with pytest.raises(InvalidLoanParameterError) as exc:
        validate_loan_request(LoanModality.PERSONAL_CREDIT, amount=5000.0, term_months=3)
    assert "abaixo do mínimo" in str(exc.value)

    # 4. Term above maximum
    with pytest.raises(InvalidLoanParameterError) as exc:
        validate_loan_request(LoanModality.PERSONAL_CREDIT, amount=5000.0, term_months=60)
    assert "acima do teto" in str(exc.value)

    # 5. Valid request succeeds
    info = validate_loan_request(LoanModality.PERSONAL_CREDIT, amount=10000.0, term_months=24)
    assert info.modality == LoanModality.PERSONAL_CREDIT


def test_unknown_modality_lookup() -> None:
    """get_modality_info raises InvalidLoanParameterError for unknown modality."""
    with pytest.raises(InvalidLoanParameterError):
        get_modality_info("unknown_type")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 3. Tool Execution & Debt-to-Income Margin Tests
# ---------------------------------------------------------------------------


def test_simulate_loan_without_customer(tools: LoanTools) -> None:
    """simulate_loan succeeds when customer_id is None and attaches disclaimer."""
    result = tools.simulate_loan(
        customer_id=None,
        amount=15000.0,
        term_months=36,
        modality=LoanModality.PERSONAL_CREDIT,
    )

    assert isinstance(result, LoanSimulationResult)
    assert result.customer_id is None
    assert result.requested_amount == 15000.0
    assert result.term_months == 36
    assert result.monthly_installment > 0.0
    assert result.estimated_iof > 0.0
    assert result.total_amount_payable > 15000.0
    assert result.annual_cet > 0.0
    assert result.disclaimer == DEFAULT_LOAN_DISCLAIMER
    assert len(result.schedule_summary) >= 2


def test_simulate_loan_within_margin(tools: LoanTools) -> None:
    """simulate_loan evaluates debt-to-income margin for Dave Weckl (income R$ 8.274)."""
    # R$ 5.000 in 24x produces ~R$ 280 installment, well below 30% margin (~R$ 2.482)
    result = tools.simulate_loan(
        customer_id="CUST-0001",
        amount=5000.0,
        term_months=24,
        modality=LoanModality.PERSONAL_CREDIT,
    )

    assert result.customer_monthly_income == 8274.0
    assert result.debt_to_income_ratio is not None
    assert result.debt_to_income_ratio < 0.30
    assert result.is_within_margin is True


def test_simulate_loan_exceeding_margin(tools: LoanTools) -> None:
    """simulate_loan flags is_within_margin=False when installment exceeds allowed ratio."""
    # R$ 45.000 in 12x produces ~R$ 4.300 installment, exceeding 30% margin (R$ 2.482)
    result = tools.simulate_loan(
        customer_id="CUST-0001",
        amount=45000.0,
        term_months=12,
        modality=LoanModality.PERSONAL_CREDIT,
    )

    assert result.debt_to_income_ratio is not None
    assert result.debt_to_income_ratio > 0.30
    assert result.is_within_margin is False


def test_check_loan_pre_conditions_approved(tools: LoanTools) -> None:
    """check_loan_pre_conditions returns is_eligible=True for reasonable payment."""
    res = tools.check_loan_pre_conditions(
        customer_id="CUST-0001",
        monthly_installment=800.0,
        modality=LoanModality.PERSONAL_CREDIT,
    )

    assert res.is_eligible is True
    assert "dentro do limite" in res.message


def test_check_loan_pre_conditions_rejected(tools: LoanTools) -> None:
    """check_loan_pre_conditions returns is_eligible=False for excessive payment."""
    res = tools.check_loan_pre_conditions(
        customer_id="CUST-0001",
        monthly_installment=3500.0,
        modality=LoanModality.PERSONAL_CREDIT,
    )

    assert res.is_eligible is False
    assert "excedendo o limite" in res.message


def test_check_loan_pre_conditions_customer_not_found(tools: LoanTools) -> None:
    """check_loan_pre_conditions raises CustomerNotFoundError for unknown customer."""
    with pytest.raises(CustomerNotFoundError):
        tools.check_loan_pre_conditions(
            customer_id="CUST-9999",
            monthly_installment=500.0,
        )


# ---------------------------------------------------------------------------
# 4. MCP Server & JSON-RPC Protocol Tests
# ---------------------------------------------------------------------------


def test_mcp_initialize(server: LoanMCPServer) -> None:
    """JSON-RPC initialize returns server information and capabilities."""
    req = {
        "jsonrpc": "2.0",
        "id": "init-1",
        "method": "initialize",
        "params": {"protocolVersion": "2024-11-05"},
    }
    resp = server.handle_jsonrpc(req)

    assert resp is not None
    assert resp["result"]["serverInfo"]["name"] == "atlas-loan-mcp"
    assert "tools" in resp["result"]["capabilities"]


def test_mcp_ping(server: LoanMCPServer) -> None:
    """JSON-RPC ping returns empty dictionary."""
    req = {"jsonrpc": "2.0", "id": "p-1", "method": "ping"}
    resp = server.handle_jsonrpc(req)
    assert resp is not None
    assert resp["result"] == {}


def test_mcp_tools_list_contract(server: LoanMCPServer) -> None:
    """tools/list advertises all 3 loan tools with valid schemas."""
    req = {"jsonrpc": "2.0", "id": "list-1", "method": "tools/list"}
    resp = server.handle_jsonrpc(req)

    assert resp is not None
    tools = resp["result"]["tools"]
    tool_names = {t["name"] for t in tools}

    assert tool_names == {
        "simulate_loan",
        "get_loan_modalities",
        "check_loan_pre_conditions",
    }


def test_mcp_tools_call_simulate_loan_success(server: LoanMCPServer) -> None:
    """tools/call successfully executes simulate_loan over JSON-RPC."""
    req = {
        "jsonrpc": "2.0",
        "id": "call-1",
        "method": "tools/call",
        "params": {
            "name": "simulate_loan",
            "arguments": {
                "customer_id": "CUST-0001",
                "amount": 10000.0,
                "term_months": 24,
                "modality": "personal_credit",
            },
        },
    }
    resp = server.handle_jsonrpc(req)

    assert resp is not None
    assert resp["result"]["isError"] is False
    payload = json.loads(resp["result"]["content"][0]["text"])
    assert payload["requested_amount"] == 10000.0
    assert payload["term_months"] == 24
    assert payload["monthly_installment"] > 0
    assert "Simulação baseada em dados" in payload["disclaimer"]


def test_mcp_tools_call_validation_error(server: LoanMCPServer) -> None:
    """Out-of-bounds parameters return isError=True over JSON-RPC."""
    req = {
        "jsonrpc": "2.0",
        "id": "call-err",
        "method": "tools/call",
        "params": {
            "name": "simulate_loan",
            "arguments": {
                "amount": -500.0,  # Negative amount violates schema gt=0
                "term_months": 24,
            },
        },
    }
    resp = server.handle_jsonrpc(req)

    assert resp is not None
    assert resp["result"]["isError"] is True


def test_mcp_tools_call_unknown_tool(server: LoanMCPServer) -> None:
    """Unknown tool name returns isError=True."""
    req = {
        "jsonrpc": "2.0",
        "id": "call-unk",
        "method": "tools/call",
        "params": {"name": "invalid_tool", "arguments": {}},
    }
    resp = server.handle_jsonrpc(req)
    assert resp is not None
    assert resp["result"]["isError"] is True


def test_mcp_unknown_method(server: LoanMCPServer) -> None:
    """Unregistered method returns standard -32601 code."""
    req = {"jsonrpc": "2.0", "id": "m-err", "method": "non_existent_method"}
    resp = server.handle_jsonrpc(req)
    assert resp is not None
    assert resp["error"]["code"] == -32601


def test_create_loan_server_helper() -> None:
    """create_loan_server helper creates a working server instance."""
    srv = create_loan_server()
    assert isinstance(srv, LoanMCPServer)
    assert len(srv.get_tool_definitions()) == 3


# ---------------------------------------------------------------------------
# 5. HTTP & SSE Transport Server Tests
# ---------------------------------------------------------------------------


def test_loan_http_server_endpoints() -> None:
    """Test HTTP transport endpoints on LoanMCPServer."""
    client = TestClient(app)

    # 1. Health
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["service"] == "atlas-loan-mcp"

    # 2. Tools
    res_tools = client.get("/tools")
    assert res_tools.status_code == 200
    assert len(res_tools.json()["tools"]) == 3

    # 3. REST invocation of simulate_loan
    res_call = client.post(
        "/tools/simulate_loan",
        json={"amount": 10000.0, "term_months": 24, "modality": "personal_credit"},
    )
    assert res_call.status_code == 200
    data = res_call.json()["result"]
    assert data["requested_amount"] == 10000.0
    assert data["monthly_installment"] > 0

    # 4. JSON-RPC over HTTP
    rpc_req = {
        "jsonrpc": "2.0",
        "id": "rpc-http",
        "method": "tools/call",
        "params": {"name": "get_loan_modalities", "arguments": {}},
    }
    res_rpc = client.post("/mcp/jsonrpc", json=rpc_req)
    assert res_rpc.status_code == 200
    assert res_rpc.json()["result"]["isError"] is False
