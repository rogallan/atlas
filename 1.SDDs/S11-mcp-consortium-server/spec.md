# Spec — S11 · MCP Consortium Server

> **Domain:** MCP · **Quarter:** Q2 · **Depends on:** S01 (Python Toolchain), S02 (Synthetic Customer Base), S08 (MCP Customer Server)

## 1. Goal

Implement a typed Model Context Protocol (MCP) server providing consortium (consórcio) modality exploration, group quota rules, and hypothetical letter-of-credit (carta de crédito) installment simulations, calculating administrative fees, reserve fund rates, and bid (lance) scenarios deterministically without making binding claims.

## 2. Context

Per `architecture.md`, `constitution.md` (Principles 3 & 4: "Explicit tools" and "Evidence before claims") and the PDI operation map ("Consórcio: MCP + RAG"), consortiums represent a popular financial planning alternative in Brazilian banking (automotive, real estate, services, heavy equipment). The Consortium Server models group rules, administration fee rates (taxa de administração), reserve funds (fundo de reserva), and installment formulas, enabling relationship managers to simulate quotas and bid strategies for synthetic clients without misrepresenting simulations as guaranteed contemplations.

## 3. In scope

- MCP Server conforming to the Model Context Protocol specification.
- Typed catalog & simulation tools:
  - `list_consortium_modalities()`: Lists available segments (Real Estate / Imóvel, Auto / Veículos, Services / Serviços).
  - `get_consortium_group_rules(modality: str)`: Returns group terms (duration in months, administrative fee total and monthly percentage, reserve fund percentage, assembly frequency).
  - `simulate_consortium(modality: str, credit_amount: float, term_months: int, embedded_bid_pct: float | None = 0.0)`: Calculates monthly installments (common fund + admin fee + reserve fund), total cost, and estimated bid impact on tenure/installment reduction.
- Input validation (boundaries for credit amounts, term durations, and valid modalities).
- Mandatory simulation disclaimer and transparent breakdown of fee components.
- Contract tests verifying consortium math, fee accumulation, and schema compliance.

## 4. Out of scope

- Real quota allocation, consortium group assembly execution, or actual lottery draw/contemplation.
- Direct credit financing or loan math with compound interest (handled in S09 MCP Loan Server).
- State mutation (purchasing a quota or debiting installments).

## 5. Requirements

- **R1. MCP Compliance:** Expose tools following standard MCP JSON-RPC protocol over stdio / local HTTP SSE transport.
- **R2. Deterministic Consortium Calculation:** Calculations must follow standard Brazilian consortium group financial formulas:
  - Common Fund (Fundo Comum): $\frac{\text{Credit Amount}}{\text{Term Months}}$
  - Administration Fee (Taxa de Administração): $\frac{\text{Credit Amount} \times \text{Admin Fee \%}}{\text{Term Months}}$
  - Reserve Fund (Fundo de Reserva): $\frac{\text{Credit Amount} \times \text{Reserve \%}}{\text{Term Months}}$
  - Total Monthly Installment: $\text{Fundo Comum} + \text{Taxa Adm} + \text{Fundo Reserva}$
- **R3. Input Range Validation:** Validate that `credit_amount` falls within the modality bounds (e.g., Auto R$ 30k–R$ 200k, Real Estate R$ 150k–R$ 1.5M), `term_months` matches group terms, and `embedded_bid_pct` does not exceed maximum allowable bid limit (e.g. 30%).
- **R4. Bid (Lance) Simulation:** Support simulating free bid (lance livre) or embedded bid (lance embutido), showing how the bid reduces the installment value or the remaining term.
- **R5. Mandatory Hypothetical Disclaimer:** Every simulation response must state: *"Simulação de consórcio baseada em dados puramente sintéticos e regras fictícias. A contemplação depende exclusivamente de sorteio ou lance em assembleia e não é garantida em data específica."*
- **R6. Transparent Fee Breakdown:** Detailed itemization of common fund, administration fee, reserve fund, and total cost of the quota.

## 6. Acceptance criteria

- MCP Consortium Server advertises `list_consortium_modalities`, `get_consortium_group_rules`, and `simulate_consortium` with complete JSON schemas.
- Installment and fee calculations produce exact values matching benchmark consortium group fixtures.
- Out-of-bounds parameters (e.g. credit below minimum, invalid term) return structured validation errors.
- 100% of simulation outputs contain the non-binding contemplation disclaimer and transparent fee breakdown.
- No response implies or guarantees a specific date or period for contemplation.
