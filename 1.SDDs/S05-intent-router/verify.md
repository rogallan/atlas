# Verify — S05 · Intent Router

## Evidence checklist

- [ ] Schema validation test output confirming that `IntentResult` parses all model outputs and rejects malformed payloads.
- [ ] Evaluation report showing routing accuracy >= 90% against `golden_intents.json`.
- [ ] Ambiguity test cases demonstrating that underspecified requests return `clarification` with a valid `suggested_clarification`.
- [ ] Fallback and resilience test proving that provider timeout/error defaults to graceful clarification rather than crashing.
- [ ] Code review confirming separation of concerns: router classifies and extracts parameters, without executing downstream tools directly.

## Sign-off

- [ ] Reviewed against `spec.md` — all functional requirements (R1–R5) and acceptance criteria satisfied.
- [ ] Reviewed against `plan.md` — interfaces and ambiguity handling match the planned design.
- [ ] No task in `tasks.md` is checked without corresponding evidence above.
