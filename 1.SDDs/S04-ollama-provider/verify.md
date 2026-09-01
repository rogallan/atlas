# Verify — S04 · Ollama Provider

## Evidence checklist

- [ ] Contract test run showing success, timeout, and malformed-JSON cases handled as specified.
- [ ] Structured output test run showing schema validation and the corrective-retry path.
- [ ] Configuration test showing model selection changes via environment/config only.
- [ ] Code review confirming no Ollama-specific types leak outside the provider module.

## Sign-off

- [ ] Reviewed against `spec.md` — all requirements (R1–R5) satisfied.
- [ ] Reviewed against `plan.md` — resilience and structured-output strategy match what was
      implemented.
- [ ] No task in `tasks.md` is checked without corresponding evidence above.
