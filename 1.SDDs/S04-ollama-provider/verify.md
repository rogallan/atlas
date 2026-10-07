# Verify — S04 · Ollama Provider

## Evidence checklist

- [x] Contract test run showing success, timeout, and malformed-JSON cases handled as specified.
- [x] Structured output test run showing schema validation and the corrective-retry path.
- [x] Configuration test showing model selection changes via environment/config only.
- [x] Code review confirming no Ollama-specific types leak outside the provider module.

## Sign-off

- [x] Reviewed against `spec.md` — all requirements (R1–R5) satisfied.
- [x] Reviewed against `plan.md` — resilience and structured-output strategy match what was
      implemented.
- [x] No task in `tasks.md` is checked without corresponding evidence above.

## Execution Evidence Log

1. **Protocol & Conformance Tests (`4.tests/contract/test_llm_contract.py`)**:
   - `test_ollama_provider_implements_protocol` ➔ PASSED (`isinstance(provider, LLMProvider)` verified with `@runtime_checkable`).

2. **Unit & Resilience Tests (`4.tests/unit/test_ollama_provider.py`)**:
   - `test_ollama_generate_success` ➔ PASSED (standard text generation via HTTP mock).
   - `test_ollama_configuration_driven` ➔ PASSED (custom host and model dynamically parsed from settings).
   - `test_ollama_timeout_and_retry_exhaustion` ➔ PASSED (retried 2 times then raised `LLMTimeoutError`).
   - `test_ollama_transient_failure_recovery` ➔ PASSED (recovered on attempt 2 after transient connection error).
   - `test_ollama_generate_structured_success` ➔ PASSED (valid JSON schema parsed into Pydantic model).
   - `test_ollama_structured_corrective_retry` ➔ PASSED (attempt 1 broken JSON recovered on corrective prompt attempt 2).
   - `test_ollama_structured_output_exhausted_failure` ➔ PASSED (failed twice raised `StructuredOutputError`).
   - `test_ollama_streaming` ➔ PASSED (asynchronously yielded NDJSON tokens).

3. **Coverage & Quality**:
   - `uv run pytest` ➔ `24 passed in 2.09s`, Total coverage: `92.42%`.
   - `uv run ruff check` ➔ `All checks passed!`
   - `uv run mypy` ➔ `Success: no issues found in 29 source files`.
   - `uv run pre-commit run` ➔ All hooks passed.
