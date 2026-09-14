# Spec — S09 · MCP Loan Server

> **Domain:** MCP · **Quarter:** Q2 · **Depends on:** S01 (Python Toolchain), S02 (Synthetic Customer Base), S08 (MCP Customer Server)

## 1. Goal

Implement a typed Model Context Protocol (MCP) server providing loan simulation and eligibility estimation tools based on explicit parameters and synthetic financial rules, ensuring transparent financial calculation assumptions while strictly preventing false claims of real credit approval or contracting.

## 2. Context

Per `architecture.md` and `constitution.md` (Principles 3 & 4: "Explicit tools" and "Evidence before claims", plus non-negotiable principle "100% synthetic data / never real operations"), relationship managers need to simulate credit scenarios (e.g., Personal Loan / CDC, Payroll-Deductible Loan / Consignado) for fictitious clients. The Loan Server isolates the financial math, interest rate bands, and installment projections behind typed MCP tools, returning transparent disclosures and explicitly labeling results as hypothetical simulations.

## 3. In scope

- MCP Server conforming to the Model Context Protocol specification.
- Typed simulation tools:
  - `simulate_loan(customer_id: str, amount: float, term_months: int, modality: str)`: Computes monthly installment, total interest, effective annual rate (CET - Custo Efetivo Total), and amortization schedule summary using standard financial formulas (e.g., Price table).
  - `get_loan_modalities()`: Returns available credit modalities, allowed ranges (min/max amount, min/max term), and benchmark interest rates.
  - `check_loan_pre_conditions(customer_id: str, amount: float, installment: float)`: Evaluates synthetic debt-to-income (comprometimento de renda) limits based on the customer's synthetic profile.
- Input validation (boundaries for loan amounts, terms, and valid modalities).
- Mandatory simulation disclaimer and transparent parameter breakdown in every output.
- Contract tests verifying financial math, boundary conditions, and schema compliance.

## 4. Out of scope

- Real credit underwriting, credit bureau bureau calls (e.g. Serasa), or legal contracting.
- State mutation (creating live loans, debiting funds, or disbursing capital).
- Other product simulations (insurance, consortium, tariffs) — covered in S10, S11, and S12.
- Final ticket or application submission — covered in S13 MCP Ticket Server.

## 5. Requirements

- **R1. MCP Compliance:** Expose tools following the standard MCP JSON-RPC protocol over stdio / local HTTP SSE transport.
- **R2. Deterministic Financial Computation:** Calculations (installment, total interest, CET) must use standardized financial formulas (e.g., French Amortization / Tabela Price) yielding deterministic outputs for given inputs.
- **R3. Input Range Validation:** Validate that `amount > 0`, `term_months` falls within modality boundaries (e.g., 6 to 72 months), and `modality` is supported. Reject invalid ranges with informative typed errors.
- **R4. Synthetic Customer Context:** When `customer_id` is supplied, fetch the customer's synthetic monthly income from S02/S08 to verify that the proposed installment does not exceed synthetic regulatory debt-to-income limits (e.g. 30% or 35% for consignado).
- **R5. Mandatory Hypothetical Disclaimer:** Every response payload must include an explicit disclaimer: *"Simulação baseada em dados puramente sintéticos e regras fictícias. Não constitui aprovação ou oferta vinculante de crédito."*
- **R6. Detailed Premise Breakdown:** Provide transparent breakdown of calculation premises (monthly interest rate, annual CET, IOF estimate, total amount payable).

## 6. Acceptance criteria

- MCP Loan Server advertises `simulate_loan`, `get_loan_modalities`, and `check_loan_pre_conditions` with complete Pydantic/JSON schemas.
- Financial calculation test cases match verified amortization benchmark values to the cent.
- Out-of-bounds requests (e.g., negative amount, term > max_term) return structured validation errors.
- 100% of simulation responses contain the mandatory hypothetical disclaimer and premise breakdown.
- No response suggests or implies actual credit disbursement.
