# Verify — S09 · MCP Loan Server

## Evidence checklist

- [ ] MCP Inspector log confirming tool advertisement (`tools/list`) with complete input/output schemas for `simulate_loan`.
- [ ] Financial calculation benchmark test run showing zero discrepancy with reference Price amortization fixtures.
- [ ] Boundary tests log proving rejection of negative amounts, zero terms, and out-of-range parameters.
- [ ] Margin check verification test showing that high monthly payments flag `is_within_margin = False` based on synthetic income.
- [ ] Payload inspection confirming that every returned simulation contains the mandatory non-binding disclaimer and premise breakdown.

## Sign-off

- [ ] Reviewed against `spec.md` — all requirements (R1–R6) satisfied.
- [ ] Reviewed against `plan.md` — formulas, schemas, and catalog configurations match implementation.
- [ ] No task in `tasks.md` is checked without corresponding evidence above.
