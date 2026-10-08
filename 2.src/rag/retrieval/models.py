"""Data contracts and schemas for RAG Retrieval and Grounded Synthesis (S07)."""

from pydantic import BaseModel, ConfigDict, Field

from rag.models import DocumentMetadata


class Citation(BaseModel):
    """Verifiable source attribution for claims made in grounded responses."""

    model_config = ConfigDict(extra="ignore")

    chunk_id: str = Field(description="Deterministic ID of the supporting chunk")
    source_title: str = Field(description="Title of parent regulation or document")
    norm_reference: str | None = Field(
        default=None,
        description="Official norm identifier (e.g. Resolução BCB nº 1/2020)",
    )
    section_title: str | None = Field(
        default=None,
        description="Chapter, article or section heading where excerpt appears",
    )
    source_url_or_path: str = Field(description="Document path or source URL")
    excerpt: str = Field(description="Relevant text passage supporting the claim")


class RetrievalFilter(BaseModel):
    """Optional metadata filters applied during vector search."""

    model_config = ConfigDict(extra="ignore")

    source_type: str | None = Field(
        default=None,
        description="Category filter: bacen_norm, resolution, tariff_table, etc.",
    )
    norm_number: str | None = Field(
        default=None,
        description="Exact or prefix match for regulation number",
    )
    min_publication_date: str | None = Field(
        default=None,
        description="Earliest publication date (YYYY-MM-DD or DD/MM/YYYY)",
    )


class SearchResult(BaseModel):
    """A single retrieved chunk candidate with cosine similarity score."""

    model_config = ConfigDict(extra="ignore")

    chunk_id: str = Field(description="Unique chunk identifier")
    document_id: str = Field(description="Parent document identifier")
    text: str = Field(description="Text passage content")
    similarity_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Calculated semantic similarity (1.0 = identical)",
    )
    metadata: DocumentMetadata = Field(description="Complete provenance metadata")


class GroundedResponse(BaseModel):
    """Synthesized response grounded exclusively on retrieved regulatory evidence."""

    model_config = ConfigDict(extra="ignore")

    answer: str = Field(description="Synthesized answer text with inline citation markers")
    has_sufficient_evidence: bool = Field(
        description=(
            "True if context contained sufficient evidence; False if lack of evidence"
        ),
    )
    citations: list[Citation] = Field(
        default_factory=list,
        description="List of verifiable citations backing the answer claims",
    )
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score based on retrieval similarity and model grounding",
    )
    disclaimer: str | None = Field(
        default=None,
        description="Optional regulatory disclaimer (e.g. informational nature)",
    )
