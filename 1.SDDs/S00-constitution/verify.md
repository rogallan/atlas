# S00 — Constitution + Architecture · Verification

## Acceptance criteria (Definition of Done for this item)

- [ ] `constitution.md` exists at the repository root and contains, at
      minimum, the 6 principles defined in spec.md (local-first, security by
      default, explicit tools, evidence before claims, tests before release,
      fictitious data always).
- [ ] Each principle in `constitution.md` has at least one concrete example of
      application in the ATLAS context (not just an abstract statement).
- [ ] `architecture.md` exists at the repository root and documents the 6
      boundaries (Front, API, Agent, MCP, Knowledge/RAG, Infra) with the
      responsibility and contract of each.
- [ ] `architecture.md` contains the textual diagram of the main flow
      (User → Front → API → Agent Router → RAG/MCP → Validation → Response).
- [ ] Both documents were reviewed with the IDP mentor (record the
      date/observations in the commit itself or in `docs/adr/`).
- [ ] The repository's `README.md` references (links to) `constitution.md` and
      `architecture.md`.
- [ ] No S01 work was started before this item was completed (S00 is blocking
      for the rest of the catalog, per the IDP's Q1 ordering).

## How to verify

1. Open `constitution.md` and `architecture.md` at the repository root and
   confirm both exist and are not empty/placeholder.
2. Confirm the 6 principles are present and each has an applied example.
3. Confirm the flow diagram in `architecture.md` covers all 6 boundaries
   mentioned in the IDP.
4. Confirm with the mentor that the review was done.
5. Mark this item as complete in the IDP checklist (section 14) only after
   the 4 steps above.
