"""RAG Retrieval module: semantic search, citations, and grounded synthesis (S07)."""

from rag.retrieval.citations import create_citation_from_chunk, extract_citations
from rag.retrieval.models import Citation, GroundedResponse, RetrievalFilter, SearchResult
from rag.retrieval.searcher import VectorSearcher
from rag.retrieval.service import RAGRetrievalService
from rag.retrieval.synthesizer import STANDARD_REFUSAL_MESSAGE, GroundedSynthesizer

__all__ = [
    "Citation",
    "GroundedResponse",
    "GroundedSynthesizer",
    "RAGRetrievalService",
    "RetrievalFilter",
    "STANDARD_REFUSAL_MESSAGE",
    "SearchResult",
    "VectorSearcher",
    "create_citation_from_chunk",
    "extract_citations",
]
