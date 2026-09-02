# S00 — Constitution + Architecture · Technical Plan

## 1. Approach

This item doesn't produce code; it produces two decision artifacts that serve
as a reference for the rest of the project. The plan is to draft, review, and
version both documents in a single short iteration, before starting S01.

## 2. Structure of `constitution.md`

```
constitution.md
├── Purpose of the document
├── Principles (local-first, security by default, explicit tools,
│                evidence before claims, tests before release,
│                fictitious data always)
├── How to use this document (every spec.md should reference it when relevant)
└── Change process (how a principle can be revised — via ADR)
```

## 3. Structure of `architecture.md`

```
architecture.md
├── Overview (textual diagram of the flow: user → Front → API → Agent →
│              RAG/MCP → response)
├── Front (React Chat)        — responsibility, what it does NOT do
├── API (FastAPI)             — product boundary, contracts, streaming
├── Agent                     — Router → Knowledge/RAG or Query/Action → Validation
├── MCP                       — decoupled business capabilities
├── Knowledge/RAG             — ingestion → chunking → embeddings → retrieval
├── Infra                     — local (Docker+Ollama+Vector+MCP) and cloud (Terraform/AWS)
└── Contracts between modules — what each boundary accepts/returns, and what
                                 must never cross that boundary (e.g., raw
                                 customer data must never go straight to the Front)
```

The textual diagram of the main flow:

```
User → React Chat (Front)
     → FastAPI (API: simulated auth, session, streaming)
     → Agent Router
          ├─ Knowledge → RAG (retrieval + citation)
          └─ Query/Action → MCP (profile, loan, insurance, consortium, tariffs, ticket)
     → Validation/Critic (grounding, schema, policy)
     → Response (streaming, with sources/citations when applicable)
```

## 4. Decisions already made in the IDP (inherited, not reopened here)

- Local LLM via Ollama (S04 details the adapter).
- Frontend published on Vercel, local backend exposed via ngrok (S16 details
  this).
- Terraform represents the AWS alternative, not a day-to-day dependency (S21).
- Multi-agent only where there's a measurable benefit — the architecture starts
  from a single agent with a Router, evolving only if justified by evidence
  (evals).

## 5. Risks & mitigation

| Risk | Mitigation |
|---|---|
| Principles become too generic and don't guide real decisions | Every principle must have at least one concrete example of application in ATLAS |
| Documented architecture drifts from the code over time | `architecture.md` is reviewed every quarter (checkpoint at the start of Q2, Q3, Q4) |
| The document's scope grows to include implementation details | Implementation details live in each Sxx's specs; this document covers only boundaries and contracts |

## 6. Expected output

Two Markdown files versioned at the repository root (`constitution.md`,
`architecture.md`), referenced from the project's `README.md`.
