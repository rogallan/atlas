# Plan — S08 · MCP Customer Server

## 1. Approach

Implement the MCP Customer Server in `src/mcp/customer/`. The server will use the official Python `mcp` SDK (or FastMCP abstraction) and read directly from the synthetic dataset produced in S02 via a repository abstraction. It provides typed tools, strictly validates inputs via Pydantic, applies a simulated authorization filter, and emits structured audit events.

## 2. Architecture & Components

```
src/mcp/customer/
├── __init__.py
├── server.py        # MCP Server entrypoint, transport & tool registrations
├── tools.py         # Business handlers for profile, accounts, history, and summary
├── models.py        # Pydantic input/output schemas
├── repository.py    # Synthetic customer database read repository (queries S02 dataset)
└── auth.py          # Simulated authorization & audit logger
```

### Component Flow:
1. **Tool Invocation:** The Agent Orchestrator (S14) invokes `get_customer_profile` or `get_customer_summary` via MCP client.
2. **Schema Validation:** MCP layer validates incoming parameters against Pydantic models in `models.py`.
3. **Simulated Authorization:** `auth.py` verifies the simulated caller context (e.g., manager token/role).
4. **Data Retrieval:** `repository.py` looks up the customer record in the synthetic dataset.
5. **Audit Logging:** An audit event is recorded with timestamp, operator ID, and queried customer ID.
6. **Structured Response:** The typed Pydantic response model is serialized and returned to the caller.

## 3. Key Interfaces & Tool Schemas

```python
from enum import Enum
from pydantic import BaseModel, Field


class CustomerSegment(str, Enum):
  RETAIL = "retail"
  PREMIUM = "premium"
  PRIVATE = "private"


class CustomerProfileResponse(BaseModel):
  customer_id: str
  full_name: str
  segment: CustomerSegment
  monthly_income: float
  relationship_years: int
  credit_score_range: str
  risk_rating: str


class AccountSummary(BaseModel):
  account_number: str
  branch: str
  account_type: str
  balance: float
  currency: str = "BRL"
  status: str


class FinancialEventItem(BaseModel):
  event_id: str
  event_date: str
  description: str
  amount: float
  category: str


class CustomerSummaryResponse(BaseModel):
  profile: CustomerProfileResponse
  accounts: list[AccountSummary]
  active_contracts_count: int
  recent_events: list[FinancialEventItem]
  relationship_notes: str | None = None
```

```python
# MCP Tool Signatures
def get_customer_profile(customer_id: str) -> CustomerProfileResponse:
  ...


def get_customer_accounts(customer_id: str) -> list[AccountSummary]:
  ...


def get_financial_history(
    customer_id: str, limit: int = 10
) -> list[FinancialEventItem]:
  ...


def get_customer_summary(customer_id: str) -> CustomerSummaryResponse:
  ...
```

## 4. Security & Simulated Authorization Strategy

- **Simulated Auth Context:** Every request passes an authorization header/metadata dictionary. If the caller does not hold the simulated `manager` or `analyst` role, return a structured `MCPError(code=UNAUTHORIZED)`.
- **Audit Logging:** Emits JSON log events containing `{ "event": "customer_data_access", "customer_id": "...", "operator_id": "...", "tool": "...", "timestamp": "..." }` to standard ops logger, keeping access fully traceable.
- **PII Protection:** Only synthetic attributes from S02 are exposed. No real identity registries or live services are queried.

## 5. Test Strategy

- **Contract Tests:** Validate that tools adhere to MCP schemas (input validation, output shapes, error codes).
- **Repository Integration Tests:** Query known customer IDs from S02 seed to verify deterministic data match.
- **Negative / Edge Tests:**
  - Non-existent `customer_id` -> returns `CustomerNotFoundError`.
  - Negative/zero limit in `get_financial_history` -> validation error.
  - Missing authorization -> returns unauthorized error.
- **Audit Logging Verification:** Verify an audit log entry is written for each successful and denied query.

## 6. Risks & Mitigations

- **Risk:** Discrepancy between S02 dataset models and MCP tool output schemas.
  - **Mitigation:** Import core domain entities from `src/data/models.py` (established in S02) into the repository layer and map explicitly to customer tool DTOs.
- **Risk:** MCP protocol transport instability in local testing.
  - **Mitigation:** Support both stdio and direct in-memory tool calling for fast unit/integration testing without spawning child processes.
