# ADR 0004: Agent Orchestration Engine (LangGraph StateGraph)

## Status
Accepted

## Date
2026-10-08

## Context
Per `1.SDDs/S14-agent-graph/spec.md`, ATLAS coordinates multiple specialized banking domains (Regulatory RAG, Customer Analytics, Loan Simulations, Insurance, Consortia, Tariff Check, and Support Ticketing). The system requires an orchestration framework capable of:
1. Cyclical state transitions with strong typing.
2. Interruption and checkpointing for Human-in-the-Loop (HITL) confirmation of high-impact actions.
3. Explicit node boundaries, error recovery, and auditability.
4. Clean separation of concerns between Intent Routing, Context Retrieval, MCP Execution, and Guardrail Validation.

## Decision
Selected **LangGraph (`StateGraph`)** as the core agent execution engine:
1. **Explicit State Model:** Implemented `AgentSessionState` capturing conversation turns, active customer context, intent, pending actions, tool results, citations, and HITL approval tokens.
2. **Deterministic State Transitions:**
   - `router_node`: Classifies utterance and extracts structured entities.
   - `rag_node`: Executes vector search and retrieves regulatory chunks when intent is `knowledge`.
   - `mcp_node`: Invokes domain tools when intent is `simulation` or `action`.
   - `validator_node`: Enforces guardrails, PII masking, and schema validation.
   - `synthesis_node`: Streams grounded responses with exact legal citations.
3. **HITL Interruption:** If a sensitive action is identified (e.g., ticket creation or limit changes), the graph checkpoints state and sets `requires_human_confirmation = True`, requiring an explicit confirmation payload before executing.

## Consequences
- **Positive:**
  - Predictable control flow without unbounded LLM loops.
  - Native support for human approval workflows and deterministic stage timing.
  - Complete observability: Each node logs execution duration, input state, and output state.
- **Negative / Mitigations:**
  - Graph definition requires explicit routing logic and schema definitions.
  - Mitigated by strict Pydantic v2 schemas across all node payloads and state models.
