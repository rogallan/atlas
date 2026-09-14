# Tasks — S08 · MCP Customer Server

- [ ] Define Pydantic request and response schemas in `src/mcp/customer/models.py`.
- [ ] Implement synthetic data repository adapter in `src/mcp/customer/repository.py` querying S02 dataset.
- [ ] Implement simulated authorization and audit logging filter in `src/mcp/customer/auth.py`.
- [ ] Implement customer tool handlers (`get_customer_profile`, `get_customer_accounts`, `get_financial_history`, `get_customer_summary`) in `src/mcp/customer/tools.py`.
- [ ] Implement MCP Server bootstrap and transport registration in `src/mcp/customer/server.py`.
- [ ] Implement unit and contract tests in `tests/unit/test_mcp_customer.py` verifying tool invocation, error cases, and schema compliance.
- [ ] Verify audit log emission upon tool execution.

## Definition of Done

- All tasks above are complete and merged.
- MCP Customer Server runs locally and responds to standard MCP tool requests.
- Queries against synthetic customers return deterministic data matching the S02 seed.
- Non-existent IDs and unauthorized attempts trigger structured errors.
- Contract tests pass with 100% schema validation.
