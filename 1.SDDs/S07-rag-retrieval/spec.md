# Spec — S07 · RAG Retrieval

> **Domain:** Knowledge · **Quarter:** Q2 · **Depends on:** S01 (Python Toolchain), S04 (Ollama Provider), S06 (RAG Ingestion)

## 1. Goal

Implement the retrieval and grounded generation engine for public Central Bank (BACEN) and banking regulatory knowledge, featuring semantic vector search with metadata filters, top-k ranking, traceable citations, and explicit guardrails for handling queries with missing documentary evidence.

## 2. Context

Per `architecture.md` and `constitution.md` (Principle 4: "Evidence before claims"), the copilot must never invent or guess regulatory rules, tariffs, or credit guidelines. When the Intent Router (S05) determines an intent requires regulatory knowledge, the RAG Retrieval engine searches the indexed Vector Store (S06), evaluates semantic similarity against threshold criteria, synthesizes answers grounded solely on the retrieved excerpts, formats citations with transparent provenance, and explicitly admits lack of evidence when documents do not support an answer.

## 3. In scope

- Semantic vector search querying the local Vector Store populated in S06.
- Metadata filtering (by document type, norm number, publication date range, or topic).
- Configurable top-k retrieval with similarity score thresholding.
- Grounded prompt formulation enforcing strict reliance on retrieved context excerpts.
- Traceable citation synthesis: generating structured references (norm name, article/section, document title, page/URL).
- Explicit missing-evidence handling: when retrieved chunks fail the confidence/relevance threshold, output a standardized "no sufficient evidence" message.
- Evaluation benchmark (`golden_questions.json`) to quantify retrieval metrics (Precision@k, Recall@k) and groundedness.

## 4. Out of scope

- Document parsing, chunking, and vector database indexing (covered in S06 RAG Ingestion).
- Client-facing React streaming and citation UI badges (covered in S15 React Chat).
- MCP domain tool execution or customer account lookups (covered in S08–S13).

## 5. Requirements

- **R1. Semantic Search with Metadata Filtering:** Query the vector store using user query embeddings, with optional metadata filters (e.g., `source_type == 'bacen_norm'`, `publication_date >= '2023-01-01'`).
- **R2. Relevance Threshold & Top-k Control:** Return the top-$k$ most similar chunks (default $k=3$ to $5$), rejecting chunks whose distance/similarity falls below a calibrated relevance threshold.
- **R3. Evidence-Grounded Synthesis:** The synthesizer must formulate the response based exclusively on provided context chunks. Hallucinations or reliance on ungrounded pre-trained weights are strictly forbidden by prompt and validation.
- **R4. Traceable Citations:** Every factual assertion in the synthesized response must reference one or more source chunks with verifiable metadata (`norm_reference`, `section_title`, `title`).
- **R5. Explicit Handling of Missing Evidence:** If no chunks satisfy the similarity threshold, or if the retrieved excerpts do not contain the specific answer, the retriever returns an explicit fallback indicating that no sufficient regulatory evidence was found, inviting the user to clarify.
- **R6. Conflicting Sources Resolution:** When multiple documents address the same subject with conflicting details, prefer the most recent/currently effective norm based on `effective_date` metadata and disclose this distinction in the response.

## 6. Acceptance criteria

- 100% of generated responses cite valid, existing chunks from the vector store with accurate metadata.
- For queries outside the corpus scope (negative/adversarial test cases), the system returns the missing-evidence response 100% of the time, with zero hallucinations.
- Retrieval benchmark (`golden_questions.json`) achieves Recall@k >= 85% and Groundedness score >= 90%.
- Latency for local search + synthesis remains within acceptable interactive bounds on the local environment.
