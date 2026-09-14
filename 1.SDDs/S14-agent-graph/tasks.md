# Tasks — S14 · Agent Graph

- [ ] Define the agent state model (`AgentState`) and node enumerations in `src/agent/graph/state.py`.
- [ ] Implement `RouterNode` integrating S05 Intent Router in `src/agent/graph/nodes/router_node.py`.
- [ ] Implement `RAGNode` integrating S07 RAG Retrieval in `src/agent/graph/nodes/rag_node.py`.
- [ ] Implement `MCPNode` dispatching to S08–S13 servers in `src/agent/graph/nodes/mcp_node.py`.
- [ ] Implement `ValidatorNode` (grounding check, schema check, HITL action interception) in `src/agent/graph/nodes/validator_node.py`.
- [ ] Implement `SynthesizerNode` and `FallbackNode` with step-limit enforcement.
- [ ] Implement conditional routing edges and assemble the compiled graph in `src/agent/graph/orchestrator.py`.
- [ ] Implement input prompt injection and jailbreak detector in `src/agent/guardrails/injection.py`.
- [ ] Implement comprehensive integration tests in `tests/integration/test_agent_graph.py` covering multi-turn routing, HITL confirmation guardrails, step-limit aborts, and prompt injection defense.

## Definition of Done

- All tasks above are complete and merged.
- End-to-end graph handles all primary routes (RAG, Customer, Simulations, Tickets, Clarification).
- Unconfirmed state-changing actions are blocked 100% of the time by the Validator node.
- Step limits and timeouts reliably prevent runaway execution loops.
- Prompt injection attempts are neutralized without crashing the orchestrator.
- End-to-end graph integration tests pass in CI.
