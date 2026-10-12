"""Vector Store abstraction and ChromaDB local persistent adapter (S06)."""

import logging
from pathlib import Path
from typing import Any, Protocol

import chromadb

from rag.models import DocumentChunk

logger = logging.getLogger(__name__)

DEFAULT_COLLECTION_NAME = "bacen_regulations"
DEFAULT_STORAGE_PATH = Path("2.src/rag/storage/chroma")


class VectorStore(Protocol):
    """Protocol defining the Vector Store interface."""

    def upsert_chunks(self, chunks: list[DocumentChunk]) -> int:
        """Upsert a list of document chunks into the store. Returns count inserted/updated."""
        ...

    def count(self) -> int:
        """Return total number of vector entries in the collection."""
        ...

    def reset(self) -> None:
        """Purge all vectors and reset the collection."""
        ...


class ChromaVectorStore:
    """Persistent local vector database client using ChromaDB."""

    def __init__(
        self,
        storage_path: Path | str = DEFAULT_STORAGE_PATH,
        collection_name: str = DEFAULT_COLLECTION_NAME,
    ) -> None:
        """Initialize the ChromaDB persistent client and collection.

        Args:
            storage_path: Directory path where ChromaDB sqlite/parquet data is persisted.
            collection_name: Name of the target Chroma collection.
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name

        self.client = chromadb.PersistentClient(path=str(self.storage_path))
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "ATLAS Central Bank Regulations and Banking Rules"},
        )

    def upsert_chunks(self, chunks: list[DocumentChunk]) -> int:
        """Upsert chunks idempotently into ChromaDB."""
        if not chunks:
            return 0

        ids: list[str] = []
        embeddings: list[list[float]] = []
        documents: list[str] = []
        metadatas: list[dict[str, Any]] = []

        for chunk in chunks:
            if chunk.embedding is None:
                logger.warning("Skipping chunk %s because embedding is None", chunk.chunk_id)
                continue

            ids.append(chunk.chunk_id)
            embeddings.append(chunk.embedding)
            documents.append(chunk.text)

            meta_dict: dict[str, Any] = {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "token_count": chunk.token_count,
                "title": chunk.metadata.title,
                "source_type": chunk.metadata.source_type,
                "norm_number": chunk.metadata.norm_number or "",
                "publication_date": chunk.metadata.publication_date or "",
                "effective_date": chunk.metadata.effective_date or "",
                "section_title": chunk.metadata.section_title or "",
                "source_url_or_path": chunk.metadata.source_url_or_path,
            }
            metadatas.append(meta_dict)

        if not ids:
            return 0

        from typing import cast

        self.collection.upsert(
            ids=ids,
            embeddings=cast(Any, embeddings),
            documents=documents,
            metadatas=cast(Any, metadatas),
        )
        return len(ids)

    def count(self) -> int:
        """Return total document count in the collection."""
        return int(self.collection.count())

    def reset(self) -> None:
        """Delete and recreate the collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
        except Exception as exc:
            logger.debug("Failed deleting collection during reset: %s", exc)

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "ATLAS Central Bank Regulations and Banking Rules"},
        )
