# Tasks — S08 · MCP Customer Server

- [x] Define Pydantic request and response schemas in `src/mcp/customer/models.py`.
- [x] Implement synthetic data repository adapter in `src/mcp/customer/repository.py` querying S02 dataset.
- [x] Implement simulated authorization and audit logging filter in `src/mcp/customer/auth.py`.
- [x] Implement customer tool handlers (`get_customer_profile`, `get_customer_accounts`, `get_financial_history`, `get_customer_summary`) in `src/mcp/customer/tools.py`.
- [x] Implement MCP Server bootstrap and transport registration in `src/mcp/customer/server.py`.
- [x] Implement unit and contract tests in `tests/unit/test_mcp_customer.py` verifying tool invocation, error cases, and schema compliance.
- [x] Verify audit log emission upon tool execution.

## Definition of Done

- [x] All tasks above are complete and merged.
- [x] MCP Customer Server runs locally and responds to standard MCP tool requests.
- [x] Queries against synthetic customers return deterministic data matching the S02 seed.
- [x] Non-existent IDs and unauthorized attempts trigger structured errors.
- [x] Contract tests pass with 100% schema validation.
