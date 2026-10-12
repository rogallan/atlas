# Architecture Decision Records (ADRs) — ATLAS Banking Copilot

This catalog contains the architectural decisions made during the design, implementation, and hardening of the ATLAS Banking GenAI Copilot (Q1–Q4). Every record follows the Michael Nygard ADR format.

---

## 📑 Master Index of Architectural Decisions

| ID | Title | Domain / Epics | Status | Date |
| :---: | :--- | :--- | :---: | :---: |
| [0001](file:///c:/Users/rogall/source/repos/atlas/8.docs/adr/0001-package-manager.md) | **Package and Dependency Manager Selection (uv)** | Foundation · S01 | Accepted | 2026-10-06 |
| [0002](file:///c:/Users/rogall/source/repos/atlas/8.docs/adr/0002-vector-store-and-embeddings.md) | **Local Vector Store (ChromaDB) and Local Embeddings (Ollama)** | RAG Ingestion · S06/S07 | Accepted | 2026-10-07 |
| [0003](file:///c:/Users/rogall/source/repos/atlas/8.docs/adr/0003-local-llm-runtime.md) | **Local-First Open LLM Runtime (Ollama with Qwen 2.5 7B)** | Foundation · S04 | Accepted | 2026-10-07 |
| [0004](file:///c:/Users/rogall/source/repos/atlas/8.docs/adr/0004-agent-orchestration-engine.md) | **Agent Orchestration Engine (LangGraph StateGraph)** | Multi-Agent · S14 | Accepted | 2026-10-08 |
| [0005](file:///c:/Users/rogall/source/repos/atlas/8.docs/adr/0005-mcp-tool-integration.md) | **Inter-Agent Tool Integration Standard (Model Context Protocol)** | Tools & MCP · S08–S13 | Accepted | 2026-10-09 |
| [0006](file:///c:/Users/rogall/source/repos/atlas/8.docs/adr/0006-web-framework-and-api.md) | **Web Framework and API Gateway (FastAPI with Pydantic v2)** | API Gateway · S03 | Accepted | 2026-10-09 |
| [0007](file:///c:/Users/rogall/source/repos/atlas/8.docs/adr/0007-hitl-approval-pattern.md) | **Human-in-the-Loop (HITL) Critical Action Approval Pattern** | Governance · S13/S14 | Accepted | 2026-10-10 |
| [0008](file:///c:/Users/rogall/source/repos/atlas/8.docs/adr/0008-defensive-guardrails.md) | **Defensive Security Guardrails (Dual-Layer Injection & PII Masking)** | Security · S18 | Accepted | 2026-10-10 |
| [0009](file:///c:/Users/rogall/source/repos/atlas/8.docs/adr/0009-observability-and-telemetry.md) | **Observability, Metrics, and Distributed Tracing Architecture** | Operations · S19 | Accepted | 2026-10-11 |
| [0010](file:///c:/Users/rogall/source/repos/atlas/8.docs/adr/0010-frontend-architecture.md) | **Frontend Architecture (Next.js 15, React 19, SSE Streaming)** | User Experience · S15 | Accepted | 2026-10-11 |
| [0011](file:///c:/Users/rogall/source/repos/atlas/8.docs/adr/0011-ngrok-tunneling.md) | **Ingress & Secure Tunneling via Ngrok Static Domain** | Networking · S16 | Accepted | 2026-10-11 |
| [0012](file:///c:/Users/rogall/source/repos/atlas/8.docs/adr/0012-aws-terraform-iac.md) | **Production Cloud Architecture & Terraform AWS IaC** | Infrastructure · S21 | Accepted | 2026-10-12 |

---

## 🏛️ Decision Lifecycle

- Any change to architectural principles defined in [`constitution.md`](file:///c:/Users/rogall/source/repos/atlas/constitution.md) must be proposed as a new ADR.
- ADRs are immutable once marked `Accepted`. Revisions or replacements create a new record that references and supersedes the predecessor.
