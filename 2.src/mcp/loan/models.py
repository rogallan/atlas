"""Pydantic data models and schemas for MCP Loan Server (S09)."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_LOAN_DISCLAIMER: str = (
    "Simulação baseada em dados puramente sintéticos e regras fictícias. "
    "Não constitui aprovação ou oferta vinculante de crédito."
)


class LoanModality(StrEnum):
    """Credit modality types aligned with Brazilian banking standards."""

    PERSONAL_CREDIT = "personal_credit"  # Crédito Pessoal / CDC
    PAYROLL_LOAN = "payroll_loan"  # Empréstimo Consignado
    WORKING_CAPITAL = "working_capital"  # Capital de Giro


class ModalityInfo(BaseModel):
    """Characteristics and regulatory constraints of a loan modality."""

    model_config = ConfigDict(extra="ignore")

    modality: LoanModality = Field(description="Internal modality identifier")
    display_name: str = Field(description="Commercial name of the product")
    min_amount: float = Field(ge=0.0, description="Minimum loan amount in BRL")
    max_amount: float = Field(gt=0.0, description="Maximum loan amount in BRL")
    min_term_months: int = Field(ge=1, description="Minimum term in months")
    max_term_months: int = Field(ge=1, description="Maximum term in months")
    monthly_interest_rate: float = Field(
        gt=0.0, description="Benchmark monthly rate (e.g. 0.0219 for 2.19%)"
    )
    annual_interest_rate: float = Field(
        gt=0.0, description="Compound annual rate (e.g. 0.297 for 29.7%)"
    )
    max_debt_income_ratio: float = Field(
        gt=0.0, le=1.0, description="Maximum allowed debt-to-income ratio (e.g. 0.30)"
    )
    description: str = Field(description="Regulatory and commercial description")


class AmortizationScheduleItem(BaseModel):
    """Amortization schedule entry for an individual month (Price Table)."""

    model_config = ConfigDict(extra="ignore")

    month: int = Field(ge=1, description="Installment month number (1 to n)")
    installment: float = Field(gt=0.0, description="Total monthly installment amount in BRL")
    interest: float = Field(ge=0.0, description="Interest portion of the installment in BRL")
    amortization: float = Field(ge=0.0, description="Principal amortization portion in BRL")
    remaining_balance: float = Field(
        ge=0.0, description="Outstanding balance after installment in BRL"
    )


class LoanSimulationResult(BaseModel):
    """Complete loan simulation output with financial parameters and disclaimers."""

    model_config = ConfigDict(extra="ignore")

    customer_id: str | None = Field(default=None, description="Queried customer ID if provided")
    modality: LoanModality = Field(description="Selected credit modality")
    modality_display_name: str = Field(description="Commercial product name")
    requested_amount: float = Field(gt=0.0, description="Financed principal amount in BRL")
    term_months: int = Field(ge=1, description="Contract term in months")
    monthly_installment: float = Field(gt=0.0, description="Monthly payment (PMT) in BRL")
    total_interest: float = Field(ge=0.0, description="Total interest paid over the term in BRL")
    total_amount_payable: float = Field(
        gt=0.0, description="Total amount payable (Principal + Interest + IOF) in BRL"
    )
    monthly_interest_rate: float = Field(gt=0.0, description="Applied monthly interest rate")
    annual_interest_rate: float = Field(gt=0.0, description="Applied annual interest rate")
    annual_cet: float = Field(gt=0.0, description="Total Effective Cost (CET) annualized")
    estimated_iof: float = Field(ge=0.0, description="Estimated federal IOF tax in BRL")
    customer_monthly_income: float | None = Field(
        default=None, description="Customer monthly income if known"
    )
    debt_to_income_ratio: float | None = Field(
        default=None,
        description="Installment percentage relative to monthly income (e.g. 0.25 = 25%)",
    )
    is_within_margin: bool = Field(
        default=True, description="True if installment is within debt-to-income margin"
    )
    margin_limit_ratio: float = Field(description="Maximum regulatory margin threshold")
    disclaimer: str = Field(
        default=DEFAULT_LOAN_DISCLAIMER, description="Mandatory non-binding disclaimer"
    )
    schedule_summary: list[AmortizationScheduleItem] = Field(
        default_factory=list,
        description="First few and final installments of the amortization schedule",
    )


class PreConditionsCheckResult(BaseModel):
    """Result of debt-to-income and customer eligibility check."""

    model_config = ConfigDict(extra="ignore")

    customer_id: str = Field(description="Customer identifier")
    modality: LoanModality = Field(description="Target loan modality")
    customer_monthly_income: float = Field(description="Registered monthly income in BRL")
    monthly_installment: float = Field(description="Proposed installment amount in BRL")
    debt_to_income_ratio: float = Field(description="Calculated ratio (installment / income)")
    margin_limit_ratio: float = Field(description="Allowed maximum threshold")
    is_eligible: bool = Field(description="True if within margin limit")
    message: str = Field(description="Diagnostic eligibility message")


# ---------------------------------------------------------------------------
# Tool Input Schemas
# ---------------------------------------------------------------------------


class SimulateLoanInput(BaseModel):
    """Input parameters for simulate_loan."""

    model_config = ConfigDict(extra="ignore")

    customer_id: str | None = Field(
        default=None,
        pattern=r"^CUST-\d{4}$",
        description="Optional synthetic customer identifier (e.g. CUST-0001)",
    )
    amount: float = Field(
        default=10000.0,
        gt=0.0,
        description="Requested loan principal amount in BRL",
    )
    term_months: int = Field(
        default=24,
        ge=1,
        le=120,
        description="Financing term in months (e.g. 12, 24, 36, 48)",
    )
    modality: LoanModality = Field(
        default=LoanModality.PERSONAL_CREDIT,
        description="Credit modality: personal_credit, payroll_loan, working_capital",
    )


class CheckLoanPreConditionsInput(BaseModel):
    """Input parameters for check_loan_pre_conditions."""

    model_config = ConfigDict(extra="ignore")

    customer_id: str = Field(
        pattern=r"^CUST-\d{4}$",
        description="Synthetic customer identifier (e.g. CUST-0001)",
    )
    monthly_installment: float = Field(
        gt=0.0,
        description="Proposed monthly installment value in BRL",
    )
    modality: LoanModality = Field(
        default=LoanModality.PERSONAL_CREDIT,
        description="Target credit modality",
    )


# ---------------------------------------------------------------------------
# Domain Exceptions
# ---------------------------------------------------------------------------


class MCPLoanError(Exception):
    """Base exception for loan server operations."""

    def __init__(self, message: str, code: int = -32000, details: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details


class InvalidLoanParameterError(MCPLoanError):
    """Raised when loan parameters violate modality bounds."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, code=422)


class ModalityNotFoundError(MCPLoanError):
    """Raised when an unknown credit modality is requested."""

    def __init__(self, modality: str) -> None:
        super().__init__(message=f"Modalidade de crédito não encontrada: '{modality}'", code=404)
