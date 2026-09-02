# S00 — Constitution + Architecture

Quarter: Q1 · Category: Project foundation
Deliverable: `constitution.md` + `architecture.md`

## 1. Goal

Establish, before any product code is written, the non-negotiable principles and
the architectural boundaries that will govern every technical decision in ATLAS
throughout the four quarters. This item is the foundation of the entire SDD
pattern: no other item in the catalog (S01 → S22) may conflict with what is
defined here.

## 2. Context

ATLAS is a conversational copilot for a bank relationship manager that:
- consults public knowledge from the Central Bank via RAG;
- consults a fictitious customer/financial-history database via MCP;
- executes simple **simulated** operations (never real ones) through controlled
  tools.

Because it touches a sensitive domain (banking) even with synthetic data, and
because it uses LLMs with tool calling, the project needs explicit security,
verification, and quality principles from the very first commit.

## 3. Scope

This item covers exclusively the creation of two foundational documents:

1. **`constitution.md`** — the project's principles, non-negotiable, that any
   future spec/plan/tasks must respect.
2. **`architecture.md`** — a map of the boundaries between the system's modules
   (Front / API / Agent / MCP / RAG / Infra), with the responsibilities and the
   communication contracts between them.

## 4. Out of scope

- Implementation of any product code (that starts at S01+).
- Low-level decisions about specific libraries/frameworks (those live in the
  ADRs of each item, e.g., S06 decides the Vector DB, S04 decides the Ollama
  integration).
- Detailed definition of business operations (that lives in S02 and in the
  IDP's "Operations Map" section).

## 5. Candidate principles (to be drafted in constitution.md)

- **Local-first**: development runs entirely locally (Ollama, containers,
  Vector DB/Store, MCP); the cloud is an alternative path, not a day-to-day
  dependency.
- **Security by default**: no sensitive action is executed without validation
  and, when applicable, human confirmation (human-in-the-loop).
- **Explicit tools**: the agent never improvises a capability; every action
  goes through a typed, auditable tool/MCP.
- **Evidence before claims**: knowledge-based (RAG) responses are only given
  with a traceable citation; in the absence of evidence, the agent admits it
  doesn't know instead of making something up.
- **Tests before release**: no feature is considered "done" (Definition of
  Done) without automated tests and, when applicable, passing evals.
- **Fictitious data, always**: no real customer data is used at any layer of
  the project, including in documentation and published videos.

## 6. Acceptance criteria

- [ ] `constitution.md` versioned at the repository root, with the principles
      above drafted and validated.
- [ ] `architecture.md` documenting the Front/API/Agent/MCP/RAG/Infra
      boundaries, including a textual diagram and the responsibility contract
      of each module.
- [ ] Both documents reviewed with the IDP mentor.
- [ ] No decision in S01+ may contradict what is defined here without opening
      an ADR explaining the exception.
