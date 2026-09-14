# Plan — S07 · RAG Retrieval

## 1. Approach

Implement the retrieval and grounded generation layer under `src/rag/retrieval/`. The component acts as an autonomous service consumed by the Agent Orchestrator (S14). It connects to the Vector Store initialized in S06, embeds user queries locally using the Ollama embedding adapter, filters and ranks relevant chunks, and synthesizes answers with strict citation schemas.

## 2. Architecture & Components

```
src/rag/retrieval/
├── __init__.py
├── models.py         # RetrievalQuery, SearchResult, GroundedResponse, Citation
├── searcher.py       # Vector similarity search with metadata filter queries
├── synthesizer.py    # LLM prompt composer & grounded answer generator
├── citations.py      # Citation extractor & reference linker
└── service.py        # High-level RAG retrieval service orchestrating search + synthesis
```

### Retrieval Flow:
1. **Query Formulation:** The service accepts a user query and optional metadata filters (e.g. specific norm or date window).
2. **Embedding:** `searcher.py` invokes the Ollama embedder to produce the query vector.
3. **Similarity Search:** The vector store executes cosine/distance search, returning candidates with scores.
4. **Relevance Threshold Check:** Chunks scoring below `SIMILARITY_THRESHOLD` (e.g., cosine similarity < 0.70) are discarded.
5. **Missing-Evidence Decision:** If zero chunks pass the filter, short-circuit immediately with a standardized missing-evidence response.
6. **Synthesis:** `synthesizer.py` passes the valid context chunks into an anti-hallucination system prompt for Ollama.
7. **Citation Parsing:** `citations.py` parses citation markers (e.g., `[fonte: 1]`) and populates typed `Citation` objects with source document title, norm number, and text excerpt.

## 3. Key Interfaces & Data Contracts

```python
from pydantic import BaseModel, Field


class Citation(BaseModel):
  chunk_id: str
  source_title: str
  norm_reference: str | None = None
  section_title: str | None = None
  source_url_or_path: str
  excerpt: str


class GroundedResponse(BaseModel):
  answer: str
  has_sufficient_evidence: bool
  citations: list[Citation] = Field(default_factory=list)
  confidence_score: float = Field(ge=0.0, le=1.0)
  disclaimer: str | None = None


class RetrievalFilter(BaseModel):
  source_type: str | None = None
  norm_number: str | None = None
  min_publication_date: str | None = None
```

```python
from typing import Protocol


class RAGRetrievalService(Protocol):

  def retrieve_and_answer(
      self, query: str, filters: RetrievalFilter | None = None, top_k: int = 4
  ) -> GroundedResponse:
    ...
```

## 4. Prompt Engineering & Missing Evidence Strategy

- **System Prompt Rules:**
  1. *Rule 1 (Evidence Only):* Answer using ONLY facts directly mentioned in the `<context>` block. Do not extrapolate.
  2. *Rule 2 (No Evidence Admission):* If the context does not contain the answer, reply exactly: *"Não foram encontradas informações suficientes na documentação pública do Banco Central para responder a esta pergunta."*
  3. *Rule 3 (Citation Markers):* Explicitly append bracketed references `[^chunk_id]` next to every claim.
  4. *Rule 4 (Recency):* When contrasting norms are present, highlight the one with the latest effective date.

## 5. Evaluation Strategy & Golden Questions

- Create `tests/data/golden_questions.json` featuring:
  - 30 factual questions directly answered by the BACEN corpus.
  - 15 out-of-domain questions (e.g., general world knowledge, personal opinions, unindexed policies).
  - 10 temporal/conflict resolution questions.
- Automated evaluation runner measuring:
  - **Context Recall & Precision:** Did the top-k chunks contain the gold answer?
  - **Faithfulness / Groundedness:** Are all claims in the answer supported by retrieved chunks?
  - **Refusal Accuracy:** Did the system correctly refuse out-of-domain/negative questions?

## 6. Risks & Mitigations

- **Risk:** LLM ignores prompt instructions and answers from pre-trained knowledge on out-of-domain queries.
  - **Mitigation:** Post-synthesis validator in `synthesizer.py` verifying that citations are present. If zero citations are returned or groundedness check fails, fall back to the safe refusal response.
- **Risk:** Top-k chunks exceed context window or inflate local latency.
  - **Mitigation:** Cap $k=4$, truncate chunk text to necessary context, and use concise local prompts.
