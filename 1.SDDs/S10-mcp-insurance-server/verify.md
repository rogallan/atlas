# Verify — S10 · MCP Insurance Server

## Evidence checklist

- [ ] MCP Inspector log confirming tool advertisement (`tools/list`) with complete input/output schemas for `simulate_insurance_quote`.
- [ ] Actuarial calculation test execution showing exact match with reference insurance quote fixtures.
- [ ] Boundary tests log proving rejection of capital below minimum, above maximum, or with invalid coverage identifiers.
- [ ] Separation of concerns verification confirming that numeric quotes are generated deterministically by the tool, with reference hooks for RAG document enrichment.
- [ ] Payload inspection confirming that every returned quote contains the mandatory non-binding disclaimer and itemized coverage breakdown.

## Sign-off

- [ ] Reviewed against `spec.md` — all requirements (R1–R6) satisfied.
- [ ] Reviewed against `plan.md` — catalog structures, formulas, and tool interfaces match implementation.
- [ ] No task in `tasks.md` is checked without corresponding evidence above.
