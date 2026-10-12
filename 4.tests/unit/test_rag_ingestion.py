"""Unit tests for RAG Ingestion: loaders, chunkers, embedder, and vector store (S06)."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from rag.ingestion.chunkers import RecursiveRegulatoryChunker
from rag.ingestion.embedder import OllamaEmbedder
from rag.ingestion.loaders import DocumentLoader, RawDocument, clean_text
from rag.ingestion.pipeline import IngestionPipeline
from rag.ingestion.store import ChromaVectorStore
from rag.models import DocumentChunk, DocumentMetadata, compute_chunk_id


def test_compute_chunk_id_deterministic() -> None:
    """compute_chunk_id must produce identical hashes for identical inputs."""
    h1 = compute_chunk_id("doc-1", 0, "Art. 1º O Pix é um arranjo aberto.")
    h2 = compute_chunk_id("doc-1", 0, "Art. 1º O Pix é um arranjo aberto.")
    h3 = compute_chunk_id("doc-1", 1, "Art. 1º O Pix é um arranjo aberto.")
    h4 = compute_chunk_id("doc-2", 0, "Art. 1º O Pix é um arranjo aberto.")

    assert h1 == h2
    assert h1 != h3
    assert h1 != h4
    assert len(h1) == 32


def test_clean_text() -> None:
    """clean_text normalizes newlines, removes duplicate spaces and blanks."""
    raw = "Art. 1º\r\n\r\n\r\nTexto com   muitos    espaços.\r\n"
    cleaned = clean_text(raw)
    assert cleaned == "Art. 1º\n\nTexto com muitos espaços."


def test_markdown_loader(tmp_path: Path) -> None:
    """DocumentLoader.load_markdown extracts headings, norm number and date."""
    md_file = tmp_path / "resolucao_teste.md"
    md_file.write_text(
        "# Regulamento do Pix\n\n"
        "**Norma de Referência:** Resolução BCB nº 1/2020\n"
        "**Data:** 12/08/2020\n\n"
        "Art. 1º O Pix entra em vigor.",
        encoding="utf-8",
    )

    doc = DocumentLoader.load_markdown(md_file)
    assert doc.document_id == "resolucao_teste"
    assert doc.metadata.title == "Regulamento do Pix"
    assert doc.metadata.norm_number == "Resolução BCB nº 1/2020"
    assert doc.metadata.publication_date == "12/08/2020"
    assert doc.metadata.source_type == "bacen_norm"
    assert "Art. 1º" in doc.content


def test_plain_text_loader(tmp_path: Path) -> None:
    """DocumentLoader.load_text extracts lines and uses first non-empty line as title."""
    txt_file = tmp_path / "manual_credito.txt"
    txt_file.write_text(
        "Manual Operacional de Crédito CDC\n\nRegras de concessão.",
        encoding="utf-8",
    )

    doc = DocumentLoader.load_text(txt_file)
    assert doc.document_id == "manual_credito"
    assert doc.metadata.title == "Manual Operacional de Crédito CDC"
    assert doc.metadata.source_type == "bacen_norm"


def test_unsupported_extension(tmp_path: Path) -> None:
    """Unsupported extensions raise ValueError."""
    bad_file = tmp_path / "arquivo.xlsx"
    bad_file.write_text("teste", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported document format"):
        DocumentLoader.load_file(bad_file)


def test_recursive_regulatory_chunker() -> None:
    """Chunker splits regulatory texts on article/heading boundaries and records metadata."""
    meta = DocumentMetadata(
        document_id="pix-rules",
        title="Regras do Pix",
        source_type="bacen_norm",
        source_url_or_path="pix.md",
    )
    long_content = (
        "## Capítulo I — Do Objeto\n\n"
        "Art. 1º O Pix é um arranjo de pagamento aberto.\n\n"
        "Art. 2º O funcionamento é 24 horas todos os dias.\n\n"
        "## Capítulo II — Da Segurança\n\n"
        "Art. 3º Limite noturno padrão de R$ 1.000,00."
    )
    doc = RawDocument(document_id="pix-rules", content=long_content, metadata=meta)

    chunker = RecursiveRegulatoryChunker(chunk_size=120, chunk_overlap=20)
    chunks = chunker.chunk_document(doc)

    assert len(chunks) >= 2
    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i
        assert chunk.document_id == "pix-rules"
        assert chunk.token_count > 0
        assert chunk.chunk_id is not None
        assert len(chunk.text) <= 150  # reasonable boundary margin


def test_chunker_invalid_overlap() -> None:
    """chunk_overlap >= chunk_size raises ValueError."""
    with pytest.raises(ValueError, match="strictly less"):
        RecursiveRegulatoryChunker(chunk_size=100, chunk_overlap=100)


@pytest.mark.asyncio
async def test_ollama_embedder_query_and_batch() -> None:
    """OllamaEmbedder correctly calls batch endpoint and falls back gracefully."""
    from unittest.mock import MagicMock

    embedder = OllamaEmbedder(batch_size=2)
    fake_vector = [0.1] * 768

    with patch.object(embedder, "_post", new_callable=AsyncMock) as mock_post:
        # Mock batch response
        mock_response = MagicMock()
        mock_response.json.return_value = {"embeddings": [fake_vector, fake_vector]}
        mock_post.return_value = mock_response

        res = await embedder.embed_documents(["texto 1", "texto 2"])
        assert len(res) == 2
        assert len(res[0]) == 768

        # Test embed_query
        mock_single_resp = MagicMock()
        mock_single_resp.json.return_value = {"embedding": fake_vector}
        mock_post.return_value = mock_single_resp
        single = await embedder.embed_query("pesquisa teste")
        assert len(single) == 768


def test_pdf_loader_mock(tmp_path: Path) -> None:
    """DocumentLoader.load_pdf extracts page texts and page count metadata."""
    from unittest.mock import MagicMock

    pdf_file = tmp_path / "resolucao_mock.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 mock content")

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Art. 1º Norma extraída do PDF."

    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]
    mock_reader.metadata.title = "Resolução em PDF"

    with patch("rag.ingestion.loaders.PdfReader", return_value=mock_reader):
        doc = DocumentLoader.load_pdf(pdf_file)
        assert doc.document_id == "resolucao_mock"
        assert doc.metadata.title == "Resolução em PDF"
        assert "Art. 1º" in doc.content
        assert doc.metadata.extra_metadata.get("page_count") == 1


def test_chroma_vector_store_idempotency(tmp_path: Path) -> None:
    """ChromaVectorStore upserts chunks idempotently without duplicating total count."""
    store = ChromaVectorStore(
        storage_path=tmp_path / "chroma_test",
        collection_name="test_collection",
    )
    assert store.count() == 0

    meta = DocumentMetadata(
        document_id="doc-test",
        title="Documento Teste",
        norm_number="Resolução 10",
        source_url_or_path="test.md",
    )
    chunk1 = DocumentChunk.create(
        document_id="doc-test",
        chunk_index=0,
        text="Artigo primeiro sobre normas de juros.",
        metadata=meta,
        embedding=[0.05] * 768,
    )
    chunk2 = DocumentChunk.create(
        document_id="doc-test",
        chunk_index=1,
        text="Artigo segundo sobre portabilidade.",
        metadata=meta,
        embedding=[0.08] * 768,
    )

    # First ingestion
    inserted = store.upsert_chunks([chunk1, chunk2])
    assert inserted == 2
    assert store.count() == 2

    # Second ingestion with the exact same chunks (idempotency check)
    inserted_again = store.upsert_chunks([chunk1, chunk2])
    assert inserted_again == 2
    # CRITICAL: Count must NOT increase!
    assert store.count() == 2

    # Reset collection
    store.reset()
    assert store.count() == 0


@pytest.mark.asyncio
async def test_ingestion_pipeline_end_to_end(tmp_path: Path) -> None:
    """IngestionPipeline processes directory and indexes chunks into vector store."""
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    (knowledge_dir / "doc1.md").write_text(
        "# Pix\n\nArt. 1º Regras gerais do Pix.",
        encoding="utf-8",
    )
    (knowledge_dir / "doc2.md").write_text(
        "# Tarifas\n\nArt. 1º Serviços gratuitos.",
        encoding="utf-8",
    )

    class MockEmbedder:
        async def embed_documents(self, texts: list[str]) -> list[list[float]]:
            return [[0.01] * 768 for _ in texts]

        async def embed_query(self, text: str) -> list[float]:
            return [0.01] * 768

    store = ChromaVectorStore(
        storage_path=tmp_path / "chroma_pipeline",
        collection_name="pipeline_test",
    )
    pipeline = IngestionPipeline(
        embedder=MockEmbedder(),
        store=store,
    )

    report = await pipeline.ingest_directory(knowledge_dir)
    assert report.total_files_scanned == 2
    assert report.total_documents_processed == 2
    assert report.total_chunks_created >= 2
    assert report.total_chunks_indexed >= 2
    assert len(report.errors) == 0
