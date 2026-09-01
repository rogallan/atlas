# Constitution — ATLAS · Banking GenAI Copilot

> **Status:** Approved · **Phase:** S00 · **Quarter:** Q1
> **Repository:** https://github.com/rogallan/atlas
> **PDI owner:** to be filled in · **Mentor:** to be filled in

## 1. Project purpose

ATLAS is the anchor project of the Software Engineer (GenAI specialization) Individual Development
Plan. It builds a **conversational copilot for a bank relationship manager**, capable of:

- consulting **public knowledge from the Central Bank** (RAG over documents);
- consulting a **fictitious customer/financial history database** (100% synthetic data);
- executing **simple simulated operations** (loan, insurance, consortium, tariffs, ticket) through
  controlled tools (MCP), never real operations.

The project is developed **locally**, with the LLM served via **Ollama**, and has a path to cloud
publishing/infrastructure (Vercel for the frontend, Terraform as an AWS alternative for the
backend).

## 2. Principles (non-negotiable)

1. **Local-first.** The development environment runs locally (Ollama, FastAPI, MCP, Vector
   Store/DB). No cloud dependency is required to develop or evaluate the project.
2. **Security by default.** Every state-changing action (e.g., opening a ticket) requires explicit
   human confirmation before execution. Authorization, least privilege, and auditing are part of
   the design, not an afterthought.
3. **Explicit tools.** The agent never "guesses" an operation — it only executes what is modeled as
   a tool (MCP) or a RAG query, with validated input/output schemas.
4. **Evidence before claims.** No response from the copilot may present something as fact without
   documentary grounding (RAG) or without coming from a deterministic tool (MCP). Absence of
   evidence is handled explicitly — the agent says it doesn't know rather than inventing an answer.
5. **Tests before release.** No phase of the SDD catalog is considered complete without tests
   (unit, contract, integration, or evaluation) that prove the behavior described in its spec.
6. **100% synthetic data.** No real customer, account, or financial history data is used at any
   stage of the project — generation, testing, demos, or publishing. No exceptions.

## 3. Scope and out-of-scope

**In scope:**
- Natural-language conversation about public knowledge (Central Bank).
- Querying synthetic customer/history data via MCP.
- Fictitious simulations (loan, insurance, consortium, tariffs) with explicit parameters.
- Simulated actions with human confirmation (e.g., opening a fictitious ticket).
- Observability, security, evaluation (harness/evals), and frontend publishing.

**Out of scope:**
- Any real credit approval, contracting, or financial operation.
- Use of real customer or third-party data.
- Actions that modify third-party production systems.

## 4. Cross-cutting acceptance criteria

- **Evidence before claims:** every RAG-based response cites its source; every MCP-based response
  references the tool and the parameters used.
- **Tests before release:** each item in the SDD catalog (S00–S22) is only marked complete once
  tests/evaluations prove out its corresponding `spec.md`.
- **Human-in-the-loop:** no action (a state-changing tool) is executed without the user's explicit
  confirmation.

## 5. Governance and versioning

- This document and its companion `architecture.md` are the foundation for all SDD specifications
  (S00 → S22) in the PDI catalog.
- Changes to principles require validation with the mentor and a new version of this file
  (preserving history via the repository's version control).
- `constitution.md` lives under `SDDs/S00-constitution/`, per the proposed project structure.

## 6. References

- Repository: https://github.com/rogallan/atlas
- Blog: https://rogerallantex.blogspot.com/
- YouTube: https://www.youtube.com/@rogallany
- Companion document: `architecture.md` (technical boundaries and solution design)
