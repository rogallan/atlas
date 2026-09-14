# Plan — S06 · RAG Ingestion

## 1. Approach

Design and implement a clean, modular ingestion pipeline under `src/rag/ingestion/`. The architecture prioritizes reproducibility, local-first execution, and rich metadata retention to ensure transparent source attribution in later retrieval steps.

## 2. Architecture & Components

```
src/rag/
├── __init__.py
├── models.py             # DocumentChunk, IngestionMetadata, DocumentSource
├── ingestion/
│   ├── __init__.py
│   ├── loaders.py        # PDF, Markdown, TXT file parsers
│   ├── chunkers.py       # Hierarchical / recursive text chunker
│   ├── embedder.py       # Local embedding adapter (Ollama embeddings)
│   ├── store.py          # Vector Store client abstraction (e.g., Chroma / Qdrant local)
│   └── pipeline.py       # Ingestion orchestrator & CLI runner
└── storage/              # Local vector database storage directory (.chroma / data)
```

### Flow of Execution:
1. **Raw Document Discovery:** `loaders.py` scans `docs/knowledge/` for raw regulatory documents (BACEN resolutions, credit rules, tariff tables).
2. **Text Extraction & Sanitization:** Text is extracted and normalized; structural headings and document headers are captured into `IngestionMetadata`.
3. **Chunking:** `chunkers.py` splits documents into ~500-token chunks with 50-token overlap, respecting Markdown headers or legal article boundaries (e.g., "Art. 1º", "Art. 2º").
4. **Hashing & Deduplication:** Generates deterministic `chunk_id` via SHA256 of `(doc_id, chunk_index, chunk_text)`.
5. **Embedding:** `embedder.py` sends batches of text chunks to Ollama (`nomic-embed-text` or `bge-m3`).
6. **Indexing:** `store.py` upserts vectors and metadata dictionaries into the local vector database.

## 3. Key Interfaces & Data Contracts

```python
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
  document_id: str
  title: str
  source_type: str = Field(
      default="bacen_norm",
      description="Type of source: norm, resolution, manual, tariff_table",
  )
  norm_number: str | None = None
  publication_date: str | None = None
  section_title: str | None = None
  source_url_or_path: str


class DocumentChunk(BaseModel):
  chunk_id: str
  document_id: str
  text: str
  token_count: int
  chunk_index: int
  metadata: DocumentMetadata
  embedding: list[float] | None = None
```

```python
from typing import Protocol


class VectorStore(Protocol):

  def upsert_chunks(self, chunks: list[DocumentChunk]) -> int:
    ...

  def count(self) -> int:
    ...

  def reset(self) -> None:
    ...
```

## 4. Technical Decisions & ADR Alignment

- **Local Vector DB:** ChromaDB in local persistence mode (`chromadb.PersistentClient`) or Qdrant Local. (Documented in `docs/adr/ADR-003-vector-store.md`).
- **Embedding Model:** `nomic-embed-text` via Ollama local API (768 dimensions) or `bge-m3`. Fast, open weights, runs locally on CPU/GPU.
- **Chunking Strategy:** Recursive character text splitter with separators configured for Portuguese legal/banking structures (`["\n## ", "\n### ", "\nArt. ", "\n\n", "\n", " "]`).

## 5. Test Strategy

- **Parser unit tests:** Verify PDF and Markdown loaders correctly extract text and preserve metadata tags.
- **Chunking tests:** Assert chunk sizes remain within bounds and verify that overlap preserves sentence coherence.
- **Idempotency test:** Ingesting the same sample file twice results in identical chunk IDs and no growth in total vector collection count.
- **Embedding mock test:** Test batch embedding error handling, rate limiting, and retry behavior.

## 6. Risks & Mitigations

- **Risk:** PDFs with tables or multi-column layouts produce fragmented or unreadable text.
  - **Mitigation:** Use structured text parsers (such as `pypdf` or `pymupdf`), preprocess tables into markdown syntax where possible, and curate sample documents in Markdown alongside PDFs.
- **Risk:** Embedding generation overhead on local CPU.
  - **Mitigation:** Implement batching (batch size 16–32) and verify Ollama hardware acceleration; provide caching for previously computed embeddings.
