# Verify — S11 · MCP Consortium Server

## Evidence checklist

- [ ] MCP Inspector log confirming tool advertisement (`tools/list`) with complete input/output schemas for `simulate_consortium`.
- [ ] Calculation benchmark test execution showing exact match with reference consortium group fixtures.
- [ ] Boundary tests log proving rejection of credit below minimum, above maximum, or with invalid terms.
- [ ] Bid simulation tests demonstrating accurate modeling of embedded and free bids.
- [ ] Payload inspection confirming that every returned simulation contains the mandatory non-binding disclaimer and itemized fee breakdown.

## Sign-off

- [ ] Reviewed against `spec.md` — all requirements (R1–R6) satisfied.
- [ ] Reviewed against `plan.md` — group rules, financial accounting formulas, and tool interfaces match implementation.
- [ ] No task in `tasks.md` is checked without corresponding evidence above.
