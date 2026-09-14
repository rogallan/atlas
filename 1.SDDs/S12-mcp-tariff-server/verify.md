# Verify — S12 · MCP Tariff Server

## Evidence checklist

- [ ] MCP Inspector log confirming tool advertisement (`tools/list`) with complete input/output schemas for `get_service_fee` and `check_essential_services_quota`.
- [ ] Essential services test log proving exact zero-cost quotas for standard monthly allowances (4 withdrawals, 2 transfers, 2 statements).
- [ ] Channel differentiation test output proving higher fees for assisted branch counter versus digital app channels.
- [ ] Cross-consistency validation test run proving zero contradiction between MCP table entries and RAG text documents.
- [ ] Inspection of responses confirming presence of traceability metadata (`regulatory_basis`, `effective_date`).

## Sign-off

- [ ] Reviewed against `spec.md` — all requirements (R1–R6) satisfied.
- [ ] Reviewed against `plan.md` — catalog schema, channel models, and tool interfaces match implementation.
- [ ] No task in `tasks.md` is checked without corresponding evidence above.
