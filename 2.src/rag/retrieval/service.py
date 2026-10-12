"""High-level RAG Retrieval and Grounded Synthesis Service (S07)."""

import logging

from rag.retrieval.citations import extract_citations
from rag.retrieval.models import GroundedResponse, RetrievalFilter
from rag.retrieval.searcher import VectorSearcher
from rag.retrieval.synthesizer import STANDARD_REFUSAL_MESSAGE, GroundedSynthesizer

logger = logging.getLogger(__name__)

DISCLAIMER_TEXT = (
    "Aviso Regulatório: Resposta gerada automaticamente com base em normas públicas "
    "do Banco Central do Brasil e SUSEP para fins consultivos."
)


class RAGRetrievalService:
    """End-to-end service coordinating semantic search, grounding, and citation linking."""

    def __init__(
        self,
        searcher: VectorSearcher | None = None,
        synthesizer: GroundedSynthesizer | None = None,
    ) -> None:
        """Initialize the RAG retrieval service.

        Args:
            searcher: VectorSearcher component.
            synthesizer: GroundedSynthesizer component.
        """
        self.searcher = searcher or VectorSearcher()
        self.synthesizer = synthesizer or GroundedSynthesizer()

    async def retrieve_and_answer(
        self,
        query: str,
        filters: RetrievalFilter | None = None,
        top_k: int = 4,
    ) -> GroundedResponse:
        """Execute semantic search and synthesize an evidence-grounded response.

        Args:
            query: User's banking regulatory inquiry.
            filters: Optional metadata filtering criteria.
            top_k: Maximum candidate passages to retrieve.

        Returns:
            GroundedResponse with verified citations or explicit refusal.
        """
        clean_query = query.strip()
        if not clean_query:
            return GroundedResponse(
                answer=STANDARD_REFUSAL_MESSAGE,
                has_sufficient_evidence=False,
                citations=[],
                confidence_score=1.0,
                disclaimer=DISCLAIMER_TEXT,
            )

        # 1. Semantic search with threshold gatekeeping
        candidates = await self.searcher.search(
            query=clean_query,
            top_k=top_k,
            filters=filters,
        )

        # 2. Gatekeeper: if no candidate chunks passed threshold, short-circuit
        if not candidates:
            logger.info("No candidates passed similarity threshold for query: '%s'", clean_query)
            return GroundedResponse(
                answer=STANDARD_REFUSAL_MESSAGE,
                has_sufficient_evidence=False,
                citations=[],
                confidence_score=0.95,
                disclaimer=DISCLAIMER_TEXT,
            )

        # 3. Conflict resolution & recency ordering:
        # prefer candidates with more recent publication dates
        candidates.sort(
            key=lambda c: (
                c.metadata.publication_date or "",
                c.similarity_score,
            ),
            reverse=True,
        )

        # 4. Synthesize response
        answer, has_evidence = await self.synthesizer.synthesize(
            query=clean_query,
            chunks=candidates,
        )

        # 5. Extract and link citations
        citations = extract_citations(answer, candidates) if has_evidence else []

        # 6. Compute composite confidence score
        avg_sim = sum(c.similarity_score for c in candidates) / len(candidates)
        confidence = round(avg_sim, 2) if has_evidence else 0.95

        return GroundedResponse(
            answer=answer,
            has_sufficient_evidence=has_evidence,
            citations=citations,
            confidence_score=confidence,
            disclaimer=DISCLAIMER_TEXT,
        )
