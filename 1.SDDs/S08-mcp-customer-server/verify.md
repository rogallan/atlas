# Verify — S08 · MCP Customer Server

## Evidence checklist

- [ ] MCP Inspector or contract test log confirming tool advertisement (`tools/list`) with compliant JSON schemas.
- [ ] Test execution output showing successful profile, accounts, history, and summary lookups against seeded synthetic clients.
- [ ] Error handling test output verifying `CustomerNotFoundError` on non-existent `customer_id`.
- [ ] Authorization test output verifying rejection of queries lacking simulated manager authorization.
- [ ] Audit log verification confirming structured JSON events logged for each query without real PII.

## Sign-off

- [ ] Reviewed against `spec.md` — all requirements (R1–R6) satisfied.
- [ ] Reviewed against `plan.md` — data models, tool interfaces, and security filter match implementation.
- [ ] No task in `tasks.md` is checked without corresponding evidence above.
