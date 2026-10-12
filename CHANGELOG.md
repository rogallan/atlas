# Changelog — ATLAS Banking GenAI Copilot

All notable changes to the ATLAS Banking GenAI Copilot project are documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and follows the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) standard.

---

## [1.0.0] - 2026-10-12

### Milestone: Full Production Release Candidate (Q1–Q4 Culmination)
Culmination of the Senior GenAI Software Engineer Individual Development Plan (PDI). All 23 Software Design Documents (S00 to S22) are implemented, verified, and signed off.

### Added
- **S22 — Release Governance & Technical Portfolio:**
  - Automated release readiness and Definition of Done auditor (`6.ops/release/release_checklist.py`).
  - Git history security clearance and synthetic customer compliance scanner (`6.ops/release/security_audit.sh` & `security_audit.py`).
  - Executive benchmark scorecard report (`7.evals/reports/final_scorecard_v1.0.0.md`).
  - Complete master catalog of 12 Architecture Decision Records (`8.docs/adr/ADR-0001` to `ADR-0012`).
  - 10-minute interactive live demonstration script (`8.docs/portfolio/demo_script.md`).
  - 20-episode video curriculum syllabus (`8.docs/portfolio/video_curriculum.md`).
  - Technical portfolio showcase summary (`8.docs/portfolio/README.md`).
- **S21 — Terraform AWS Cloud Infrastructure:**
  - Modular Terraform suite (`network`, `compute`, `data`, `security_iam`, `observability`).
  - Architectural equivalence mapping Local-First $\leftrightarrow$ AWS (`infra/terraform/MAPPING.md`).
  - Monthly engineering cost estimate model (`docs/architecture/aws_cost_estimate.md`).
  - Automated IaC test suite (`4.tests/unit/test_terraform_aws.py`).
- **S20 — Containerized Local Development Stack:**
  - Multi-stage non-root `Dockerfile` with wheel caching and uv layer separation.
  - Production-ready `docker-compose.yml` orchestrating API Gateway, ChromaDB, and health checks.
- **S19 — Observability & Token Cost Accounting:**
  - Prometheus metrics exporter (`/metrics`) tracking HTTP throughput, latency histograms, and agent stage durations.
  - Real-time token consumption and USD cost estimation store (`TokenAccountingStore`).
  - Machine-parsable structured JSON logging with ISO-8601 timestamps and automatic PII masking.
- **S18 — Dual-Layer Defensive Security Guardrails:**
  - Input guardrail rejecting prompt injections, jailbreaks, and system prompt extraction.
  - Output guardrail performing deterministic regex masking of Brazilian CPFs and account numbers.
  - Cross-tenant session context isolation preventing unauthorized customer data access.
- **S17 — Evaluation Harness & Quality Gates:**
  - Regression evaluation harness runner (`evals.runner`) asserting RAG Groundedness, Context Recall, Intent Accuracy, and Safety compliance against golden datasets.
- **S16 — Ingress & Tunneling Integration:**
  - Automated Ngrok static domain tunnel (`scripts/start_tunnel.py`) enabling secure HTTPS edge communication between Vercel and local Uvicorn.
  - Automated preflight smoke tests validating SSL handshake and CORS headers.
- **S15 — Next.js 15 Streaming Chat Frontend:**
  - Modern web application with React 19, Tailwind CSS, and Server-Sent Events (SSE) token streaming.
  - Interactive financial widgets: amortization tables, consortium letter sliders, and HITL approval cards.
- **S14 — Multi-Agent Orchestration Engine:**
  - Cyclical state machine implemented via LangGraph `StateGraph`.
  - Cryptographically signed Human-in-the-Loop (HITL) approval pattern for high-impact actions.
- **S08–S13 — Model Context Protocol (MCP) Financial Tool Suite:**
  - 6 independent MCP servers: Customer Repository, Loan Simulator (Price & SAC), Insurance Quoter, Consortium Calculator, Tariff Comparison (BACEN Res. 3.919), and Support Tickets.
- **S06–S07 — Regulatory RAG Pipeline:**
  - Hierarchical chunking preserving legal article boundaries over BACEN & CMN normative documents.
  - Vector search powered by local ChromaDB and `nomic-embed-text` embeddings with strict citation badges.
- **S05 — Semantic Intent Router:**
  - Five-class intent classifier (`knowledge`, `simulation`, `action`, `clarification`, `out_of_domain`) with entity extraction.
- **S04 — Open-Weights LLM Runtime:**
  - Ollama integration serving `Qwen 2.5 7B Instruct` with asynchronous client and CI test mocks.
- **S03 — ASGI API Gateway:**
  - FastAPI gateway with Pydantic v2 schemas, correlation ID propagation, and OpenAPI documentation.
- **S02 — Synthetic Banking Data Generator:**
  - 100% synthetic customer base generator producing deterministic profiles, credit scores, and transactions.
- **S01 — Python Toolchain:**
  - Modern toolchain configured with `uv`, `ruff`, `mypy`, and `pytest`.
- **S00 — Constitution & Architectural Charter:**
  - Foundational principles: Local-First, Security by Default, Explicit Tools, Evidence Before Claims.

---

## Quality Gate Summary (v1.0.0)

| Quality Gate | Metric / Target | Result | Status |
| :--- | :---: | :---: | :---: |
| **Test Suite Pass Rate** | 100% (299 tests) | 299 passed, 0 failed | ✅ PASS |
| **Code Coverage** | $\ge 70.0\%$ | **84.57%** | ✅ PASS |
| **Intent Classification** | $\ge 90.0\%$ | **96.0%** | ✅ PASS |
| **RAG Context Recall** | $\ge 85.0\%$ | **100.0%** | ✅ PASS |
| **Groundedness / Faithfulness** | $\ge 90.0\%$ | **100.0%** | ✅ PASS |
| **Safety / HITL Compliance** | $100.0\%$ | **100.0%** | ✅ PASS |
| **Security Leak Clearance** | 0 secrets / 100% synthetic | 0 leaks detected | ✅ PASS |
| **Terraform IaC Validation** | Valid syntax / clean plan | 40 resources to add | ✅ PASS |
