"""Semantic search engine querying the local Vector Store with metadata filters (S07)."""

import logging
from typing import Any, cast

from rag.ingestion.embedder import Embedder, OllamaEmbedder
from rag.ingestion.store import ChromaVectorStore
from rag.models import DocumentMetadata
from rag.retrieval.models import RetrievalFilter, SearchResult

logger = logging.getLogger(__name__)

DEFAULT_SIMILARITY_THRESHOLD = 0.45


def distance_to_similarity(distance: float) -> float:
    """Convert vector space distance to normalized similarity score in [0.0, 1.0]."""
    if distance < 0.0:
        return 1.0
    # Inverse distance transformation
    similarity = 1.0 / (1.0 + distance)
    return round(max(0.0, min(1.0, similarity)), 4)


class VectorSearcher:
    """Executes semantic similarity search over indexed banking document chunks."""

    def __init__(
        self,
        store: ChromaVectorStore | None = None,
        embedder: Embedder | None = None,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ) -> None:
        """Initialize the vector searcher.

        Args:
            store: ChromaVectorStore instance.
            embedder: Concrete Embedder implementation.
            similarity_threshold: Minimum similarity required for a chunk to be considered relevant.
        """
        self.store = store or ChromaVectorStore()
        self.embedder = embedder or OllamaEmbedder()
        self.similarity_threshold = similarity_threshold

    def _build_where_clause(self, filters: RetrievalFilter | None) -> dict[str, Any] | None:
        """Build Chroma where-clause dictionary from RetrievalFilter."""
        if not filters:
            return None

        clauses: list[dict[str, Any]] = []
        if filters.source_type:
            clauses.append({"source_type": {"$eq": filters.source_type}})
        if filters.norm_number:
            clauses.append({"norm_number": {"$eq": filters.norm_number}})

        if not clauses:
            return None
        if len(clauses) == 1:
            return clauses[0]
        return {"$and": clauses}

    async def search(
        self,
        query: str,
        top_k: int = 4,
        filters: RetrievalFilter | None = None,
    ) -> list[SearchResult]:
        """Search the vector store for document chunks semantically relevant to query.

        Args:
            query: User's question or search query string.
            top_k: Maximum number of candidate chunks to return.
            filters: Optional metadata filtering criteria.

        Returns:
            Ranked list of SearchResult objects above the similarity threshold.
        """
        clean_query = query.strip()
        if not clean_query:
            return []

        # 1. Generate query embedding
        query_vector = await self.embedder.embed_query(clean_query)
        if not query_vector:
            return []

        where_clause = self._build_where_clause(filters)

        # 2. Query Chroma collection
        try:
            results = self.store.collection.query(
                query_embeddings=cast(Any, [query_vector]),
                n_results=top_k,
                where=where_clause,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            logger.error("Vector store query failed: %s", exc, exc_info=True)
            return []

        # 3. Parse and filter results
        query_results = cast(dict[str, Any], results)
        ids_list = (query_results.get("ids") or [[]])[0]
        docs_list = (query_results.get("documents") or [[]])[0]
        metas_list = (query_results.get("metadatas") or [[]])[0]
        dists_list = (query_results.get("distances") or [[]])[0]

        search_results: list[SearchResult] = []

        for chunk_id, text, meta, dist in zip(
            ids_list, docs_list, metas_list, dists_list, strict=False
        ):
            sim_score = distance_to_similarity(float(dist))

            if sim_score < self.similarity_threshold:
                logger.debug(
                    "Skipping chunk %s with similarity %.4f below threshold %.4f",
                    chunk_id,
                    sim_score,
                    self.similarity_threshold,
                )
                continue

            metadata = DocumentMetadata(
                # pyrefly: ignore [bad-argument-type]
                document_id=meta.get("document_id", "unknown"),
                # pyrefly: ignore [bad-argument-type]
                title=meta.get("title", "Documento Sem Título"),
                # pyrefly: ignore [bad-argument-type]
                source_type=meta.get("source_type", "bacen_norm"),
                # pyrefly: ignore [bad-argument-type]
                norm_number=meta.get("norm_number") or None,
                # pyrefly: ignore [bad-argument-type]
                publication_date=meta.get("publication_date") or None,
                # pyrefly: ignore [bad-argument-type]
                effective_date=meta.get("effective_date") or None,
                # pyrefly: ignore [bad-argument-type]
                section_title=meta.get("section_title") or None,
                # pyrefly: ignore [bad-argument-type]
                source_url_or_path=meta.get("source_url_or_path", ""),
            )

            result = SearchResult(
                chunk_id=chunk_id,
                document_id=metadata.document_id,
                text=text,
                similarity_score=sim_score,
                metadata=metadata,
            )
            search_results.append(result)

        # Sort descending by similarity score
        search_results.sort(key=lambda x: x.similarity_score, reverse=True)
        return search_results
