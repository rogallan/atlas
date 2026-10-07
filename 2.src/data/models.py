"""Typed Pydantic models for the synthetic customer database (S02).

All entities modeled here represent 100% synthetic, fictitious banking data.
No real customer, account, or transaction data is ever used in ATLAS.
"""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class CustomerSegment(StrEnum):
    """Customer banking segment."""

    RETAIL = "retail"
    PRIME = "prime"
    PRIVATE = "private"
    CORPORATE_SMB = "corporate_smb"


class AccountType(StrEnum):
    """Account type."""

    CHECKING = "checking"
    SAVINGS = "savings"
    INVESTMENT = "investment"


class AccountStatus(StrEnum):
    """Account lifecycle status."""

    ACTIVE = "active"
    BLOCKED = "blocked"
    CLOSED = "closed"


class ProductCategory(StrEnum):
    """Catalog product categories aligned with MCP servers."""

    LOAN = "loan"
    INSURANCE = "insurance"
    CONSORTIUM = "consortium"
    TARIFF = "tariff"


class ContractStatus(StrEnum):
    """Contract status."""

    ACTIVE = "active"
    PENDING_CONFIRMATION = "pending_confirmation"
    SETTLED = "settled"
    CANCELLED = "cancelled"


class FinancialEventType(StrEnum):
    """Financial event transaction type."""

    PIX_IN = "pix_in"
    PIX_OUT = "pix_out"
    SALARY_DEPOSIT = "salary_deposit"
    BILL_PAYMENT = "bill_payment"
    LOAN_DISBURSEMENT = "loan_disbursement"
    LOAN_INSTALLMENT = "loan_installment"
    TARIFF_CHARGE = "tariff_charge"
    INSURANCE_PREMIUM = "insurance_premium"


class Customer(BaseModel):
    """Synthetic customer profile."""

    id: str = Field(..., description="Unique fictitious customer identifier, e.g. CUST-0001")
    name: str = Field(..., description="Fictitious full name")
    email: str = Field(..., description="Fictitious email address")
    document_hash: str = Field(..., description="Fictitious hashed CPF/CNPJ identifier")
    segment: CustomerSegment
    credit_score: int = Field(..., ge=0, le=1000, description="Simulated credit score (0-1000)")
    # pyrefly: ignore [bad-argument-type]
    income_monthly: Decimal = Field(..., ge=0, description="Monthly income in BRL")
    created_at: date


class Account(BaseModel):
    """Synthetic bank account."""

    id: str = Field(..., description="Unique fictitious account identifier, e.g. ACC-0001")
    customer_id: str = Field(..., description="Reference to Customer.id")
    type: AccountType
    status: AccountStatus = AccountStatus.ACTIVE
    currency: str = Field(default="BRL")
    balance: Decimal = Field(..., description="Current balance in BRL")
    opened_at: date


class Product(BaseModel):
    """Fictitious banking product offering."""

    id: str = Field(..., description="Unique product identifier, e.g. PROD-LOAN-01")
    name: str
    category: ProductCategory
    description: str
    min_credit_score: int = Field(default=0, ge=0, le=1000)
    base_rate_or_fee: Decimal = Field(..., description="Base interest rate (%) or monthly fee")


class Contract(BaseModel):
    """Contractual agreement between customer and banking product."""

    id: str = Field(..., description="Unique contract identifier, e.g. CTR-0001")
    customer_id: str = Field(..., description="Reference to Customer.id")
    product_id: str = Field(..., description="Reference to Product.id")
    status: ContractStatus
    principal_amount: Decimal | None = None
    installment_amount: Decimal | None = None
    start_date: date
    end_date: date | None = None
    terms: dict[str, Any] = Field(default_factory=dict)


class FinancialEvent(BaseModel):
    """Transaction or financial ledger event."""

    id: str = Field(..., description="Unique event identifier, e.g. EVT-0001")
    account_id: str = Field(..., description="Reference to Account.id")
    type: FinancialEventType
    amount: Decimal = Field(..., description="Transaction amount in BRL (positive value)")
    timestamp: datetime
    description: str


class CustomerHistory(BaseModel):
    """Aggregated historical summary for a customer."""

    customer_id: str
    total_balance: Decimal
    active_contracts_count: int
    total_borrowed: Decimal
    credit_risk_tier: str = Field(..., description="Risk tier: LOW, MEDIUM, HIGH")
    last_activity_date: date | None
    events_count: int


class SyntheticDataset(BaseModel):
    """Complete root bundle of synthetic customer data."""

    version: str
    seed: int
    generated_at: str
    disclaimer: str
    customers: list[Customer]
    accounts: list[Account]
    products: list[Product]
    contracts: list[Contract]
    financial_events: list[FinancialEvent]
    histories: list[CustomerHistory]
