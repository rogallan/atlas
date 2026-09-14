# Spec — S06 · RAG Ingestion

> **Domain:** Knowledge · **Quarter:** Q2 · **Depends on:** S01 (Python Toolchain), S04 (Ollama Provider)

## 1. Goal

Build a reproducible, local-first ingestion pipeline for public Central Bank (BACEN) documents and banking regulations, transforming raw documents (PDF, Markdown, HTML, text) into clean, metadata-enriched chunks, generating embeddings locally, and indexing them into a local Vector Store/DB.

## 2. Context

Per `architecture.md` and `PDI_ATLAS_GenAI_Banking_Copilot_PT_BR.html`, the RAG boundary is responsible for grounding copilot answers with traceable public knowledge. The first stage of this pipeline is ingestion: extracting text and structural metadata, choosing an effective chunking strategy, generating local embeddings, and indexing them deterministically so that the retrieval phase (S07) has high-quality context and provenance for citations.

## 3. In scope

- Document loaders for public Central Bank documents (PDF, Markdown, TXT).
- Metadata extraction (document title, norm/resolution number, issue date, effective date, source URL, section/chapter, page number).
- Document chunking strategy evaluation and implementation (e.g. recursive text splitting with token/character overlap, preserving headers).
- Local embedding generation via Ollama (or local HuggingFace model runner) using an agreed-upon model (e.g., `nomic-embed-text` or `bge-m3`).
- Vector Store/DB integration (e.g., ChromaDB, Qdrant local, or LanceDB) with persistent local storage.
- Ingestion CLI/script with idempotency (upsert or hashing to prevent duplicate indexing).
- Automated tests verifying ingestion, chunk integrity, and metadata retention.

## 4. Out of scope

- Semantic search, top-k retrieval, and reranking algorithms (covered in S07 RAG Retrieval).
- End-to-end question answering or citation formatting in chat responses (covered in S07 and S14).
- Dynamic web scraping of third-party portals during user queries (all documents are loaded from a curated repository folder).

## 5. Requirements

- **R1. Document Parsing and Cleaners:** Extract raw text while removing artifacts (headers, footers, duplicate whitespace) and preserving structural headings.
- **R2. Provenance and Metadata Enrichment:** Every chunk must retain origin metadata: `document_id`, `title`, `source_type`, `norm_reference`, `effective_date`, `section`, and `chunk_id`.
- **R3. Chunking Strategy:** Text splitter configurable by chunk size (tokens/characters) and overlap, benchmarked to maintain semantic cohesion without cutting sentences or regulatory articles abruptly.
- **R4. Local Embedding Model:** Generate vector embeddings strictly using a local provider (Ollama embeddings endpoint or local transformer) without cloud vendor dependencies.
- **R5. Local Vector Store / Persistence:** Store vectors alongside payload metadata in an embedded/local vector database with persistent storage on disk.
- **R6. Idempotent Ingestion Pipeline:** Re-running the pipeline over identical documents must not generate duplicate chunks or alter existing chunk IDs (hash-based identity).

## 6. Acceptance criteria

- Running the ingestion script on the Central Bank sample corpus processes all files without errors and populates the local vector store.
- 100% of stored chunks have populated metadata containing at least `source_type`, `title`, and `chunk_id`.
- Re-running the ingestion pipeline on the exact same corpus results in zero duplicate chunks created.
- Automated unit tests validate chunk boundaries, metadata preservation, and embedding generation locally.
