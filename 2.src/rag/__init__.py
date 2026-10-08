"""RAG pipeline: ingestion, chunking, embeddings, indexing, and retrieval."""

from rag.ingestion import (
    ChromaVectorStore,
    DocumentLoader,
    IngestionPipeline,
    OllamaEmbedder,
    RecursiveRegulatoryChunker,
)
from rag.models import DocumentChunk, DocumentMetadata, IngestionReport
from rag.retrieval import (
    Citation,
    GroundedResponse,
    RAGRetrievalService,
    RetrievalFilter,
    VectorSearcher,
)

__all__ = [
    "ChromaVectorStore",
    "Citation",
    "DocumentChunk",
    "DocumentLoader",
    "DocumentMetadata",
    "GroundedResponse",
    "IngestionPipeline",
    "IngestionReport",
    "OllamaEmbedder",
    "RAGRetrievalService",
    "RecursiveRegulatoryChunker",
    "RetrievalFilter",
    "VectorSearcher",
]
