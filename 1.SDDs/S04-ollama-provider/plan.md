# Plan — S04 · Ollama Provider

## 1. Approach

Define the provider interface first (so it can be mocked in tests for later phases), then implement
the Ollama-backed version behind it, then add resilience (timeout/retry/fallback) and structured
output validation.

## 2. Key interfaces

```
class LLMProvider(Protocol):
    def generate(self, prompt: str, **kwargs) -> str: ...
    def generate_structured(self, prompt: str, schema: type[BaseModel], **kwargs) -> BaseModel: ...
```

`OllamaProvider` implements `LLMProvider`, wrapping calls to the local Ollama HTTP API.

## 3. Configuration

- `OLLAMA_HOST`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT_SECONDS`, `OLLAMA_MAX_RETRIES` — all read from
  environment/config, with sane local-dev defaults.

## 4. Resilience strategy

- **Timeout:** per-request timeout enforced on the HTTP call to Ollama.
- **Retry:** exponential backoff, up to `OLLAMA_MAX_RETRIES` attempts, only for retryable failures
  (timeouts, connection errors — not validation errors).
- **Fallback:** after retries are exhausted, raise a typed `LLMProviderError` that calling code
  (Agent Orchestrator) can catch and handle explicitly (e.g., respond with a graceful error message
  rather than crashing).

## 5. Structured output

- `generate_structured()` prompts the model for JSON, parses the response, and validates it against
  a Pydantic schema.
- On validation failure, one retry with a corrective prompt is attempted before raising a typed
  `StructuredOutputError`.

## 6. Test strategy

- **Contract tests** against a mocked Ollama HTTP endpoint (success, timeout, malformed JSON
  cases).
- **Structured output test** verifying schema validation and the corrective-retry path.
- **Configuration test** verifying model selection changes based on config, without code changes.

## 7. Risks & mitigations

- **Risk:** Ollama's local API behavior differs across versions. **Mitigation:** pin the tested
  Ollama version in documentation and keep the provider's HTTP calls isolated in one module.
- **Risk:** structured output is unreliable for some models. **Mitigation:** the corrective-retry
  path plus a clear typed error for callers to handle gracefully.
