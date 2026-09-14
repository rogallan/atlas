# Spec — S14 · Agent Graph

> **Domain:** Agent Orchestration · **Quarter:** Q2 · **Depends on:** S01 (Python Toolchain), S04 (Ollama Provider), S05 (Intent Router), S06/S07 (RAG), S08–S13 (MCP Servers)

## 1. Goal

Implement the central stateful Agent Graph orchestrator that coordinates the end-to-end conversation flow: routing incoming requests via the Intent Router, delegating to RAG retrieval or specialized MCP domain servers, validating intermediate and final outputs via a dedicated Validator/Critic node (grounding, schema, policy), and enforcing strict execution boundaries (step limits, timeouts, and fallback handling).

## 2. Context

Per `architecture.md`, `constitution.md` (Principles 2, 3, 4: "Security by default", "Explicit tools", "Evidence before claims"), and the interactive solution design in `PDI_ATLAS_GenAI_Banking_Copilot_PT_BR.html`, the copilot's intelligence lives inside an explicit, deterministic state graph (`Router → RAG/MCP → Validator/Critic → Response`). Rather than letting an unconstrained LLM loop autonomously, the graph enforces strict state transitions, ensures that state-changing actions (S13) stop for human confirmation, validates that factual claims are anchored by citations or tool outputs, and guards against prompt injection from users and documents.

## 3. In scope

- Stateful Agent Graph orchestrator implemented using a state graph pattern (e.g. LangGraph or lightweight native state machine).
- Graph Nodes:
  - `Router Node`: Invokes S05 Intent Router to determine intent (`knowledge`, `query`, `simulation`, `action`, `clarification`).
  - `RAG Retrieval Node`: Dispatches to S07 when intent is `knowledge` or regulatory lookups.
  - `MCP Tool Node`: Dispatches to S08–S13 servers when intent is customer query, simulation, or ticket action.
  - `Validator / Critic Node`: Performs post-execution verification: checking factual grounding against retrieved sources, ensuring tool output schema adherence, detecting policy violations, and halting unconfirmed actions.
  - `Response Synthesizer Node`: Prepares final answer, attaching citation badges, simulation cards, or action confirmation proposals.
- Execution Guardrails:
  - Maximum step limit (default: 5 graph steps) to eliminate infinite tool loops.
  - Per-turn timeout enforcement.
  - Resilient fallback node triggered on LLM or tool failure.
- Adversarial Defense: Basic prompt injection detection on user input and retrieved document context.

## 4. Out of scope

- FrontEnd React UI or visual rendering of the conversation (handled in S15 React Chat).
- Raw HTTP network framing and SSE streaming protocols (handled in S03 FastAPI Gateway).
- Individual tool internal logic or database seed queries (handled in S06–S13).

## 5. Requirements

- **R1. Deterministic State Graph:** Formally define graph state, nodes, and conditional edges:
  $$\text{Input} \rightarrow \text{Router} \xrightarrow{\text{intent}} \begin{cases} \text{RAG Node} \\ \text{MCP Tool Node} \\ \text{Clarification Node} \end{cases} \rightarrow \text{Validator/Critic} \rightarrow \text{Response} \rightarrow \text{End}$$
- **R2. Validator/Critic Node (Guardrail):** The Validator node must inspect candidate responses before returning to the user:
  - *Grounding check:* Verify claims cite valid chunks or tool payloads.
  - *Action check:* If an action tool was invoked, verify that explicit human confirmation was provided; otherwise, block execution and emit an action confirmation request card.
  - *Policy check:* Reject any offensive, financial speculation, or real contracting statements.
- **R3. Step Limits and Anti-Looping:** Restrict graph iterations to a configurable maximum (e.g. 5 steps). If the limit is exceeded, branch to the fallback node.
- **R4. Timeout and Resilient Fallback:** When a node times out or fails unexpectedly, the graph transitions to the `Fallback Node`, returning a graceful explanation to the relationship manager without exposing stack traces.
- **R5. Injection Detection (User & Document):** Filter inputs against common prompt injection patterns (system prompt overrides, jailbreaks, indirect injection from document text).

## 6. Acceptance criteria

- Multi-turn execution successfully routes across all supported paths (RAG, Customer Query, Loan/Insurance/Consortium Simulation, Ticket Action, and Clarification).
- Validator/Critic node detects and blocks simulated hallucinations (claims made without context or tool evidence) in automated tests.
- Attempting an action without human approval prompts the user with a confirmation card and halts execution before mutating state.
- Simulated infinite loops or node timeouts reliably terminate at the fallback node within the designated step limit.
- End-to-end integration tests prove that prompt injection payloads are neutralized by input filters and the Critic node.
