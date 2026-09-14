# Tasks — S07 · RAG Retrieval

- [ ] Define data models (`RetrievalQuery`, `GroundedResponse`, `Citation`, `RetrievalFilter`) in `src/rag/retrieval/models.py`.
- [ ] Implement semantic vector search and metadata filtering in `src/rag/retrieval/searcher.py`.
- [ ] Implement synthesis prompt templates enforcing strict grounding and citation tags in `src/rag/retrieval/synthesizer.py`.
- [ ] Implement citation extraction and reference linking in `src/rag/retrieval/citations.py`.
- [ ] Implement explicit missing-evidence handling and threshold gatekeeper in `src/rag/retrieval/service.py`.
- [ ] Implement conflict resolution policy preferring recent effective norms.
- [ ] Construct evaluation dataset `tests/data/golden_questions.json` with positive, negative (out-of-domain), and conflicting queries.
- [ ] Implement automated RAG evaluation test suite and regression tests in `tests/evals/test_rag_retrieval.py`.

## Definition of Done

- All tasks above are complete and merged.
- 100% of grounded responses contain verified, traceable citations.
- Queries without evidence in the corpus return a safe refusal with zero hallucinations.
- Retrieval benchmark achieves Recall@k >= 85% and Groundedness >= 90% on `golden_questions.json`.
- Unit, integration, and evaluation tests pass in CI.
