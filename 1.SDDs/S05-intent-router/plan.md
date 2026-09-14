# Plan — S05 · Intent Router

## 1. Approach

The Intent Router will be implemented as a specialized component inside `src/agent/router/`. It will consume the `LLMProvider` abstraction developed in S04 to execute zero-shot and few-shot classification prompts against Ollama, enforcing structured output via Pydantic. It provides deterministic parsing, confidence thresholding, and ambiguity detection before handing off to downstream components.

## 2. Architecture & Components

```
src/agent/router/
├── __init__.py
├── models.py       # Pydantic schemas (IntentType, IntentResult, ExtractedEntities)
├── prompts.py      # System prompts, taxonomy guidelines, few-shot examples
├── router.py       # IntentRouter service wrapping LLMProvider
└── evaluator.py    # Offline/test evaluation harness for golden intents
```

### Component interaction:
1. **Agent Orchestrator** passes the user message and optional recent dialogue context to `IntentRouter.route(message, context=None)`.
2. **IntentRouter** formats the prompt with domain classification guidelines and few-shot exemplars.
3. **LLMProvider** (`src.providers.ollama`) is invoked with `generate_structured(prompt, schema=IntentResult)`.
4. **Post-processor** checks if `confidence < CONFIDENCE_THRESHOLD` (default: 0.70). If so, it overrides `intent` to `IntentType.CLARIFICATION` and generates a clarification question if absent.

## 3. Key Interfaces & Data Contracts

```python
from enum import Enum
from pydantic import BaseModel, Field


class IntentType(str, Enum):
  KNOWLEDGE = "knowledge"  # Rules, Central Bank regulations, tariffs FAQ
  QUERY = "query"  # Customer profile, balance, history lookup
  SIMULATION = (
      "simulation"  # Loan simulation, insurance quote, consortium calc
  )
  ACTION = (
      "action"  # Ticket opening, scheduling, state-altering operations
  )
  CLARIFICATION = "clarification"  # Ambiguous, incomplete, or out-of-scope query


class ExtractedEntities(BaseModel):
  customer_id: str | None = Field(
      default=None, description="Synthetic customer identifier or CPF"
  )
  product_type: str | None = Field(
      default=None,
      description="loan, insurance, consortium, tariff, ticket, etc.",
  )
  amount: float | None = Field(
      default=None, description="Monetary value if mentioned"
  )
  term_months: int | None = Field(
      default=None, description="Number of installments/months"
  )
  raw_entities: dict[str, str] = Field(
      default_factory=dict, description="Additional detected key-value pairs"
  )


class IntentResult(BaseModel):
  intent: IntentType
  confidence: float = Field(
      ge=0.0, le=1.0, description="Confidence score from model"
  )
  reasoning: str = Field(description="Brief explanation for the classification")
  entities: ExtractedEntities = Field(default_factory=ExtractedEntities)
  suggested_clarification: str | None = Field(
      default=None,
      description="Required question if intent is clarification",
  )
```

## 4. Ambiguity & Fallback Strategy

- **Ambiguous input detection:** Prompts that lack an identifiable subject or action (e.g., "qual é a taxa?", "quero contratar") prompt the model to classify as `clarification` or trigger the confidence threshold rule.
- **Safety check for actions:** Queries expressing desire to perform operations without clear parameters (e.g., "abre um chamado") are flagged as `action`, but entities note missing fields, which S14 and S13 will gate with human confirmation.
- **Provider failure fallback:** If Ollama times out or errors repeatedly, `IntentRouter` falls back to a deterministic fallback: returning `CLARIFICATION` with a friendly message informing temporary system unavailability, logging the occurrence.

## 5. Golden Dataset & Evaluation Strategy

- Benchmark dataset `tests/data/golden_intents.json` containing 100+ annotated banking queries across all 5 intents:
  - Regulatory questions (Central Bank resolutions, BACEN interest rules) -> `knowledge`
  - Synthetic customer queries (income, status, accounts) -> `query`
  - Simulation prompts (CDC, personal loan, auto consortium) -> `simulation`
  - Operational actions (create support ticket, block card) -> `action`
  - Incomplete/vague utterances -> `clarification`
- Automated test script `evaluator.py` running against mocked LLM responses and integration runs with local Ollama to compute:
  - Accuracy overall.
  - Precision, Recall, and F1-Score per intent class.
  - Confusion matrix.

## 6. Risks & Mitigations

- **Risk:** LLM assigns high confidence to a hallucinated intent on vague input.
  - **Mitigation:** Strict negative examples in prompt instructions stating when to classify as `clarification`.
- **Risk:** Latency added before tool invocation.
  - **Mitigation:** Use a compact, quantized model via Ollama (e.g. `qwen2.5:7b` or `llama3.2:3b`) with minimal temperature (0.0) and constrained token limits for fast classification.
