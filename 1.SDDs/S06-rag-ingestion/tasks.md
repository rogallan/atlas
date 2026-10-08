# Tasks — S06 · RAG Ingestion

- [x] Select local embedding model and local Vector DB/Store, documenting choices in an ADR (`8.docs/adr/0002-vector-store-and-embeddings.md`).
- [x] Implement document loaders for Central Bank public documents (PDF, Markdown, TXT) in `2.src/rag/ingestion/loaders.py`.
- [x] Implement chunking strategy with Portuguese legal/regulatory boundaries in `2.src/rag/ingestion/chunkers.py`.
- [x] Implement metadata extraction and deterministic `chunk_id` hashing in `2.src/rag/models.py`.
- [x] Implement local embedding adapter for Ollama embeddings in `2.src/rag/ingestion/embedder.py`.
- [x] Implement local Vector Store adapter with persistence in `2.src/rag/ingestion/store.py`.
- [x] Assemble the ingestion pipeline and CLI runner in `2.src/rag/ingestion/pipeline.py`.
- [x] Add unit tests for loaders, chunkers, and idempotency in `4.tests/unit/test_rag_ingestion.py`.

## Definition of Done

- All tasks above are complete and merged.
- Sample Central Bank documents ingested successfully into local Vector Store.
- Re-running the pipeline is proven idempotent (zero duplicates created).
- Every stored chunk contains complete provenance metadata.
- Automated tests for parsing, chunking, and storage pass in CI.
