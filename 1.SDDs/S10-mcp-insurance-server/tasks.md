# Tasks — S10 · MCP Insurance Server

- [x] Model synthetic insurance catalog, coverage options, and limits in `src/mcp/insurance/catalog.py`.
- [x] Define Pydantic request and response schemas in `src/mcp/insurance/models.py`.
- [x] Implement deterministic premium calculation engine with IOF in `src/mcp/insurance/calculator.py`.
- [x] Implement synthetic customer profile risk adjustment integration with S02/S08 dataset.
- [x] Implement MCP tool handlers (`list_insurance_products`, `get_coverage_details`, `simulate_insurance_quote`) in `src/mcp/insurance/tools.py`.
- [x] Implement MCP Server bootstrap and transport registration in `src/mcp/insurance/server.py` and `http_server.py`.
- [x] Implement unit and contract tests in `tests/unit/test_mcp_insurance.py` verifying catalog inspection, actuarial math, boundaries, and schemas.
- [x] Validate presence of mandatory disclaimer and coverage breakdown in 100% of quote outputs.

## Definition of Done

- All tasks above are complete and merged.
- MCP Insurance Server runs locally and responds to standard MCP requests.
- Premium calculations match deterministic actuarial benchmark fixtures.
- Invalid coverages and out-of-bounds capitals trigger structured validation errors.
- Quotation outputs include mandatory hypothetical disclaimer and coverage breakdown.
