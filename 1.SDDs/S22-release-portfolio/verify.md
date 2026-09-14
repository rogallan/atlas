# Verify — S22 · Release / Portfolio

## Evidence checklist

- [ ] Command output of `python 6.ops/release/release_checklist.py` confirming 100% completion across all SDDs (S00 to S22) with zero missing tasks or evidence items.
- [ ] Final benchmark evaluation scorecard report (`7.evals/reports/final_scorecard_v1.0.0.md`) showing:
  - Intent Accuracy >= 90%
  - RAG Groundedness >= 90%
  - RAG Retrieval Recall >= 85%
  - Tool Calling Accuracy >= 90%
  - Human-in-the-Loop Safety Compliance = 100%
- [ ] Security audit execution report (`6.ops/release/security_audit.sh`) confirming zero leaked secrets and 100% synthetic data compliance in git history.
- [ ] Complete test pyramid run (`pytest --cov`) showing green status across all test types with >= 80% coverage.
- [ ] Review and verification of `8.docs/portfolio/demo_script.md` successfully executed against a clean local deployment.
- [ ] Verified `CHANGELOG.md` and Git release tag `v1.0.0` published on the repository.

## Sign-off

- [ ] Reviewed against `spec.md` — all functional requirements (R1–R6) and acceptance criteria satisfied.
- [ ] Reviewed against `plan.md` — release verification pipeline, documentation assets, and scorecard format match implementation.
- [ ] No task in `tasks.md` is checked without corresponding evidence above.
