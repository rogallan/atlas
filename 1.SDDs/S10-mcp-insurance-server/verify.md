# Verify — S10 · MCP Insurance Server

## Evidence checklist

- [x] MCP Inspector log confirming tool advertisement (`tools/list`) with complete input/output schemas for `list_insurance_products`, `get_coverage_details`, and `simulate_insurance_quote`.
- [x] Actuarial calculation test execution showing exact match with reference insurance quote fixtures (Decimal rounding, IOF Decreto 6.306/2007, 5% annual upfront discount).
- [x] Boundary tests log proving rejection of capital below minimum, above maximum, or with invalid coverage identifiers (`InvalidInsuranceParameterError`, `CoverageNotFoundError`).
- [x] Separation of concerns verification confirming that numeric quotes are generated deterministically by the tool, with reference hooks for RAG document enrichment.
- [x] Payload inspection confirming that every returned quote contains the mandatory non-binding disclaimer and itemized coverage breakdown.

## Verification Evidence

- **Unit, Contract & Integration Suite:** 136 tests passing, 2 skipped across repository with 86.68% total coverage (insurance module achieves 95%+ coverage).
- **Tool Protocol Conformance:** JSON-RPC 2.0 stdio loop and SSE/REST FastAPI HTTP transport on port 8003 tested (`test_mcp_insurance.py`).
- **Interactive CLI Demo:** Executed successfully against customer Dave Weckl (`6.ops/demo_mcp_insurance.py`).
- **Linter & Type Checking:** Ruff and Mypy passed cleanly with 0 errors across 79 source files.
- **Pre-commit:** All pre-commit hooks passed.

## Sign-off

- [x] Reviewed against `spec.md` — all requirements (R1–R6) satisfied.
- [x] Reviewed against `plan.md` — catalog structures, formulas, and tool interfaces match implementation.
- [x] No task in `tasks.md` is checked without corresponding evidence above.
