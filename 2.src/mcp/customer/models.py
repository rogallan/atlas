"""Pydantic data models and schemas for MCP Customer Server (S08)."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CustomerSegment(StrEnum):
    """Customer banking segment."""

    RETAIL = "retail"
    PRIME = "prime"
    PRIVATE = "private"
    CORPORATE_SMB = "corporate_smb"


class CustomerProfileResponse(BaseModel):
    """Customer profile and relationship health indicators."""

    model_config = ConfigDict(extra="ignore")

    customer_id: str = Field(description="Unique synthetic customer identifier")
    full_name: str = Field(description="Customer full fictitious name")
    email: str = Field(description="Simulated customer email address")
    document_hash: str = Field(description="Simulated hashed document identifier")
    segment: CustomerSegment = Field(description="Assigned banking segment")
    monthly_income: float = Field(ge=0.0, description="Monthly income in BRL")
    relationship_years: int = Field(ge=0, description="Tenure with the bank in years")
    credit_score: int = Field(ge=0, le=1000, description="Simulated credit score (0-1000)")
    credit_score_range: str = Field(description="Credit score bracket (e.g. 701-850)")
    risk_rating: str = Field(description="Credit risk classification (LOW, MEDIUM, HIGH)")


class AccountSummary(BaseModel):
    """Synthetic account balance and status overview."""

    model_config = ConfigDict(extra="ignore")

    account_id: str = Field(description="Unique account identifier")
    account_number: str = Field(description="Formatted account number")
    branch: str = Field(default="0001", description="Branch / agency number")
    account_type: str = Field(description="checking, savings, or investment")
    balance: float = Field(description="Current account balance in BRL")
    currency: str = Field(default="BRL", description="Currency code")
    status: str = Field(default="active", description="Account lifecycle status")


class FinancialEventItem(BaseModel):
    """Individual financial ledger transaction or payment event."""

    model_config = ConfigDict(extra="ignore")

    event_id: str = Field(description="Unique transaction event identifier")
    account_id: str = Field(description="Associated account identifier")
    event_date: str = Field(description="ISO timestamp of the transaction")
    description: str = Field(description="Transaction narration or description")
    amount: float = Field(description="Transaction amount in BRL")
    category: str = Field(description="Category or transaction type (pix, loan, salary, etc.)")


class CustomerSummaryResponse(BaseModel):
    """Aggregated briefing view for the relationship manager."""

    model_config = ConfigDict(extra="ignore")

    profile: CustomerProfileResponse = Field(description="Customer profile details")
    accounts: list[AccountSummary] = Field(description="List of active/registered accounts")
    total_balance: float = Field(description="Total aggregated balance across all accounts in BRL")
    active_contracts_count: int = Field(ge=0, description="Number of active banking contracts")
    recent_events: list[FinancialEventItem] = Field(
        default_factory=list,
        description="Chronological list of recent financial events",
    )
    relationship_notes: str | None = Field(
        default=None,
        description="Automated briefing notes or insights for the manager",
    )


# ---------------------------------------------------------------------------
# Tool Input Schemas
# ---------------------------------------------------------------------------


class GetCustomerProfileInput(BaseModel):
    """Input parameters for get_customer_profile."""

    model_config = ConfigDict(extra="ignore")

    customer_id: str = Field(
        description="Fictitious customer identifier (e.g. CUST-0001)",
        pattern=r"^CUST-\d{4}$",
    )


class GetCustomerAccountsInput(BaseModel):
    """Input parameters for get_customer_accounts."""

    model_config = ConfigDict(extra="ignore")

    customer_id: str = Field(
        description="Fictitious customer identifier (e.g. CUST-0001)",
        pattern=r"^CUST-\d{4}$",
    )


class GetFinancialHistoryInput(BaseModel):
    """Input parameters for get_financial_history."""

    model_config = ConfigDict(extra="ignore")

    customer_id: str = Field(
        description="Fictitious customer identifier (e.g. CUST-0001)",
        pattern=r"^CUST-\d{4}$",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of historical transactions to return (1-50)",
    )


class GetCustomerSummaryInput(BaseModel):
    """Input parameters for get_customer_summary."""

    model_config = ConfigDict(extra="ignore")

    customer_id: str = Field(
        description="Fictitious customer identifier (e.g. CUST-0001)",
        pattern=r"^CUST-\d{4}$",
    )


# ---------------------------------------------------------------------------
# Exceptions & Error Models
# ---------------------------------------------------------------------------


class MCPCustomerError(Exception):
    """Base exception for MCP customer server operations."""

    def __init__(self, message: str, code: int = -32000, details: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details


class CustomerNotFoundError(MCPCustomerError):
    """Raised when the specified customer_id does not exist in the database."""

    def __init__(self, customer_id: str) -> None:
        super().__init__(
            message=f"Cliente não encontrado com o identificador: {customer_id}",
            code=404,
            details={"customer_id": customer_id},
        )


class UnauthorizedError(MCPCustomerError):
    """Raised when the caller lacks required relationship manager authorization."""

    def __init__(self, message: str = "Acesso negado: operador não autorizado.") -> None:
        super().__init__(message=message, code=401)
