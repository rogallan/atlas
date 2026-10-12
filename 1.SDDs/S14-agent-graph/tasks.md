# Tasks — S14 · Agent Graph

- [x] Define the agent state model (`AgentState`) and node enumerations in `src/agent/graph/state.py`.
- [x] Implement `RouterNode` integrating S05 Intent Router in `src/agent/graph/nodes/router_node.py`.
- [x] Implement `RAGNode` integrating S07 RAG Retrieval in `src/agent/graph/nodes/rag_node.py`.
- [x] Implement `MCPNode` dispatching to S08–S13 servers in `src/agent/graph/nodes/mcp_node.py`.
- [x] Implement `ValidatorNode` (grounding check, schema check, HITL action interception) in `src/agent/graph/nodes/validator_node.py`.
- [x] Implement `SynthesizerNode` and `FallbackNode` with step-limit enforcement.
- [x] Implement conditional routing edges and assemble the compiled graph in `src/agent/graph/orchestrator.py`.
- [x] Implement input prompt injection and jailbreak detector in `src/agent/guardrails/injection.py`.
- [x] Implement comprehensive integration tests in `tests/integration/test_agent_graph.py` covering multi-turn routing, HITL confirmation guardrails, step-limit aborts, and prompt injection defense.

## Definition of Done

- [x] All tasks above are complete and merged.
- [x] End-to-end graph handles all primary routes (RAG, Customer, Simulations, Tickets, Clarification).
- [x] Unconfirmed state-changing actions are blocked 100% of the time by the Validator node.
- [x] Step limits and timeouts reliably prevent runaway execution loops.
- [x] Prompt injection attempts are neutralized without crashing the orchestrator.
- [x] End-to-end graph integration tests pass in CI.
