# Tasks — S11 · MCP Consortium Server

- [x] Model synthetic consortium modalities, group rules, allowed terms, and fee structures in `src/mcp/consortium/catalog.py`.
- [x] Define Pydantic request and response schemas in `src/mcp/consortium/models.py`.
- [x] Implement deterministic consortium accounting engine (common fund, admin fee, reserve fund, bids) in `src/mcp/consortium/calculator.py`.
- [x] Implement MCP tool handlers (`list_consortium_modalities`, `get_consortium_group_rules`, `simulate_consortium`) in `src/mcp/consortium/tools.py`.
- [x] Implement MCP Server bootstrap and transport registration in `src/mcp/consortium/server.py` and `http_server.py`.
- [x] Implement unit and contract tests in `tests/unit/test_mcp_consortium.py` verifying catalog inspection, fee calculations, bid simulations, and schemas.
- [x] Validate presence of mandatory contemplation disclaimer and fee breakdown in 100% of simulation outputs.

## Definition of Done

- All tasks above are complete and merged.
- MCP Consortium Server runs locally and responds to standard MCP requests.
- Installment calculations and fee breakdowns match benchmark consortium group fixtures.
- Out-of-bounds parameters produce structured validation errors.
- Simulation outputs explicitly disclose that contemplation depends on assembly draws or bids.
