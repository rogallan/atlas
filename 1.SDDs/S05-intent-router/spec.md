# Spec — S05 · Intent Router

> **Domain:** Agent · **Quarter:** Q1 · **Depends on:** S01 (Python Toolchain), S04 (Ollama Provider)

## 1. Goal

Implement the Intent Router component of the Agent Orchestrator to classify incoming user messages into canonical banking intents (`knowledge`, `query`, `simulation`, `action`, `clarification`) producing a strictly validated structured output (JSON schema) and handling ambiguous queries gracefully.

## 2. Context

Per `architecture.md` and `PDI_ATLAS_GenAI_Banking_Copilot_PT_BR.html`, user messages forwarded from the FastAPI Gateway (S03) reach the Agent Orchestrator. Before dispatching to RAG (S06/S07) or MCP domain servers (S08–S13), the copilot must determine the intent with high precision, extract key entities/parameters, and identify ambiguous requests that require human clarification rather than hallucinating or executing unwarranted tools.

## 3. In scope

- Taxonomy definition: `knowledge`, `query`, `simulation`, `action`, and `clarification`.
- Strict structured output definition using Pydantic models (JSON schema).
- LLM prompt engineering and few-shot examples for banking relationship manager scenarios.
- Ambiguity detection leading to the `clarification` intent with targeted follow-up questions.
- Benchmark evaluation dataset (`golden_intents.json`) to evaluate routing accuracy.
- Fallback handling for classification failures or schema validation errors.

## 4. Out of scope

- Direct execution of RAG searches or MCP tool calls (handled by S06–S13 and orchestrated by S14).
- Full multi-turn conversation memory graph or state machine (handled in S14 Agent Graph).
- Direct HTTP exposure or API streaming (handled in S03 FastAPI Gateway).

## 5. Requirements

- **R1. Canonical Intent Taxonomy:** The router must classify queries into exactly one primary intent:
  - `knowledge`: Questions regarding public banking regulations, Central Bank rules, tariffs, or financial concepts.
  - `query`: Read-only queries regarding customer profiles, accounts, balances, or transaction history.
  - `simulation`: Calculations or hypothetical projections (loans, financing, insurance quotes, consortium plans) using synthetic formulas without committing state.
  - `action`: State-changing operations (opening tickets, scheduling contact, initiating service requests) that ultimately require explicit human confirmation.
  - `clarification`: Vague, incomplete, or highly ambiguous queries where the necessary operational parameters or user goals cannot be deduced with high confidence.
- **R2. Structured Output Schema:** Output must strictly conform to a Pydantic schema including `intent`, `confidence` (float between 0.0 and 1.0), `reasoning` (concise rationale), `entities` (extracted domain entities like customer IDs, product types, amounts), and optional `suggested_clarification` (required if intent is `clarification`).
- **R3. Integration with LLM Provider:** Utilize the `LLMProvider.generate_structured()` contract established in S04 to communicate with Ollama.
- **R4. Ambiguity and Low-Confidence Handling:** If model confidence is below a configurable threshold (e.g. 0.70) or the prompt lacks crucial context, the router must designate `clarification` to prevent unsafe tool invocation.
- **R5. Golden Intent Dataset & Evals:** Provide a versioned benchmark dataset (`golden_intents.json`) covering standard, edge-case, and adversarial banking prompts, measuring classification accuracy and precision per intent.

## 6. Acceptance criteria

- 100% of router responses validate against the structured output Pydantic schema without runtime schema errors.
- Routing accuracy across the golden evaluation dataset achieves >= 90% overall accuracy in automated test runs.
- Ambiguous prompts (e.g., "quero ver aquilo lá", "faz um cálculo pra mim") reliably route to `clarification` with a non-empty `suggested_clarification`.
- Malformed outputs from Ollama trigger the retry/fallback mechanism without crashing the orchestrator.
