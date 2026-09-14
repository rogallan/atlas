# Plan — S13 · MCP Ticket Server

## 1. Approach

Implement the MCP Ticket Server under `src/mcp/ticket/`. The server provides the first state-changing capability of the ATLAS copilot, architected around a strict Human-in-the-Loop (HITL) two-phase commit pattern: `prepare_ticket` returns a confirmation proposal with a signed, short-lived token, and `confirm_and_create_ticket` performs the persistent state change only upon affirmative human consent.

## 2. Architecture & Components

```
src/mcp/ticket/
├── __init__.py
├── server.py        # MCP Server entrypoint, transport & tool registrations
├── tools.py         # Handlers: prepare_ticket, confirm_and_create_ticket, get_ticket, list_customer_tickets
├── models.py        # Pydantic schemas (TicketDraft, TicketRecord, ConfirmationToken, TicketCategory)
├── store.py         # In-memory / file-backed ticket repository with idempotency index
└── audit.py         # Security audit logging module recording approval workflows
```

### Flow of Execution:
1. **Preparation Phase:** The Agent Orchestrator (S14) invokes `prepare_ticket(...)`.
2. **Draft & Token Creation:** `store.py` stages a pending draft with a unique `confirmation_token` valid for 10 minutes.
3. **User Confirmation Prompt:** The Agent returns a confirmation card to the React frontend (S15), asking the relationship manager for explicit confirmation.
4. **Approval Execution:** When the user confirms, the frontend calls the agent, which triggers `confirm_and_create_ticket(token, approved_by_user=True)`.
5. **Guardrail Check:** If `approved_by_user == False` or the token is expired/already used, the operation is blocked and logged as `ACTION_REJECTED`.
6. **State Mutation & Idempotency:** The ticket is committed to `store.py`, generating a persistent ticket number (e.g. `TCK-2024-00123`).
7. **Audit Event:** Emits a structured JSON audit record confirming that explicit human authorization was verified.

## 3. Key Interfaces & Tool Schemas

```python
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class TicketCategory(str, Enum):
  CONTESTATION = "contestation"
  CARD_MAINTENANCE = "card_maintenance"
  LIMIT_INCREASE = "limit_increase"
  TARIFF_REVIEW = "tariff_review"
  GENERAL_INQUIRY = "general_inquiry"


class TicketPriority(str, Enum):
  LOW = "low"
  MEDIUM = "medium"
  HIGH = "high"
  URGENT = "urgent"


class TicketStatus(str, Enum):
  PENDING_APPROVAL = "pending_approval"
  OPEN = "open"
  IN_ANALYSIS = "in_analysis"
  REJECTED = "rejected"
  CLOSED = "closed"


class TicketDraft(BaseModel):
  confirmation_token: str
  customer_id: str
  category: TicketCategory
  title: str
  description: str
  priority: TicketPriority
  expires_at: datetime
  summary_for_human: str


class TicketRecord(BaseModel):
  ticket_id: str
  customer_id: str
  category: TicketCategory
  title: str
  description: str
  priority: TicketPriority
  status: TicketStatus
  created_at: datetime
  approved_by_user: bool
  operator_id: str
```

```python
# Tool Signatures
def prepare_ticket(
    customer_id: str,
    category: TicketCategory,
    title: str,
    description: str,
    priority: TicketPriority = TicketPriority.MEDIUM,
) -> TicketDraft:
  ...


def confirm_and_create_ticket(
    confirmation_token: str,
    approved_by_user: bool,
    idempotency_key: str | None = None,
) -> TicketRecord:
  ...


def get_ticket(ticket_id: str) -> TicketRecord:
  ...


def list_customer_tickets(customer_id: str) -> list[TicketRecord]:
  ...
```

## 4. Security & Guardrail Strategy (Constitution Principle 2)

- **Two-Phase Enforcement:** The server refuses to instantiate a `TicketRecord` directly without passing through a valid `confirmation_token`.
- **Replay Protection:** Once a token is submitted to `confirm_and_create_ticket`, it is invalidated immediately.
- **Idempotency Store:** If `idempotency_key` is reused within 24 hours, return the previously created `TicketRecord` without altering state.
- **Audit Logging Structure:**
  ```json
  {
    "event": "ticket_action_executed",
    "timestamp": "2026-09-11T00:45:00Z",
    "operator_id": "manager_001",
    "customer_id": "CUST-789",
    "ticket_id": "TCK-2024-00123",
    "approved_by_human": true,
    "category": "card_maintenance"
  }
  ```

## 5. Test Strategy

- **Happy Path Workflow Test:** `prepare_ticket` -> receive token -> `confirm_and_create_ticket(token, approved=True)` -> verify `status == 'open'`.
- **Rejection Guardrail Test:** `confirm_and_create_ticket(token, approved=False)` -> assert status `rejected`, state uncommitted, rejection audit emitted.
- **Expired Token Test:** Advance clock beyond TTL -> verify token expiration error.
- **Idempotency Test:** Resubmit identical `idempotency_key` -> verify single ticket generated.
- **Audit Log Verification:** Verify structured audit lines for draft, approved, and blocked attempts.

## 6. Risks & Mitigations

- **Risk:** Agent bypassing human approval by automatically setting `approved_by_user=True`.
  - **Mitigation:** The Agent Graph (S14) and FastAPI Gateway (S03) enforce that `confirm_and_create_ticket` can only be invoked when the client's HTTP request specifically carries the user's interactive button click response.
- **Risk:** Accumulation of abandoned ticket drafts in memory.
  - **Mitigation:** Implement periodic cache eviction for expired confirmation tokens.
