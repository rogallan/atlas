# Tasks — S17 · Harness / Evals

- [ ] Define evaluation data models (`TestCase`, `TestResult`, `ScorecardSummary`) in `evals/models.py`.
- [ ] Create and curate benchmark datasets:
  - `evals/datasets/golden_intents.json` (Intent classification test cases)
  - `evals/datasets/golden_questions.json` (RAG retrieval & groundedness cases)
  - `evals/datasets/golden_conversations.json` (Multi-turn banking dialogues and workflows)
- [ ] Implement metric evaluators in `evals/metrics/`:
  - `retrieval.py` (Recall@k, Precision@k, MRR)
  - `groundedness.py` (Faithfulness / hallucination detection)
  - `tool_selection.py` (Tool choice and parameter extraction accuracy)
  - `safety.py` (Human-in-the-Loop action enforcement verification)
- [ ] Implement CLI evaluation runner with threshold gatekeeper in `evals/runner.py`.
- [ ] Implement scorecard reporter generating markdown reports in `evals/reporters/markdown.py`.
- [ ] Integrate evaluation runner into CI test workflow as a regression quality gate.
- [ ] Execute baseline benchmark run and generate initial scorecard report in `evals/reports/`.

## Definition of Done

- All tasks above are complete and merged.
- Evaluation runner executes cleanly from the terminal with a single command.
- Baseline scorecard achieves target quality thresholds:
  - Intent Accuracy >= 90%
  - Retrieval Recall@k >= 85%
  - Groundedness Score >= 90%
  - Safety HITL Compliance = 100%
- CI quality gate prevents merging regressions that breach established thresholds.
