"""Domain models and data contracts for RAG Ingestion and Storage (S06)."""

import hashlib
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def compute_chunk_id(document_id: str, chunk_index: int, text: str) -> str:
    """Compute a deterministic SHA-256 chunk identifier for idempotency.

    Args:
        document_id: Unique document identifier.
        chunk_index: Sequential index of the chunk within the document.
        text: Raw text content of the chunk.

    Returns:
        Hexadecimal SHA-256 hash string (truncated to 32 chars for readability).
    """
    raw_payload = f"{document_id}:{chunk_index}:{text.strip()}"
    return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()[:32]


class DocumentMetadata(BaseModel):
    """Metadata detailing document origin and regulatory provenance."""

    model_config = ConfigDict(extra="ignore")

    document_id: str = Field(description="Unique document identifier (e.g., filename slug)")
    title: str = Field(description="Official document or regulation title")
    source_type: str = Field(
        default="bacen_norm",
        description="Category: bacen_norm, resolution, circular, manual, tariff_table",
    )
    norm_number: str | None = Field(
        default=None,
        description="Official norm or resolution number (e.g., 'Resolução BCB nº 1/2020')",
    )
    publication_date: str | None = Field(
        default=None,
        description="Date of publication (YYYY-MM-DD or standard date string)",
    )
    effective_date: str | None = Field(
        default=None,
        description="Date the regulation enters into effect",
    )
    section_title: str | None = Field(
        default=None,
        description="Heading, chapter, or section name where chunk resides",
    )
    source_url_or_path: str = Field(
        description="Relative file path or original public URL",
    )
    extra_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary additional key-value properties",
    )


class DocumentChunk(BaseModel):
    """A single coherent passage of text with metadata and optional embedding."""

    model_config = ConfigDict(extra="ignore")

    chunk_id: str = Field(description="Deterministic hash identifying the chunk")
    document_id: str = Field(description="Identifier of parent document")
    text: str = Field(description="Extracted chunk text content")
    token_count: int = Field(ge=0, description="Approximate token count of text")
    chunk_index: int = Field(ge=0, description="0-based sequential order in parent document")
    metadata: DocumentMetadata = Field(description="Provenance metadata for citations")
    embedding: list[float] | None = Field(
        default=None,
        description="Dense vector embedding from nomic-embed-text or compatible provider",
    )

    @classmethod
    def create(
        cls,
        document_id: str,
        chunk_index: int,
        text: str,
        metadata: DocumentMetadata,
        embedding: list[float] | None = None,
    ) -> "DocumentChunk":
        """Factory method computing deterministic chunk_id and token count."""
        # Simple heuristic: ~1 token per 4 characters in Portuguese
        approx_tokens = max(1, len(text.split()))
        chunk_id = compute_chunk_id(document_id, chunk_index, text)
        return cls(
            chunk_id=chunk_id,
            document_id=document_id,
            text=text,
            token_count=approx_tokens,
            chunk_index=chunk_index,
            metadata=metadata,
            embedding=embedding,
        )


class IngestionReport(BaseModel):
    """Summary report produced after a pipeline run."""

    model_config = ConfigDict(extra="ignore")

    total_files_scanned: int = 0
    total_documents_processed: int = 0
    total_chunks_created: int = 0
    total_chunks_indexed: int = 0
    errors: list[str] = Field(default_factory=list)
