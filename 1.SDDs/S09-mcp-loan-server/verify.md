# Verify — S09 · MCP Loan Server

## Evidence checklist

- [x] MCP Inspector log confirming tool advertisement (`tools/list`) with complete input/output schemas for `simulate_loan`, `get_loan_modalities`, and `check_loan_pre_conditions`.
- [x] Financial calculation benchmark test run showing zero discrepancy with reference Price amortization fixtures (Tabela Price PMT, IOF Decreto 6.306/2007, CET Resolução CMN 4.881/2020).
- [x] Boundary tests log proving rejection of negative amounts, zero terms, and out-of-range parameters (`InvalidLoanParameterError`).
- [x] Margin check verification test showing that high monthly payments flag `is_within_margin = False` based on synthetic income.
- [x] Payload inspection confirming that every returned simulation contains the mandatory non-binding disclaimer and premise breakdown.

## Verification Evidence

- **Unit, Contract & Integration Suite:** 115 tests passing, 2 skipped across repository with 87.11% total coverage (loan module components achieve 95%+ coverage).
- **Tool Protocol Conformance:** JSON-RPC 2.0 stdio loop and SSE/REST FastAPI HTTP transport on port 8002 tested (`test_mcp_loan.py`).
- **Linter & Type Checking:** Ruff and Mypy passed with zero warnings/errors.
- **Pre-commit:** All pre-commit hooks passed.

## Sign-off

- [x] Reviewed against `spec.md` — all requirements (R1–R6) satisfied.
- [x] Reviewed against `plan.md` — formulas, schemas, and catalog configurations match implementation.
- [x] No task in `tasks.md` is checked without corresponding evidence above.
