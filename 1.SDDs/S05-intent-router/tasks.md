# Tasks — S05 · Intent Router

- [ ] Define the taxonomy (`knowledge`, `query`, `simulation`, `action`, `clarification`) and create domain Pydantic models in `src/agent/router/models.py`.
- [ ] Implement prompts and few-shot classification templates in `src/agent/router/prompts.py`.
- [ ] Implement `IntentRouter` service in `src/agent/router/router.py` using `LLMProvider.generate_structured()`.
- [ ] Implement ambiguity handling and confidence thresholding (`confidence < threshold` -> `clarification`).
- [ ] Construct the evaluation benchmark dataset `tests/data/golden_intents.json` covering all intent categories and edge cases.
- [ ] Build evaluation runner and unit/contract tests for `IntentRouter` in `tests/unit/test_intent_router.py` and `tests/evals/test_golden_intents.py`.

## Definition of Done

- All tasks above are complete and merged into the codebase.
- Router produces 100% compliant JSON conforming to `IntentResult`.
- Evaluation dataset achieves >= 90% routing accuracy with automated evaluation reporting.
- Ambiguity and low confidence gracefully trigger clarification prompts without runtime exceptions.
- Unit and contract tests pass in CI.
