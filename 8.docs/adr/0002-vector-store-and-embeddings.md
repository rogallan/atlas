# ADR 0002: Local Vector Store (ChromaDB) and Local Embeddings (Ollama nomic-embed-text)

## Status
Accepted

## Date
2026-10-07

## Context
Per the ATLAS architectural charter (`1.SDDs/architecture.md`) and RAG specifications (`1.SDDs/S06-rag-ingestion/spec.md`), the banking copilot requires a Retrieval-Augmented Generation (RAG) system to ground answers in official Banco Central do Brasil (BACEN) regulations, resolutions, and credit rules.
Key architectural constraints:
1. **Local-First & Air-gapped Capability:** No external cloud API calls for embeddings or vector storage during local development and testing.
2. **Deterministic Metadata Retention:** Full provenance (resolution number, publication date, section, article) must be attached to every chunk to enable legal citation.
3. **Reproducibility & Idempotency:** Ingestion must be repeatable without creating duplicate vector entries.
4. **Python Toolchain Integration:** Must integrate smoothly with our Python 3.11+ stack managed by `uv`.

## Decision
1. **Vector Store:** Selected **ChromaDB** (`chromadb.PersistentClient`) with embedded SQLite/DuckDB persistence.
   - **Rationale:** Native Python client, zero external server dependencies for local execution, built-in metadata filtering, and straightforward migration path to client/server or distributed modes if needed.
2. **Embedding Model:** Selected **`nomic-embed-text`** served locally via Ollama (`http://localhost:11434/api/embed` and `/api/embeddings`).
   - **Rationale:** High-performance 768-dimensional text embedding model with 8192 context window, open weights, already installed and operational in the local Ollama daemon, and strong multilingual/Portuguese retrieval performance.
3. **Chunking Strategy:** Recursive character chunking with Portuguese regulatory delimiters (`\n## `, `\n### `, `\nArt. `, `\n\n`, `\n`, ` `), target chunk size ~500 tokens (approx. 1500 chars), with 10% overlap (150 chars).

## Consequences
- **Positive:**
  - Zero cloud cost or vendor lock-in for vector operations.
  - Native integration with the existing `OllamaSettings` infrastructure developed in S04.
  - Local database files stored in `.gitignore`'d directory (`storage/chroma`).
- **Negative / Mitigations:**
  - ChromaDB requires local disk storage for vector indices.
  - Mitigated by storing persistent collections in `2.src/rag/storage/chroma/` and ignoring via `.gitignore`.
