# Verify — S12 · MCP Tariff Server

## Evidence checklist

- [x] MCP Inspector log confirming tool advertisement (`tools/list`) with complete input/output schemas for `get_service_fee`, `list_tariff_packages`, `check_essential_services_quota`, and `compare_packages`.
- [x] Essential services test log proving exact zero-cost quotas for standard monthly allowances (4 withdrawals, 2 transfers, 2 statements).
- [x] Channel differentiation test output proving higher fees for assisted branch counter versus digital app channels.
- [x] Cross-consistency validation test run proving zero contradiction between MCP table entries and RAG text documents (`verify_tariff_rag_consistency`).
- [x] Inspection of responses confirming presence of traceability metadata (`regulatory_basis`, `effective_date`).

## Verification Evidence

- **Unit, Contract & Integration Suite:** 175 tests passing, 2 skipped across repository with 84.98% total coverage (tariff module achieves 85%+ coverage).
- **Tool Protocol Conformance:** JSON-RPC 2.0 stdio loop and SSE/REST FastAPI HTTP transport on port 8005 tested (`test_mcp_tariff.py`).
- **Interactive CLI Demo:** Executed successfully with essential services quota evaluation and package comparisons (`6.ops/demo_mcp_tariff.py`).
- **Linter & Type Checking:** Ruff and Mypy passed cleanly with 0 errors across 97 source files.
- **Pre-commit:** All pre-commit hooks passed.

## Sign-off

- [x] Reviewed against `spec.md` — all requirements (R1–R6) satisfied.
- [x] Reviewed against `plan.md` — catalog schema, channel models, and tool interfaces match implementation.
- [x] No task in `tasks.md` is checked without corresponding evidence above.
