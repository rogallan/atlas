# Verify — S06 · RAG Ingestion

## Evidence checklist

- [ ] ADR in `docs/adr/` documenting the selection of local embeddings and Vector DB/Store.
- [ ] Pipeline execution log showing successful ingestion and indexing of Central Bank documents into the local vector store.
- [ ] Test run verifying chunk boundary splitting and metadata extraction accuracy.
- [ ] Idempotency test run proving that running ingestion twice does not create duplicate vectors.
- [ ] Vector store inspection showing populated metadata fields (`source_type`, `title`, `norm_reference`, `chunk_id`) across stored entries.

## Sign-off

- [ ] Reviewed against `spec.md` — all requirements (R1–R6) satisfied.
- [ ] Reviewed against `plan.md` — data models, chunking strategy, and store interface match the implementation.
- [ ] No task in `tasks.md` is checked without corresponding evidence above.
