# Tasks — S18 · Security Guardrails

- [ ] Write the formal GenAI Threat Model document in `docs/security/threat_model.md` based on OWASP Top 10 for LLM Applications.
- [ ] Define security models and schemas (`SecurityCheckResult`, `ThreatCategory`, `SecurityThreatLevel`) in `src/security/models.py`.
- [ ] Implement direct prompt injection and jailbreak detection heuristics in `src/security/input_guardrail.py`.
- [ ] Implement XML-based context isolation and indirect prompt injection defense in `src/security/context_isolation.py`.
- [ ] Implement output secret/system-prompt leakage detector in `src/security/output_guardrail.py`.
- [ ] Implement structured log sanitizer masking synthetic CPFs, account numbers, and bearer tokens in `src/security/sanitizers.py`.
- [ ] Integrate security guardrails into FastAPI request/response lifecycle in `src/security/middleware.py`.
- [ ] Build automated adversarial red-teaming test suite in `tests/security/` covering direct injection, indirect RAG injection, secret leakage, and log masking.
- [ ] Verify that 100% of adversarial attacks are mitigated without blocking valid banking queries.

## Definition of Done

- All tasks above are complete and merged.
- Threat model is documented and approved in `docs/security/`.
- Input and output guardrails intercept 100% of tested jailbreaks and prompt override attempts.
- RAG context isolation successfully neutralizes indirect injection from document text.
- Structured log sanitizer guarantees zero plain-text synthetic CPFs or secrets in logs.
- Adversarial security test suite passes cleanly in CI.
