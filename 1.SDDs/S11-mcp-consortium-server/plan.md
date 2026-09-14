# Plan — S11 · MCP Consortium Server

## 1. Approach

Implement the MCP Consortium Server under `src/mcp/consortium/`. The server provides structured catalog rules and deterministic quota calculation tools for Brazilian consortium modalities. It implements standard consortium accounting (Common Fund, Administration Fee, Reserve Fund, and Bid projections), validates input parameters via Pydantic, and returns formatted simulation payloads for the frontend (S15).

## 2. Architecture & Components

```
src/mcp/consortium/
├── __init__.py
├── server.py        # MCP Server entrypoint, transport & tool registrations
├── tools.py         # Handlers: list_consortium_modalities, get_consortium_group_rules, simulate_consortium
├── models.py        # Pydantic schemas (Modality, GroupRules, SimulationRequest, SimulationResult)
├── calculator.py    # Deterministic consortium math (quota installments, fee accruals, bid projections)
└── catalog.py       # In-memory catalog of synthetic consortium segments, allowed terms, fee rates
```

### Flow of Execution:
1. **Catalog Lookup:** The Agent Orchestrator (S14) queries `list_consortium_modalities` or `get_consortium_group_rules` to discover allowed credit ranges and fee percentages.
2. **Simulation Request:** `simulate_consortium(modality, credit_amount, term_months, embedded_bid_pct)` is invoked.
3. **Validation:** `models.py` and `catalog.py` verify that credit amount and term duration match valid group rules.
4. **Consortium Accounting:** `calculator.py` computes:
   - Monthly common fund share.
   - Monthly administrative fee share.
   - Monthly reserve fund share.
   - Bid impact (if a bid percentage is specified).
5. **Enrichment & Disclaimer:** Formats the complete fee breakdown, total nominal cost, effective total cost percentage, and attaches the mandatory disclaimer.
6. **Structured Output:** Emits the typed `ConsortiumSimulationResult` via MCP JSON-RPC.

## 3. Key Interfaces & Tool Schemas

```python
from enum import Enum
from pydantic import BaseModel, Field


class ConsortiumSegment(str, Enum):
  REAL_ESTATE = "real_estate"  # Imóvel
  AUTOMOTIVE = "automotive"  # Veículos / Automóveis
  SERVICES = "services"  # Serviços (Reformas, Festas, Viagens)


class GroupRulesInfo(BaseModel):
  segment: ConsortiumSegment
  display_name: str
  min_credit: float
  max_credit: float
  allowed_terms_months: list[int]
  total_admin_fee_pct: float  # e.g., 15.0%
  reserve_fund_pct: float  # e.g., 2.0%
  max_embedded_bid_pct: float  # e.g., 30.0%


class ConsortiumInstallmentBreakdown(BaseModel):
  common_fund_amount: float
  admin_fee_amount: float
  reserve_fund_amount: float
  monthly_total: float


class ConsortiumSimulationResult(BaseModel):
  segment: ConsortiumSegment
  credit_amount: float
  term_months: int
  installments: ConsortiumInstallmentBreakdown
  total_payable_amount: float
  total_fees_amount: float
  total_cost_percentage: float  # (total_payable / credit_amount - 1) * 100
  simulated_bid_amount: float | None = None
  post_bid_installment_estimate: float | None = None
  disclaimer: str = Field(
      default=(
          "Simulação de consórcio baseada em dados puramente sintéticos e"
          " regras fictícias. A contemplação depende exclusivamente de sorteio"
          " ou lance em assembleia e não é garantida em data específica."
      )
  )
```

```python
# Tool Signatures
def list_consortium_modalities() -> list[GroupRulesInfo]:
  ...


def get_consortium_group_rules(
    modality: ConsortiumSegment,
) -> GroupRulesInfo:
  ...


def simulate_consortium(
    modality: ConsortiumSegment = ConsortiumSegment.AUTOMOTIVE,
    credit_amount: float = 80000.0,
    term_months: int = 60,
    embedded_bid_pct: float = 0.0,
) -> ConsortiumSimulationResult:
  ...
```

## 4. Consortium Financial Formulas

- **Fundo Comum (FC):** $\frac{\text{Crédito}}{\text{Prazo}}$
- **Taxa de Administração (TA):** $\frac{\text{Crédito} \times \text{Taxa Adm \%}}{\text{Prazo}}$
- **Fundo de Reserva (FR):** $\frac{\text{Crédito} \times \text{Taxa Reserva \%}}{\text{Prazo}}$
- **Parcela Integral:** $FC + TA + FR$
- **Lance Embutido (Opcional):**
  $$\text{Valor do Lance} = \text{Crédito} \times \text{Bid \%}$$
  $$\text{Crédito Líquido Disponibilizado} = \text{Crédito} \times (1 - \text{Bid \%})$$
  $$\text{Saldo Devedor Restante amortizado pelo lance}$$

## 5. Test Strategy

- **Catalog Tests:** Verify segment boundaries, allowed terms, and fee configurations.
- **Consortium Math Unit Tests:** Verify installment breakdown, total fees, and percentage ratios against benchmark fixtures down to 2 decimal places.
- **Bid Simulation Tests:** Verify embedded and free bid calculations and installment reductions.
- **Boundary & Validation Tests:**
  - Credit amount below minimum or above maximum -> typed validation error.
  - Term not in allowed terms list -> error.
  - Bid percentage > max allowed -> error.
- **Disclaimer Verification:** Assert that 100% of simulation payloads contain the contemplation disclaimer.

## 6. Risks & Mitigations

- **Risk:** User assumes monthly installment is subject to compound interest like a loan.
  - **Mitigation:** Clear differentiation in output between consortium administrative fees and compound bank interest (CET), documented explicitly in response fields.
- **Risk:** Unrealistic expectation of immediate contemplation.
  - **Mitigation:** Hardcoded mandatory disclaimer asserting that contemplation is contingent upon assembly draws or bids.
