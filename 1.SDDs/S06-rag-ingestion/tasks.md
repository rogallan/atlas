# Tasks — S06 · RAG Ingestion

- [ ] Select local embedding model and local Vector DB/Store, documenting choices in an ADR.
- [ ] Implement document loaders for Central Bank public documents (PDF, Markdown, TXT) in `src/rag/ingestion/loaders.py`.
- [ ] Implement chunking strategy with Portuguese legal/regulatory boundaries in `src/rag/ingestion/chunkers.py`.
- [ ] Implement metadata extraction and deterministic `chunk_id` hashing in `src/rag/models.py`.
- [ ] Implement local embedding adapter for Ollama embeddings in `src/rag/ingestion/embedder.py`.
- [ ] Implement local Vector Store adapter with persistence in `src/rag/ingestion/store.py`.
- [ ] Assemble the ingestion pipeline and CLI runner in `src/rag/ingestion/pipeline.py`.
- [ ] Add unit tests for loaders, chunkers, and idempotency in `tests/unit/test_rag_ingestion.py`.

## Definition of Done

- All tasks above are complete and merged.
- Sample Central Bank documents ingested successfully into local Vector Store.
- Re-running the pipeline is proven idempotent (zero duplicates created).
- Every stored chunk contains complete provenance metadata.
- Automated tests for parsing, chunking, and storage pass in CI.
