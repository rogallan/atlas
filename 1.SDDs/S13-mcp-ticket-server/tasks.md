# Tasks — S13 · MCP Ticket Server

- [ ] Define Pydantic request, response, and draft models in `src/mcp/ticket/models.py`.
- [ ] Implement ticket storage and token tracking with idempotency index in `src/mcp/ticket/store.py`.
- [ ] Implement structured security audit logger in `src/mcp/ticket/audit.py`.
- [ ] Implement two-phase MCP tools (`prepare_ticket`, `confirm_and_create_ticket`, `get_ticket`, `list_customer_tickets`) in `src/mcp/ticket/tools.py`.
- [ ] Implement token TTL expiration and replay protection guardrails.
- [ ] Implement MCP Server bootstrap and transport registration in `src/mcp/ticket/server.py`.
- [ ] Implement comprehensive unit and guardrail tests in `tests/unit/test_mcp_ticket.py` covering approval, rejection, expired tokens, and idempotency.
- [ ] Verify audit log generation for confirmed and blocked ticket creation attempts.

## Definition of Done

- All tasks above are complete and merged.
- MCP Ticket Server runs locally and executes two-phase ticket workflows.
- Any attempt to create tickets without explicit human confirmation is definitively blocked and logged.
- Idempotency guarantees prevent duplicate ticket generation.
- Contract, unit, and guardrail security tests pass in CI.
