# Spec — S12 · MCP Tariff Server

> **Domain:** MCP · **Quarter:** Q2 · **Depends on:** S01 (Python Toolchain), S06/S07 (RAG Knowledge)

## 1. Goal

Implement a typed Model Context Protocol (MCP) server providing standardized lookups of banking fee tables (tabela de tarifas), essential service packages (serviços essenciais), and account maintenance pricing, ensuring consistent, structured tariff data when unstructured RAG alone is insufficient or prone to numerical ambiguity.

## 2. Context

Per `architecture.md`, `constitution.md` (Principle 4: "Evidence before claims"), and the PDI operation map ("Consulta de tarifas: RAG / MCP"), relationship managers and customers frequently ask about exact tariff amounts, free monthly quota limits (e.g. BACEN Resolution 3.919 essential services: 4 withdrawals, 2 transfers, 2 statements), and package exemptions based on customer relationship level. While RAG (S06/S07) retrieves long-form Central Bank resolutions and textual fee rules, the Tariff Server acts as the authoritative structured table of record for exact currency amounts, package comparisons, and waiver rules, synchronized with current documentary regulations.

## 3. In scope

- MCP Server conforming to the Model Context Protocol specification.
- Typed tariff lookup & comparison tools:
  - `get_service_fee(service_code: str)`: Returns current unit price, channel breakdown (branch counter vs. ATM vs. Internet banking), and applicable BACEN regulatory ceilings.
  - `list_tariff_packages()`: Lists account packages (Essential/Free, Classic, Premium, Private) and their monthly fees.
  - `check_essential_services_quota(service_type: str, used_count: int)`: Validates whether a transaction is within the mandatory free monthly quota established by Central Bank regulation.
  - `compare_packages(customer_segment: str | None = None)`: Compares package costs and highlights fee waiver rules based on investment/relationship thresholds.
- Input validation (valid service codes, valid package names, valid transaction channels).
- Traceable synchronization metadata (effective date, regulatory reference norm).
- Contract tests verifying consistency between MCP tariff outputs and RAG regulatory documents.

## 4. Out of scope

- Real fee debiting, billing processing, or financial transaction charging.
- Full text regulatory search of Central Bank resolutions (handled in S07 RAG Retrieval).
- Product financing or interest rate calculations (handled in S09 MCP Loan Server).

## 5. Requirements

- **R1. MCP Compliance:** Expose tools following standard MCP JSON-RPC protocol over stdio / local HTTP SSE transport.
- **R2. Structured Tariff Catalog:** Maintain a structured table of fee items (e.g., TED/DOC/Pix, extra withdrawals, physical statements, card reissue) conforming to Central Bank Resolution 3.919 taxonomy.
- **R3. Essential Services Package Guarantee:** Explicitly represent the zero-cost essential services package mandated by BACEN regulation, including exact monthly quota allowances.
- **R4. Channel Differentiation:** Support differentiating fee values by service channel (e.g., self-service/digital vs. assisted branch counter).
- **R5. Traceability & Sync Metadata:** Every tariff record must indicate its `effective_date`, `version`, and `regulatory_basis` (e.g., "Resolução CMN nº 3.919/2010").
- **R6. Consistency with RAG:** Provide deterministic schemas designed to cross-verify against RAG document excerpts so that the copilot avoids contradictions when responding to fee queries.

## 6. Acceptance criteria

- MCP Tariff Server advertises `get_service_fee`, `list_tariff_packages`, `check_essential_services_quota`, and `compare_packages` with complete JSON schemas.
- Lookups for mandatory essential services (saques, extratos, transferências) return exact zero-cost quotas conforming to BACEN rules.
- Invalid service codes or unrecognized channels trigger structured validation errors.
- 100% of tariff outputs contain traceability metadata with effective date and regulatory basis.
- Integration tests confirm tariff figures match the corresponding values in Central Bank reference documents.
