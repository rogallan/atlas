"""Document loaders for Central Bank public regulations and manuals (S06)."""

import re
from dataclasses import dataclass, field
from pathlib import Path

from pypdf import PdfReader

from rag.models import DocumentMetadata


@dataclass
class RawDocument:
    """Represents a loaded raw document prior to chunking."""

    document_id: str
    content: str
    metadata: DocumentMetadata
    sections: list[tuple[str, str]] = field(default_factory=list)


def clean_text(text: str) -> str:
    """Normalize whitespace and remove common OCR/PDF formatting artifacts."""
    # Replace carriage returns
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Replace multiple blank lines with double newline
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Replace multiple horizontal spaces/tabs with single space
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


class DocumentLoader:
    """Unified loader for Markdown, Plain Text, and PDF banking documents."""

    @staticmethod
    def load_markdown(file_path: Path) -> RawDocument:
        """Load and extract metadata from Markdown documents."""
        text = file_path.read_text(encoding="utf-8")
        clean_content = clean_text(text)

        doc_id = file_path.stem
        title = doc_id.replace("-", " ").replace("_", " ").title()
        norm_number: str | None = None
        publication_date: str | None = None
        source_type = "bacen_norm"

        # Check for first heading
        match_heading = re.search(r"^#\s+(.+)$", clean_content, re.MULTILINE)
        if match_heading:
            title = match_heading.group(1).strip()

        # Check for norm number pattern (e.g. Resolução BCB nº 1)
        norm_regex = r"(Resolução\s+(?:BCB\s+)?n[ºo°]?\s*[\d\.\-]+/\d{4})"
        match_norm = re.search(norm_regex, clean_content, re.IGNORECASE)
        if match_norm:
            norm_number = match_norm.group(1).strip()

        # Check for date pattern (YYYY-MM-DD or DD/MM/YYYY)
        match_date = re.search(r"(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})", clean_content)
        if match_date:
            publication_date = match_date.group(1).strip()

        metadata = DocumentMetadata(
            document_id=doc_id,
            title=title,
            source_type=source_type,
            norm_number=norm_number,
            publication_date=publication_date,
            source_url_or_path=str(file_path),
        )
        return RawDocument(
            document_id=doc_id,
            content=clean_content,
            metadata=metadata,
        )

    @staticmethod
    def load_text(file_path: Path) -> RawDocument:
        """Load and extract metadata from plain text files."""
        text = file_path.read_text(encoding="utf-8")
        clean_content = clean_text(text)

        doc_id = file_path.stem
        lines = [line.strip() for line in clean_content.splitlines() if line.strip()]
        title = lines[0] if lines else doc_id.title()

        metadata = DocumentMetadata(
            document_id=doc_id,
            title=title,
            source_type="bacen_norm",
            source_url_or_path=str(file_path),
        )
        return RawDocument(
            document_id=doc_id,
            content=clean_content,
            metadata=metadata,
        )

    @staticmethod
    def load_pdf(file_path: Path) -> RawDocument:
        """Load text and extract metadata from PDF files via pypdf."""
        reader = PdfReader(str(file_path))
        extracted_pages: list[str] = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                extracted_pages.append(page_text.strip())

        full_content = clean_text("\n\n".join(extracted_pages))
        doc_id = file_path.stem

        # Extract title from PDF metadata if present
        title = doc_id.replace("-", " ").replace("_", " ").title()
        if reader.metadata and reader.metadata.title:
            title = str(reader.metadata.title).strip()

        metadata = DocumentMetadata(
            document_id=doc_id,
            title=title,
            source_type="bacen_norm",
            source_url_or_path=str(file_path),
            extra_metadata={"page_count": len(reader.pages)},
        )
        return RawDocument(
            document_id=doc_id,
            content=full_content,
            metadata=metadata,
        )

    @classmethod
    def load_file(cls, file_path: Path) -> RawDocument:
        """Load any supported file by extension."""
        suffix = file_path.suffix.lower()
        if suffix in (".md", ".markdown"):
            return cls.load_markdown(file_path)
        if suffix == ".pdf":
            return cls.load_pdf(file_path)
        if suffix in (".txt", ".text"):
            return cls.load_text(file_path)
        raise ValueError(f"Unsupported document format: {suffix} (supported: .md, .txt, .pdf)")

    @classmethod
    def scan_directory(cls, directory_path: Path) -> list[RawDocument]:
        """Scan a directory for all supported documents and load them."""
        documents: list[RawDocument] = []
        if not directory_path.exists():
            return documents

        for file_path in sorted(directory_path.glob("**/*")):
            if file_path.is_file() and file_path.suffix.lower() in (".md", ".txt", ".pdf"):
                try:
                    documents.append(cls.load_file(file_path))
                except Exception:
                    # Continue scanning other files on error
                    continue
        return documents
