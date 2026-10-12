# ADR 0005: Inter-Agent Tool Integration Standard (Model Context Protocol - MCP)

## Status
Accepted

## Date
2026-10-09

## Context
Per `1.SDDs/S08` through `S13`, ATLAS requires integration with 6 specialized banking service capabilities:
1. Customer Repository (KYC, accounts, limits, transactions).
2. Loan Simulator (Price amortization, SAC tables, CET rates).
3. Insurance Simulator (Auto, Life, Residential quoting).
4. Consortium Simulator (Letter of credit, installments, bidding).
5. Tariff Catalog (BACEN Resolution 3.919 fee comparisons).
6. Support Ticket Management (Incident dispatch, SLA, audit logs).

Architectural challenge: Avoid tight coupling to proprietary ad-hoc tool interfaces and establish an open, standard protocol for AI tool exposition.

## Decision
Adopted the **Model Context Protocol (MCP)** specification:
1. **Domain Servers:** Designed 6 independent MCP Servers (`Customer`, `Loan`, `Insurance`, `Consortium`, `Tariff`, `Ticket`).
2. **Dual Transport Support:**
   - In-process / Standard I/O (stdio) transport for low-latency agent invocation and unit testing.
   - HTTP SSE / REST endpoints for distributed microservice scaling and standalone demonstration.
3. **Pydantic Tool Contracts:** Every tool is defined with typed parameters, clear descriptions, and deterministic validation.

## Consequences
- **Positive:**
  - Standardized tool discovery, schemas, and execution across all domains.
  - Pluggable architecture: Any MCP-compliant client can interact with ATLAS financial tools.
  - Complete decoupling between LLM orchestration and banking business logic.
- **Negative / Mitigations:**
  - Additional abstraction layer compared to direct Python function calls.
  - Mitigated by creating reusable in-memory server factories and unified test harnesses.
