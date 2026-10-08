# Verify — S08 · MCP Customer Server

## Evidence checklist

- [x] MCP Inspector or contract test log confirming tool advertisement (`tools/list`) with compliant JSON schemas (`test_mcp_tools_list_contract`).
- [x] Test execution output showing successful profile, accounts, history, and summary lookups against seeded synthetic clients (`CUST-0001` Dave Weckl).
- [x] Error handling test output verifying `CustomerNotFoundError` on non-existent `customer_id` (`test_customer_not_found_exception`, `test_customer_not_found_jsonrpc`).
- [x] Authorization test output verifying rejection of queries lacking simulated manager authorization (`test_authorization_denied`, `test_authorization_denied_jsonrpc`).
- [x] Audit log verification confirming structured JSON events logged for each query without real PII (`test_audit_logging_lifecycle`).

## Sign-off

- [x] Reviewed against `spec.md` — all requirements (R1–R6) satisfied.
- [x] Reviewed against `plan.md` — data models, tool interfaces, and security filter match implementation.
- [x] No task in `tasks.md` is checked without corresponding evidence above.
