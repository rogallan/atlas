# Verify — S18 · Security Guardrails

## Evidence checklist

- [ ] Approved GenAI Threat Model document in `docs/security/threat_model.md` addressing OWASP LLM Top 10 vulnerabilities.
- [ ] Adversarial test suite execution log (`pytest tests/security/test_adversarial.py`) demonstrating 100% block rate across direct injection and jailbreak payloads.
- [ ] Indirect injection test execution showing that malicious commands embedded inside simulated Central Bank document chunks are ignored by the agent.
- [ ] Leakage scanner test log confirming that attempts to extract system prompts or mock API keys return a sanitized refusal response.
- [ ] Log inspection evidence demonstrating that synthetic CPFs, account numbers, and bearer tokens are masked across application logs.
- [ ] False-positive verification test demonstrating that legitimate banking queries regarding fraud prevention and security concepts are processed normally.

## Sign-off

- [ ] Reviewed against `spec.md` — all functional requirements (R1–R6) and acceptance criteria satisfied.
- [ ] Reviewed against `plan.md` — threat categories, guardrail architecture, and sanitization regexes match implementation.
- [ ] No task in `tasks.md` is checked without corresponding evidence above.
