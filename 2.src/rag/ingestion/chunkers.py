"""Hierarchical and recursive chunking for Portuguese regulatory texts (S06)."""

import re

from rag.ingestion.loaders import RawDocument
from rag.models import DocumentChunk

DEFAULT_SEPARATORS = [
    "\n## ",
    "\n### ",
    "\n#### ",
    "\nArt. ",
    "\nParágrafo único",
    "\n§ ",
    "\n\n",
    "\n",
    ". ",
    " ",
]


class RecursiveRegulatoryChunker:
    """Splits Portuguese banking and regulatory documents preserving legal boundaries."""

    def __init__(
        self,
        chunk_size: int = 1500,
        chunk_overlap: int = 150,
        separators: list[str] | None = None,
    ) -> None:
        """Initialize the chunker.

        Args:
            chunk_size: Maximum characters per chunk (approx. 350-500 words).
            chunk_overlap: Overlapping character count between consecutive chunks.
            separators: Ordered list of split points from highest semantic level to lowest.
        """
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or list(DEFAULT_SEPARATORS)

    def _split_text(self, text: str, separators: list[str]) -> list[str]:
        """Recursively split text using the given list of separators."""
        if not text.strip():
            return []

        if len(text) <= self.chunk_size:
            return [text.strip()]

        if not separators:
            # Fallback: slice directly if no more separators are available
            return [
                text[i : i + self.chunk_size].strip()
                for i in range(0, len(text), self.chunk_size - self.chunk_overlap)
                if text[i : i + self.chunk_size].strip()
            ]

        current_sep = separators[0]
        remaining_seps = separators[1:]

        # Split using current separator
        if current_sep.startswith("\n") and current_sep.strip():
            # Keep the marker with positive lookahead or split and re-attach
            splits = text.split(current_sep)
            # Reattach separator prefix to subsequent splits
            parts = [splits[0]] + [current_sep.lstrip("\n") + s for s in splits[1:]]
        else:
            parts = text.split(current_sep)

        chunks: list[str] = []
        current_buffer: list[str] = []
        current_len = 0

        for part in parts:
            part_str = part.strip()
            if not part_str:
                continue

            # If an individual part exceeds chunk_size, split it further
            if len(part_str) > self.chunk_size:
                if current_buffer:
                    combined = " ".join(current_buffer).strip()
                    if combined:
                        chunks.append(combined)
                    current_buffer = []
                    current_len = 0

                sub_chunks = self._split_text(part_str, remaining_seps)
                chunks.extend(sub_chunks)
                continue

            projected_len = current_len + len(part_str) + (1 if current_buffer else 0)
            if projected_len <= self.chunk_size:
                current_buffer.append(part_str)
                current_len = projected_len
            else:
                if current_buffer:
                    combined = " ".join(current_buffer).strip()
                    if combined:
                        chunks.append(combined)

                # Implement overlap by keeping suffix of previous buffer
                overlap_buffer: list[str] = []
                overlap_len = 0
                for item in reversed(current_buffer):
                    if overlap_len + len(item) <= self.chunk_overlap:
                        overlap_buffer.insert(0, item)
                        overlap_len += len(item)
                    else:
                        break

                current_buffer = overlap_buffer + [part_str]
                current_len = sum(len(x) for x in current_buffer) + len(current_buffer) - 1

        if current_buffer:
            combined = " ".join(current_buffer).strip()
            if combined:
                chunks.append(combined)

        return chunks

    def chunk_document(self, document: RawDocument) -> list[DocumentChunk]:
        """Split a RawDocument into a list of sequenced DocumentChunk instances."""
        raw_chunks = self._split_text(document.content, self.separators)
        chunks: list[DocumentChunk] = []

        current_section: str | None = None

        for index, text_passage in enumerate(raw_chunks):
            # Try to identify if chunk starts with a section heading
            heading_match = re.search(r"^(?:##|###|####)\s+([^\n]+)", text_passage)
            if heading_match:
                current_section = heading_match.group(1).strip()
            elif text_passage.startswith("Art."):
                art_match = re.search(r"^(Art\.\s*\d+[ºo°]?)", text_passage)
                if art_match:
                    current_section = art_match.group(1).strip()

            chunk_meta = document.metadata.model_copy(update={"section_title": current_section})

            chunk = DocumentChunk.create(
                document_id=document.document_id,
                chunk_index=index,
                text=text_passage,
                metadata=chunk_meta,
            )
            chunks.append(chunk)

        return chunks
