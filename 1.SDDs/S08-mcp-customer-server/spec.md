# Spec — S08 · MCP Customer Server

> **Domain:** MCP · **Quarter:** Q2 · **Depends on:** S01 (Python Toolchain), S02 (Synthetic Customer Base)

## 1. Goal

Build a typed Model Context Protocol (MCP) server providing read-only tools to query synthetic customer profiles, financial history, account balances, and relationship indicators, enforcing strict input/output validation, simulated authorization, and audit logging.

## 2. Context

Per `architecture.md` and `constitution.md` (Principles 3 & 6: "Explicit tools" and "100% synthetic data"), the copilot accesses client data strictly through decoupled, typed MCP servers querying the synthetic database generated in S02. The Customer Server is the authoritative provider of customer context (income, segment, relationship tenure, active contracts, and recent financial transactions) enabling the copilot to inform relationship managers without exposing raw database credentials or mixing business queries directly into the LLM context.

## 3. In scope

- MCP Server implementation conforming to the Model Context Protocol specification.
- Typed read-only tools:
  - `get_customer_profile(customer_id: str)`: Returns personal info, income bracket, customer segment, and relationship score.
  - `get_customer_accounts(customer_id: str)`: Returns accounts, branches, balances, and status.
  - `get_financial_history(customer_id: str, limit: int = 10)`: Returns synthetic chronological financial events and payment history.
  - `get_customer_summary(customer_id: str)`: Aggregated view combining profile, active products, and relationship indicators for briefing the manager.
- Pydantic models validating all tool inputs and outputs.
- Simulated authorization and scope checking (e.g. role-based access for relationship managers).
- Structured audit logging capturing customer lookups (caller identity, timestamp, queried customer ID, tool name).
- Contract tests verifying tool schemas and boundary edge cases.

## 4. Out of scope

- Direct database mutation or state changes (creating accounts, modifying balances) — this server is strictly read-only.
- Simulation of new products (loans, insurance, consortium) — covered in specialized MCP servers S09, S10, and S11.
- State-changing action execution (e.g. opening tickets) — covered in S13 MCP Ticket Server.
- Use of or connection to real banking databases or real PII.

## 5. Requirements

- **R1. MCP Compliance:** Expose tools following standard MCP JSON-RPC protocol over stdio / local HTTP SSE transport.
- **R2. Synthetic Grounding:** Query exclusively against the synthetic customer database defined and seeded in S02.
- **R3. Input Validation & Error Handling:** Validate input schemas (e.g. `customer_id` format). Unknown or non-existent IDs must return a clean, typed error response rather than crashing or returning arbitrary defaults.
- **R4. Output Schemas:** Every tool response must conform to strict Pydantic schemas hiding internal database primary keys or non-pertinent storage fields.
- **R5. Simulated Authorization:** Enforce simulated manager credentials/role check before returning sensitive customer records.
- **R6. Audit Logging:** Log every query invocation with a correlation ID, operator identity, target customer ID, and accessed fields.

## 6. Acceptance criteria

- MCP Customer Server boots successfully and advertises its tools (`get_customer_profile`, `get_customer_accounts`, `get_financial_history`, `get_customer_summary`) with valid JSON schemas.
- Contract tests verify that valid customer queries return accurate synthetic data matching the S02 seed.
- Non-existent customer IDs return a structured `CustomerNotFound` error.
- All query events generate structured audit log entries without leaking synthetic PII to standard error.
