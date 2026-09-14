# Spec — S10 · MCP Insurance Server

> **Domain:** MCP · **Quarter:** Q2 · **Depends on:** S01 (Python Toolchain), S02 (Synthetic Customer Base), S08 (MCP Customer Server)

## 1. Goal

Implement a typed Model Context Protocol (MCP) server providing insurance product catalog exploration, coverage rules lookup, and hypothetical premium quote simulations based on explicit parameters and synthetic underwriting tables, cleanly separating documentary facts (coverage terms) from actuarial calculation rules.

## 2. Context

Per `architecture.md`, `constitution.md` (Principles 3 & 4: "Explicit tools" and "Evidence before claims") and the PDI operation map ("Seguro: MCP + RAG"), insurance assistance requires combining factual coverage definitions (what is insured, exclusions, grace periods) with deterministic quote simulations (monthly/annual premium based on insured capital and synthetic customer risk profile). The Insurance Server encapsulates product rules, coverage matrices, and premium calculations behind strictly typed MCP tools.

## 3. In scope

- MCP Server conforming to the Model Context Protocol specification.
- Typed catalog & simulation tools:
  - `list_insurance_products()`: Lists available synthetic insurance modalities (e.g. Life, Home, Credit Life / Prestamista, Card Protection).
  - `get_coverage_details(product_id: str)`: Returns specific coverage items, indemnity limits, basic exclusions, and deductible details.
  - `simulate_insurance_quote(customer_id: str | None, product_id: str, insured_capital: float, optional_coverages: list[str])`: Computes monthly/annual premium, tax (IOF), coverage breakdown, and underwriting assumptions.
- Input validation (boundaries for insured capital, valid coverage codes, valid product types).
- Mandatory simulation disclaimer and transparent breakdown of coverage limits and deductibles.
- Contract tests verifying quote math, boundary conditions, and schema compliance.

## 4. Out of scope

- Real policy issuance, binding insurance contracts, or integration with SUSEP/real insurers.
- Direct credit or loan calculations (handled in S09 MCP Loan Server).
- Consortium simulations (handled in S11 MCP Consortium Server).
- State mutation (creating live policies or charging premiums).

## 5. Requirements

- **R1. MCP Compliance:** Expose tools following standard MCP JSON-RPC protocol over stdio / local HTTP SSE transport.
- **R2. Separation of Concerns (RAG vs Tool):** Provide structured data on product parameters and calculations. Detailed legal wording or regulatory general conditions can link to or be augmented by RAG (S07), while calculations remain 100% deterministic inside the tool.
- **R3. Deterministic Premium Computation:** Premiums must be calculated from deterministic actuarial tables based on product type, insured capital, selected coverages, and (when provided) synthetic customer age/segment from S02/S08.
- **R4. Input Range Validation:** Validate that `insured_capital` falls within product boundaries (e.g., Life min R$ 10.000 / max R$ 1.000.000) and that selected coverages exist in the catalog.
- **R5. Mandatory Hypothetical Disclaimer:** Every quote response must state: *"Cotação de seguro baseada em dados puramente sintéticos e regras fictícias. Não constitui proposta vinculante ou emissão de apólice."*
- **R6. Transparent Coverage Breakdown:** The simulation output must itemize each included coverage, individual insured amounts, deductible rules (franquias), and total premium with IOF.

## 6. Acceptance criteria

- MCP Insurance Server advertises `list_insurance_products`, `get_coverage_details`, and `simulate_insurance_quote` with complete JSON schemas.
- Premium calculations produce consistent, deterministic values matching actuarial benchmark fixtures.
- Out-of-bounds parameters (e.g. capital outside limits, invalid coverage codes) trigger typed validation errors.
- 100% of quote responses contain the mandatory hypothetical disclaimer and coverage breakdown.
- No response suggests actual policy binding or underwriting approval.
