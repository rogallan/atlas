# Verify — S17 · Harness / Evals

## Evidence checklist

- [ ] Evaluation runner execution output showing successful test completion across intent, retrieval, groundedness, tool selection, and safety suites.
- [ ] Initial benchmark scorecard report (`evals/reports/scorecard_YYYYMMDD.md`) verifying all metrics meet or exceed established thresholds.
- [ ] Quality gate test execution demonstrating deliberate build failure upon an injected regression (e.g., dropped groundedness or unconfirmed action).
- [ ] Multi-turn conversation evaluation log confirming successful state preservation, tool coordination, and HITL card gating.
- [ ] CI workflow configuration and test run showing the automated eval quality gate passing on PR/push.

## Sign-off

- [ ] Reviewed against `spec.md` — all requirements (R1–R6) satisfied.
- [ ] Reviewed against `plan.md` — metric formulas, dataset structures, and runner architecture match implementation.
- [ ] No task in `tasks.md` is checked without corresponding evidence above.
