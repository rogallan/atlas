# Verify — S07 · RAG Retrieval

## Evidence checklist

- [x] Unit and integration test logs demonstrating vector search, metadata filtering, and citation linking (`4.tests/unit/test_rag_retrieval.py` — 19/19 tests passing).
- [x] Evaluation scorecard on `golden_questions.json` demonstrating Recall@k >= 85% and Groundedness >= 90% (`4.tests/evals/test_rag_retrieval.py` — 100% recall, 100% groundedness).
- [x] Negative test runs confirming 100% adherence to missing-evidence refusal when prompts fall outside the indexed documents (Refusal Accuracy = 100%).
- [x] Sample end-to-end response output displaying properly formatted citations referencing specific Central Bank norm articles.
- [x] Conflict test demonstrating correct selection of the latest effective norm when historical revisions exist (`test_service_conflict_recency_sorting`).

## Sign-off

- [x] Reviewed against `spec.md` — all requirements (R1–R6) satisfied.
- [x] Reviewed against `plan.md` — interfaces, prompt design, and citation models match implementation.
- [x] No task in `tasks.md` is checked without corresponding evidence above.
