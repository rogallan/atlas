# Tasks — S04 · Ollama Provider

- [ ] Create a decoupled LLM adapter (interface + Ollama implementation).
- [ ] Parameterize model selection via configuration.
- [ ] Implement timeout, retry, and fallback behavior.
- [ ] Write contract tests for the provider, including structured output.

## Definition of Done

- All tasks above are complete and merged.
- Contract tests (success, timeout, malformed JSON, structured output) pass in CI.
- Model selection is fully driven by configuration, with no hardcoded model name in application
  code.
