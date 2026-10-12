# Tasks — S04 · Ollama Provider

- [x] Create a decoupled LLM adapter (interface `2.src/providers/base.py` + Ollama implementation `2.src/providers/ollama.py`).
- [x] Parameterize model selection via configuration (`2.src/providers/config.py`).
- [x] Implement timeout, retry, and fallback behavior (`_post_with_retry` with exponential backoff and typed exceptions).
- [x] Write contract tests for the provider, including structured output (`4.tests/unit/test_ollama_provider.py`, `4.tests/contract/test_llm_contract.py`).

## Definition of Done

- [x] All tasks above are complete and merged.
- [x] Contract tests (success, timeout, malformed JSON, structured output) pass in CI (24 tests green, 92.42% coverage).
- [x] Model selection is fully driven by configuration, with no hardcoded model name in application
      code.
