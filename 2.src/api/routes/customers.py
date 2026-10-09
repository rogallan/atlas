"""Customer discovery and listing endpoints (S03/S08)."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from mcp.customer.repository import CustomerRepository

router = APIRouter(prefix="/v1", tags=["Customers"])

_repo: CustomerRepository | None = None


def get_repository() -> CustomerRepository:
    global _repo
    if _repo is None:
        _repo = CustomerRepository()
    return _repo


class CustomerSummaryResponse(BaseModel):
    id: str = Field(..., description="Synthetic customer identifier, e.g. CUST-0001")
    name: str = Field(..., description="Customer full name")
    segment: str = Field(..., description="Customer banking segment, e.g. RETAIL, PRIME")
    monthly_income: float = Field(..., description="Declared monthly income")
    credit_score: int = Field(..., description="Synthetic credit score (0-1000)")
    active_account: str = Field(..., description="Primary active account ID")


@router.get(
    "/customers",
    response_model=list[CustomerSummaryResponse],
    summary="List synthetic customers",
    description="Returns all synthetic customers indexed in the repository for copilot context.",
)
async def list_customers() -> list[CustomerSummaryResponse]:
    repo = get_repository()
    customer_ids = repo.list_customer_ids()
    results: list[CustomerSummaryResponse] = []

    for cid in customer_ids:
        cust = repo.get_customer(cid)
        if not cust:
            continue
        accounts = repo.get_accounts(cid)
        primary_account = accounts[0].id if accounts else "N/A"

        results.append(
            CustomerSummaryResponse(
                id=cust.id,
                name=cust.name,
                segment=cust.segment.upper(),
                monthly_income=float(cust.income_monthly),
                credit_score=cust.credit_score,
                active_account=primary_account,
            )
        )

    return results
