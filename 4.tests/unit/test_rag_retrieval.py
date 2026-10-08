"""Unit tests for RAG Retrieval: searcher, citations, synthesizer, and service (S07)."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from rag.models import DocumentMetadata
from rag.retrieval.citations import create_citation_from_chunk, extract_citations
from rag.retrieval.models import RetrievalFilter, SearchResult
from rag.retrieval.searcher import (
    DEFAULT_SIMILARITY_THRESHOLD,
    VectorSearcher,
    distance_to_similarity,
)
from rag.retrieval.service import DISCLAIMER_TEXT, RAGRetrievalService
from rag.retrieval.synthesizer import (
    STANDARD_REFUSAL_MESSAGE,
    GroundedSynthesizer,
    build_context_block,
)


def _sample_metadata(
    doc_id: str = "doc_1",
    title: str = "Resolução Pix",
    norm_number: str | None = "BCB 1/2020",
    pub_date: str | None = "2020-08-12",
    sec_title: str | None = "Seção I",
) -> DocumentMetadata:
    return DocumentMetadata(
        document_id=doc_id,
        title=title,
        source_type="bacen_norm",
        norm_number=norm_number,
        publication_date=pub_date,
        effective_date=pub_date,
        section_title=sec_title,
        source_url_or_path="8.docs/knowledge/resolucao_pix.md",
    )


def _sample_chunk(
    chunk_id: str = "chk_001",
    text: str = "O Pix é o arranjo de pagamentos instantâneos do Banco Central.",
    similarity: float = 0.85,
    metadata: DocumentMetadata | None = None,
) -> SearchResult:
    return SearchResult(
        chunk_id=chunk_id,
        document_id="doc_1",
        text=text,
        similarity_score=similarity,
        metadata=metadata or _sample_metadata(),
    )


# ---------------------------------------------------------------------------
# 1. Similarity Metric Tests
# ---------------------------------------------------------------------------


def test_distance_to_similarity_boundaries() -> None:
    """Validate distance to similarity mapping behavior across key boundary values."""
    assert distance_to_similarity(-0.5) == 1.0
    assert distance_to_similarity(0.0) == 1.0
    assert distance_to_similarity(1.0) == 0.5
    assert distance_to_similarity(3.0) == 0.25
    assert distance_to_similarity(9.0) == 0.1


# ---------------------------------------------------------------------------
# 2. Citation Extraction & Linking Tests
# ---------------------------------------------------------------------------


def test_create_citation_from_chunk() -> None:
    """create_citation_from_chunk generates typed citation and trims long excerpts."""
    long_text = "A" * 300
    chunk = _sample_chunk(text=long_text)
    citation = create_citation_from_chunk(chunk, max_excerpt_len=50)

    assert citation.chunk_id == chunk.chunk_id
    assert citation.source_title == chunk.metadata.title
    assert citation.norm_reference == chunk.metadata.norm_number
    assert citation.section_title == chunk.metadata.section_title
    assert citation.source_url_or_path == chunk.metadata.source_url_or_path
    assert len(citation.excerpt) == 53  # 50 chars + "..."
    assert citation.excerpt.endswith("...")


def test_extract_citations_empty() -> None:
    """extract_citations returns empty list when candidate chunks is empty."""
    assert extract_citations("Texto qualquer", []) == []


def test_extract_citations_explicit_markers() -> None:
    """extract_citations matches explicit markers like [^chunk_id] and [fonte: chunk_id]."""
    c1 = _sample_chunk(chunk_id="chk_pix_01")
    c2 = _sample_chunk(chunk_id="chk_med_02")
    c3 = _sample_chunk(chunk_id="chk_tar_03")

    text = (
        "Segundo o regulamento [^chk_pix_01], o Pix funciona 24/7. "
        "Além disso, há o mecanismo de devolução [fonte: chk_med_02]."
    )

    citations = extract_citations(text, [c1, c2, c3])
    matched_ids = [c.chunk_id for c in citations]

    assert "chk_pix_01" in matched_ids
    assert "chk_med_02" in matched_ids
    assert "chk_tar_03" not in matched_ids
    assert len(citations) == 2


def test_extract_citations_indexed_markers() -> None:
    """extract_citations matches 1-based index markers like [^1] and [^2]."""
    c1 = _sample_chunk(chunk_id="chunk_first")
    c2 = _sample_chunk(chunk_id="chunk_second")

    text = "Conforme o artigo inicial [^1], o limite é de R$ 1.000."
    citations = extract_citations(text, [c1, c2])

    assert len(citations) == 1
    assert citations[0].chunk_id == "chunk_first"


def test_extract_citations_fallback_automatic_provenance() -> None:
    """extract_citations automatically attaches candidate chunks if LLM omitted markers."""
    c1 = _sample_chunk(chunk_id="chunk_auto_1")
    c2 = _sample_chunk(chunk_id="chunk_auto_2")

    text = "O limite noturno é R$ 1.000 conforme normas do Banco Central."
    citations = extract_citations(text, [c1, c2])

    assert len(citations) == 2
    assert {c.chunk_id for c in citations} == {"chunk_auto_1", "chunk_auto_2"}


# ---------------------------------------------------------------------------
# 3. VectorSearcher Tests
# ---------------------------------------------------------------------------


def test_vector_searcher_where_clause_building() -> None:
    """_build_where_clause constructs valid Chroma filter dictionaries."""
    searcher = VectorSearcher()

    assert searcher._build_where_clause(None) is None
    assert searcher._build_where_clause(RetrievalFilter()) is None

    f1 = RetrievalFilter(source_type="bacen_norm")
    assert searcher._build_where_clause(f1) == {"source_type": {"$eq": "bacen_norm"}}

    f2 = RetrievalFilter(norm_number="BCB 1/2020")
    assert searcher._build_where_clause(f2) == {"norm_number": {"$eq": "BCB 1/2020"}}

    f3 = RetrievalFilter(source_type="bacen_norm", norm_number="BCB 1/2020")
    expected = {
        "$and": [
            {"source_type": {"$eq": "bacen_norm"}},
            {"norm_number": {"$eq": "BCB 1/2020"}},
        ]
    }
    assert searcher._build_where_clause(f3) == expected


@pytest.mark.asyncio
async def test_vector_searcher_empty_query() -> None:
    """search returns empty list for empty or blank queries."""
    searcher = VectorSearcher()
    assert await searcher.search("") == []
    assert await searcher.search("   ") == []


@pytest.mark.asyncio
async def test_vector_searcher_embedder_failure() -> None:
    """search returns empty list when embedding generation fails."""
    mock_embedder = MagicMock()
    mock_embedder.embed_query = AsyncMock(return_value=[])

    searcher = VectorSearcher(embedder=mock_embedder)
    results = await searcher.search("Qual o limite do Pix?")
    assert results == []


@pytest.mark.asyncio
async def test_vector_searcher_chroma_exception() -> None:
    """search catches and logs vector store query exceptions gracefully."""
    mock_embedder = MagicMock()
    mock_embedder.embed_query = AsyncMock(return_value=[0.1, 0.2, 0.3])

    mock_store = MagicMock()
    mock_store.collection.query.side_effect = RuntimeError("Chroma connection error")

    searcher = VectorSearcher(store=mock_store, embedder=mock_embedder)
    results = await searcher.search("Qual o limite do Pix?")
    assert results == []


@pytest.mark.asyncio
async def test_vector_searcher_filters_by_threshold() -> None:
    """search filters candidates below similarity threshold and sorts descending."""
    mock_embedder = MagicMock()
    mock_embedder.embed_query = AsyncMock(return_value=[0.1, 0.2, 0.3])

    mock_store = MagicMock()
    # Chk1: dist 0.2 -> sim ~0.833 (Pass)
    # Chk2: dist 0.5 -> sim ~0.667 (Pass)
    # Chk3: dist 2.0 -> sim ~0.333 (Filtered out with threshold 0.45)
    mock_store.collection.query.return_value = {
        "ids": [["c1", "c2", "c3"]],
        "documents": [["Doc 1 text", "Doc 2 text", "Doc 3 text"]],
        "metadatas": [
            [
                {"document_id": "d1", "title": "Doc 1"},
                {"document_id": "d2", "title": "Doc 2"},
                {"document_id": "d3", "title": "Doc 3"},
            ]
        ],
        "distances": [[0.2, 0.5, 2.0]],
    }

    searcher = VectorSearcher(
        store=mock_store,
        embedder=mock_embedder,
        similarity_threshold=DEFAULT_SIMILARITY_THRESHOLD,
    )
    results = await searcher.search("Teste query", top_k=3)

    assert len(results) == 2
    assert results[0].chunk_id == "c1"
    assert results[0].similarity_score > results[1].similarity_score
    assert results[1].chunk_id == "c2"


# ---------------------------------------------------------------------------
# 4. Context Block & GroundedSynthesizer Tests
# ---------------------------------------------------------------------------


def test_build_context_block() -> None:
    """build_context_block formats candidates into XML structured string."""
    assert build_context_block([]) == "<contexto>\nNenhum documento disponível.\n</contexto>"

    chunks = [
        _sample_chunk(chunk_id="c1", text="Regra do Pix"),
        _sample_chunk(chunk_id="c2", text="Regra do MED"),
    ]
    xml = build_context_block(chunks)
    assert "<contexto>" in xml
    assert "</contexto>" in xml
    assert "[Trecho 1 - ID: c1]" in xml
    assert "Regra do Pix" in xml
    assert "[Trecho 2 - ID: c2]" in xml


@pytest.mark.asyncio
async def test_synthesizer_empty_chunks() -> None:
    """synthesize returns standard refusal message when context is empty."""
    synthesizer = GroundedSynthesizer()
    answer, has_evidence = await synthesizer.synthesize("Qualquer pergunta", [])

    assert answer == STANDARD_REFUSAL_MESSAGE
    assert has_evidence is False


@pytest.mark.asyncio
async def test_synthesizer_successful_answer() -> None:
    """synthesize passes context to LLM and returns response with evidence."""
    mock_llm = MagicMock()
    mock_llm.generate = AsyncMock(
        return_value="O limite noturno padrão do Pix é R$ 1.000 [^chk_001]."
    )

    synthesizer = GroundedSynthesizer(llm_provider=mock_llm)
    chunks = [_sample_chunk(chunk_id="chk_001")]
    answer, has_evidence = await synthesizer.synthesize(
        "Qual o limite do Pix no período noturno?",
        chunks,
    )

    assert has_evidence is True
    assert "R$ 1.000" in answer
    assert "[^chk_001]" in answer


@pytest.mark.asyncio
async def test_synthesizer_refusal_detection() -> None:
    """synthesize detects when LLM explicitly admits lack of regulatory evidence."""
    mock_llm = MagicMock()
    mock_llm.generate = AsyncMock(
        return_value="Não foram encontradas informações suficientes no contexto regulatório."
    )

    synthesizer = GroundedSynthesizer(llm_provider=mock_llm)
    chunks = [_sample_chunk()]
    answer, has_evidence = await synthesizer.synthesize("Pergunta sem resposta", chunks)

    assert has_evidence is False
    assert "não foram encontradas informações suficientes" in answer.lower()


@pytest.mark.asyncio
async def test_synthesizer_llm_exception() -> None:
    """synthesize handles provider exception and returns safe error message."""
    mock_llm = MagicMock()
    mock_llm.generate = AsyncMock(side_effect=RuntimeError("Timeout connecting to Ollama"))

    synthesizer = GroundedSynthesizer(llm_provider=mock_llm)
    chunks = [_sample_chunk()]
    answer, has_evidence = await synthesizer.synthesize("Pergunta", chunks)

    assert has_evidence is False
    assert "instabilidade ao sintetizar" in answer


# ---------------------------------------------------------------------------
# 5. RAGRetrievalService End-to-End Orchestration Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_service_empty_query() -> None:
    """retrieve_and_answer handles empty query with immediate standard refusal."""
    service = RAGRetrievalService()
    response = await service.retrieve_and_answer("   ")

    assert response.has_sufficient_evidence is False
    assert response.answer == STANDARD_REFUSAL_MESSAGE
    assert response.citations == []
    assert response.confidence_score == 1.0
    assert response.disclaimer == DISCLAIMER_TEXT


@pytest.mark.asyncio
async def test_service_no_candidates_gatekeeper() -> None:
    """retrieve_and_answer short-circuits when no candidate passes similarity threshold."""
    mock_searcher = MagicMock()
    mock_searcher.search = AsyncMock(return_value=[])

    service = RAGRetrievalService(searcher=mock_searcher)
    response = await service.retrieve_and_answer("Pergunta fora de domínio")

    assert response.has_sufficient_evidence is False
    assert response.answer == STANDARD_REFUSAL_MESSAGE
    assert response.citations == []
    assert response.confidence_score == 0.95


@pytest.mark.asyncio
async def test_service_conflict_recency_sorting() -> None:
    """retrieve_and_answer sorts candidates preferring recent publication dates."""
    old_meta = _sample_metadata(
        doc_id="d_old",
        title="Norma Antiga",
        pub_date="2018-01-01",
    )
    new_meta = _sample_metadata(
        doc_id="d_new",
        title="Norma Recente",
        pub_date="2023-10-01",
    )

    c_old = _sample_chunk(chunk_id="c_old", similarity=0.90, metadata=old_meta)
    c_new = _sample_chunk(chunk_id="c_new", similarity=0.80, metadata=new_meta)

    # Initial search returns c_old first due to higher similarity
    mock_searcher = MagicMock()
    mock_searcher.search = AsyncMock(return_value=[c_old, c_new])

    mock_synthesizer = MagicMock()
    mock_synthesizer.synthesize = AsyncMock(
        return_value=("A norma recente [^c_new] prevalece sobre a antiga.", True)
    )

    service = RAGRetrievalService(
        searcher=mock_searcher,
        synthesizer=mock_synthesizer,
    )
    response = await service.retrieve_and_answer("Qual é a regra atual?")

    # Verify synthesizer was called with c_new first because of newer publication date
    called_chunks = mock_synthesizer.synthesize.call_args[1]["chunks"]
    assert called_chunks[0].chunk_id == "c_new"
    assert called_chunks[1].chunk_id == "c_old"

    assert response.has_sufficient_evidence is True
    assert len(response.citations) >= 1
    assert any(c.chunk_id == "c_new" for c in response.citations)
