# Plan — S10 · MCP Insurance Server

## 1. Approach

Implement the MCP Insurance Server under `src/mcp/insurance/`. The server provides structured catalog inspection and deterministic premium simulations. It decouples legal terms and regulatory conditions (which can be reinforced by RAG in S07) from numerical quotes and actuarial matrices, enforcing strict validation via Pydantic and returning structured cards for the frontend (S15).

## 2. Architecture & Components

```
src/mcp/insurance/
├── __init__.py
├── server.py        # MCP Server entrypoint, transport & tool registrations
├── tools.py         # Handlers: list_insurance_products, get_coverage_details, simulate_insurance_quote
├── models.py        # Pydantic schemas (Product, Coverage, QuoteRequest, QuoteResult)
├── calculator.py    # Actuarial math engine (premium rates, age factors, IOF computation)
└── catalog.py       # In-memory catalog of synthetic insurance products, coverages, limits
```

### Flow of Execution:
1. **Catalog Lookup:** The Agent Orchestrator (S14) queries `list_insurance_products` or `get_coverage_details` to present available options to the relationship manager.
2. **Quote Simulation Request:** `simulate_insurance_quote(customer_id, product_id, insured_capital, optional_coverages)` is invoked.
3. **Validation:** `models.py` and `catalog.py` verify that the product exists, the insured capital is within acceptable bounds, and optional coverages are valid.
4. **Customer Profile Inspection (Optional):** If `customer_id` is passed, synthetic profile data (e.g. age group, segment) is fetched from S02/S08 to determine applicable risk multipliers.
5. **Premium Calculation:** `calculator.py` applies baseline rates per coverage, adjusts for customer risk factor, and adds insurance IOF (typically 0.38% or 7.38% depending on modality).
6. **Disclaimer & Output Formatting:** Bundles itemized coverage limits, deductibles, premium breakdown, and the mandatory non-binding disclaimer into a typed response.

## 3. Key Interfaces & Tool Schemas

```python
from enum import Enum
from pydantic import BaseModel, Field


class InsuranceCategory(str, Enum):
  LIFE = "life"  # Seguro de Vida
  HOME = "home"  # Seguro Residencial
  CREDIT_LIFE = "credit_life"  # Prestamista
  CARD_PROTECTION = "card_protection"  # Proteção de Cartão e Conta


class CoverageItem(BaseModel):
  code: str
  name: str
  description: str
  is_mandatory: bool
  max_indemnity_limit: float
  deductible_info: str | None = None  # Franquia


class InsuranceProductInfo(BaseModel):
  product_id: str
  name: str
  category: InsuranceCategory
  min_capital: float
  max_capital: float
  available_coverages: list[CoverageItem]
  description: str


class InsuranceQuoteResult(BaseModel):
  customer_id: str | None
  product_id: str
  product_name: str
  insured_capital: float
  included_coverages: list[CoverageItem]
  monthly_premium: float
  annual_premium: float
  estimated_iof: float
  underwriting_premises: dict[str, str] = Field(default_factory=dict)
  disclaimer: str = Field(
      default=(
          "Cotação de seguro baseada em dados puramente sintéticos e regras"
          " fictícias. Não constitui proposta vinculante ou emissão de apólice."
      )
  )
```

```python
# Tool Signatures
def list_insurance_products() -> list[InsuranceProductInfo]:
  ...


def get_coverage_details(product_id: str) -> list[CoverageItem]:
  ...


def simulate_insurance_quote(
    customer_id: str | None = None,
    product_id: str = "life_basic",
    insured_capital: float = 100000.0,
    optional_coverages: list[str] | None = None,
) -> InsuranceQuoteResult:
  ...
```

## 4. Actuarial Calculation Rules

- **Base Premium Calculation:**
  $$\text{Base Premium} = \sum_{\text{coverage} \in \text{selected}} (\text{Capital} \times \text{Rate}_{\text{coverage}})$$
- **Customer Risk Adjustment:** Adjusted by age/segment factor (e.g., 20-35 years: 1.0x; 36-50: 1.25x; 51+: 1.6x).
- **Taxes (IOF):** Added to gross premium (e.g., standard IOF applied deterministically).
- **Annual Premium:** $\text{Monthly Premium} \times 12$ with optional synthetic discount factor (e.g. 5% discount for annual upfront).

## 5. Test Strategy

- **Catalog Tests:** Verify product definitions, mandatory vs. optional coverage rules, and capital boundaries.
- **Actuarial Math Unit Tests:** Verify premium outputs against deterministic benchmark fixtures down to the cent.
- **Boundary & Validation Tests:**
  - Capital below minimum or above maximum -> typed validation error.
  - Invalid product ID or non-existent coverage codes -> error.
- **Disclaimer Verification:** Assert that 100% of quote outputs include the non-binding disclaimer and premise breakdown.

## 6. Risks & Mitigations

- **Risk:** Confusion between legal terms (exclusions, grace periods) and calculation values.
  - **Mitigation:** Clear separation of concerns: tool outputs structured numeric coverage limits; detailed legal definitions defer to or integrate with RAG (S07) when asked.
- **Risk:** Unrealistic premium calculations for extreme capital amounts.
  - **Mitigation:** Enforce strict upper and lower limits on `insured_capital` in `catalog.py`.
