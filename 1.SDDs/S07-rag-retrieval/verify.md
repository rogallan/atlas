# Verify — S07 · RAG Retrieval

## Evidence checklist

- [ ] Unit and integration test logs demonstrating vector search, metadata filtering, and citation linking.
- [ ] Evaluation scorecard on `golden_questions.json` demonstrating Recall@k >= 85% and Groundedness >= 90%.
- [ ] Negative test runs confirming 100% adherence to missing-evidence refusal when prompts fall outside the indexed documents.
- [ ] Sample end-to-end response output displaying properly formatted citations referencing specific Central Bank norm articles.
- [ ] Conflict test demonstrating correct selection of the latest effective norm when historical revisions exist.

## Sign-off

- [ ] Reviewed against `spec.md` — all requirements (R1–R6) satisfied.
- [ ] Reviewed against `plan.md` — interfaces, prompt design, and citation models match implementation.
- [ ] No task in `tasks.md` is checked without corresponding evidence above.
