# Tasks — S12 · MCP Tariff Server

- [x] Model structured tariff items, channel rates, and essential services quotas in `src/mcp/tariff/catalog.py`.
- [x] Define Pydantic request and response schemas in `src/mcp/tariff/models.py`.
- [x] Implement essential services quota calculation and package waiver rules in `src/mcp/tariff/tools.py`.
- [x] Implement cross-validation sync helper with RAG documentary source in `src/mcp/tariff/sync.py`.
- [x] Implement MCP Server bootstrap and transport registration in `src/mcp/tariff/server.py` and `http_server.py`.
- [x] Implement unit and contract tests in `tests/unit/test_mcp_tariff.py` verifying catalog lookups, channel pricing, and essential services.
- [x] Implement consistency test comparing MCP values with RAG tariff documents.

## Definition of Done

- All tasks above are complete and merged.
- MCP Tariff Server runs locally and responds to standard MCP requests.
- Essential services lookups return 100% compliant zero-cost quotas under BACEN rules.
- Channel-specific pricing and package waiver rules evaluate deterministically.
- Integration tests confirm zero discrepancies between MCP tariff values and RAG reference documents.
