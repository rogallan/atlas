# Plan — S09 · MCP Loan Server

## 1. Approach

Implement the MCP Loan Server under `src/mcp/loan/`. The server provides purely computational and rule-evaluating tools. It interacts with the synthetic customer repository (from S02/S08) solely to read income data for debt-to-income margin validation, applies strict financial formulas (Tabela Price), validates input ranges via Pydantic, and returns detailed simulation cards for the frontend (S15).

## 2. Architecture & Components

```
src/mcp/loan/
├── __init__.py
├── server.py        # MCP Server entrypoint, transport & tool registration
├── tools.py         # Handlers: simulate_loan, get_loan_modalities, check_loan_pre_conditions
├── models.py        # Pydantic schemas (LoanModality, SimulationRequest, LoanSimulationResult)
├── calculator.py    # Deterministic financial math (Price amortization, CET, IOF, PMT)
└── catalog.py       # Supported loan modalities, interest rates, and term limits
```

### Flow of Execution:
1. **Tool Invocation:** The Agent Orchestrator (S14) invokes `simulate_loan(customer_id, amount, term_months, modality)`.
2. **Schema & Range Validation:** `models.py` and `catalog.py` validate that amount and term comply with modality boundaries.
3. **Financial Math:** `calculator.py` computes monthly installment ($PMT = PV \cdot \frac{i(1+i)^n}{(1+i)^n - 1}$), estimated taxes (IOF), and CET.
4. **Synthetic Margin Check:** If `customer_id` is supplied, customer income is queried via synthetic repository to calculate installment-to-income ratio (`comprometimento_renda_pct`).
5. **Enrichment & Disclaimer:** Attach calculation premises, summary amortization schedule, and the mandatory non-binding simulation disclaimer.
6. **Structured Output:** Result returned via MCP JSON-RPC.

## 3. Key Interfaces & Tool Schemas

```python
from enum import Enum
from pydantic import BaseModel, Field


class LoanModality(str, Enum):
  PERSONAL_CREDIT = "personal_credit"  # Crédito Pessoal / CDC
  PAYROLL_LOAN = "payroll_loan"  # Empréstimo Consignado
  WORKING_CAPITAL = "working_capital"  # Capital de Giro


class ModalityInfo(BaseModel):
  modality: LoanModality
  display_name: str
  min_amount: float
  max_amount: float
  min_term_months: int
  max_term_months: int
  monthly_interest_rate: float
  annual_interest_rate: float
  max_debt_income_ratio: float


class LoanSimulationResult(BaseModel):
  customer_id: str | None
  modality: LoanModality
  requested_amount: float
  term_months: int
  monthly_installment: float
  total_interest: float
  total_amount_payable: float
  monthly_interest_rate: float
  annual_cet: float  # Custo Efetivo Total anualizado
  estimated_iof: float
  debt_to_income_ratio: float | None = Field(
      default=None, description="% da renda sintética comprometida"
  )
  is_within_margin: bool = True
  disclaimer: str = Field(
      default=(
          "Simulação baseada em dados puramente sintéticos e regras fictícias."
          " Não constitui aprovação ou oferta vinculante de crédito."
      )
  )
```

```python
# Tool Signatures
def simulate_loan(
    customer_id: str | None = None,
    amount: float = 10000.0,
    term_months: int = 24,
    modality: LoanModality = LoanModality.PERSONAL_CREDIT,
) -> LoanSimulationResult:
  ...


def get_loan_modalities() -> list[ModalityInfo]:
  ...


def check_loan_pre_conditions(
    customer_id: str, amount: float, monthly_installment: float
) -> dict:
  ...
```

## 4. Financial Calculation Formulas (Tabela Price)

- **Installment Calculation (PMT):**
  $$PMT = PV \times \frac{i \times (1 + i)^n}{(1 + i)^n - 1}$$
  where $PV$ is financed amount + IOF, $i$ is monthly interest rate, $n$ is term in months.
- **IOF Estimation:** Fixed baseline IOF (0.38%) plus daily rate (0.0082% per day, capped at 365 days / ~3.0%).
- **CET (Custo Efetivo Total):** Internal rate of return annualized, factoring in financed IOF and contractual fees.

## 5. Test Strategy

- **Financial Math Unit Tests:** Validate PMT, IOF, and CET against known financial tables and bank benchmark fixtures down to 2 decimal places.
- **Boundary / Edge Cases Tests:**
  - Zero, negative, and excessive loan amounts -> reject with informative message.
  - Term below minimum or above maximum allowed -> reject with informative message.
  - Modality not found -> validation error.
- **Margin Check Integration Test:** Verify that high installments relative to customer synthetic income flag `is_within_margin = False`.
- **Disclaimer Verification:** Assert that all returned payloads contain the non-negotiable simulation disclaimer.

## 6. Risks & Mitigations

- **Risk:** Precision and rounding errors accumulating over amortization terms.
  - **Mitigation:** Use `Decimal` for financial math internally, rounding to 2 decimal places (`ROUND_HALF_UP`) only at final presentation attributes.
- **Risk:** Hallucinated promises of approval by the LLM in conversational context.
  - **Mitigation:** Tool output explicitly separates numeric fields from the hardcoded disclaimer and margin warning, which the agent Validator (S14) verifies before answering.
