# Verify — S14 · Agent Graph

## Evidence checklist

- [ ] End-to-end integration test execution demonstrating successful traversal through all graph routes (`knowledge`, `query`, `simulation`, `action`, `clarification`).
- [ ] Guardrail evidence demonstrating that an action without prior human confirmation is intercepted by the Validator node, halting execution and returning a confirmation proposal.
- [ ] Grounding test run proving that responses containing ungrounded factual statements are flagged and rejected by the Critic node.
- [ ] Anti-looping test log showing execution terminated cleanly at the fallback node upon reaching the 5-step limit.
- [ ] Adversarial test output confirming detection and neutralization of prompt injection payloads in user inputs and documents.

## Sign-off

- [ ] Reviewed against `spec.md` — all requirements (R1–R5) satisfied.
- [ ] Reviewed against `plan.md` — graph topology, state schema, and node responsibilities match implementation.
- [ ] No task in `tasks.md` is checked without corresponding evidence above.
