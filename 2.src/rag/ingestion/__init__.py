"""RAG Ingestion components: loaders, chunkers, embedders, vector store, and pipeline (S06)."""

from rag.ingestion.chunkers import RecursiveRegulatoryChunker
from rag.ingestion.embedder import Embedder, OllamaEmbedder
from rag.ingestion.loaders import DocumentLoader, RawDocument
from rag.ingestion.pipeline import IngestionPipeline
from rag.ingestion.store import ChromaVectorStore, VectorStore

__all__ = [
    "ChromaVectorStore",
    "DocumentLoader",
    "Embedder",
    "IngestionPipeline",
    "OllamaEmbedder",
    "RawDocument",
    "RecursiveRegulatoryChunker",
    "VectorStore",
]
