# Tasks — S09 · MCP Loan Server

- [x] Define loan modalities catalog, interest rates, and term constraints in `src/mcp/loan/catalog.py`.
- [x] Define Pydantic models (`LoanModality`, `LoanSimulationResult`, `ModalityInfo`) in `src/mcp/loan/models.py`.
- [x] Implement deterministic financial math engine (Price table, IOF, CET) in `src/mcp/loan/calculator.py`.
- [x] Implement debt-to-income margin evaluation against S02/S08 synthetic customer records.
- [x] Implement MCP tool handlers (`simulate_loan`, `get_loan_modalities`, `check_loan_pre_conditions`) in `src/mcp/loan/tools.py`.
- [x] Implement MCP Server bootstrap and transport integration in `src/mcp/loan/server.py` and `http_server.py`.
- [x] Implement unit and contract tests in `tests/unit/test_mcp_loan.py` covering mathematical formulas, boundary limits, and schema validation.
- [x] Validate presence of mandatory disclaimer and premises in 100% of simulation outputs.

## Definition of Done

- All tasks above are complete and merged.
- MCP Loan Server runs locally and responds to MCP simulation requests.
- Financial calculation outputs match benchmark tables with exact cent precision.
- Out-of-bounds inputs produce typed validation errors.
- Simulation outputs are explicitly marked as hypothetical with complete premises and disclaimer.
