"""Ingestion pipeline orchestrating document loading, chunking, embedding, and indexing (S06)."""

import argparse
import asyncio
import logging
from pathlib import Path

from rag.ingestion.chunkers import RecursiveRegulatoryChunker
from rag.ingestion.embedder import Embedder, OllamaEmbedder
from rag.ingestion.loaders import DocumentLoader, RawDocument
from rag.ingestion.store import ChromaVectorStore, VectorStore
from rag.models import DocumentChunk, IngestionReport

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """End-to-end pipeline for loading, chunking, embedding, and storing banking documents."""

    def __init__(
        self,
        chunker: RecursiveRegulatoryChunker | None = None,
        embedder: Embedder | None = None,
        store: VectorStore | None = None,
    ) -> None:
        """Initialize the pipeline with component adapters."""
        self.chunker = chunker or RecursiveRegulatoryChunker()
        self.embedder = embedder or OllamaEmbedder()
        self.store = store or ChromaVectorStore()

    async def ingest_document(self, document: RawDocument) -> list[DocumentChunk]:
        """Process a single loaded document through chunking, embedding, and indexing."""
        chunks = self.chunker.chunk_document(document)
        if not chunks:
            return []

        # Extract texts and compute vector embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings = await self.embedder.embed_documents(texts)

        for chunk, emb in zip(chunks, embeddings, strict=False):
            chunk.embedding = emb

        self.store.upsert_chunks(chunks)
        return chunks

    async def ingest_file(self, file_path: Path) -> list[DocumentChunk]:
        """Load and ingest a single document file."""
        doc = DocumentLoader.load_file(file_path)
        return await self.ingest_document(doc)

    async def ingest_directory(self, directory_path: Path) -> IngestionReport:
        """Scan a directory, load all documents, and ingest them into the vector store."""
        report = IngestionReport()
        documents = DocumentLoader.scan_directory(directory_path)
        report.total_files_scanned = len(documents)

        for doc in documents:
            try:
                chunks = await self.ingest_document(doc)
                report.total_documents_processed += 1
                report.total_chunks_created += len(chunks)
            except Exception as exc:
                err_msg = f"Failed to ingest {doc.document_id}: {exc}"
                logger.error(err_msg, exc_info=True)
                report.errors.append(err_msg)

        report.total_chunks_indexed = self.store.count()
        return report


async def run_cli() -> None:
    """CLI runner for executing document ingestion."""
    parser = argparse.ArgumentParser(
        description="ATLAS Banking Copilot - RAG Document Ingestion Pipeline"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default="8.docs/knowledge",
        help="Directory containing regulatory documents (Markdown, TXT, PDF)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Purge existing vector database collection before ingesting",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    store = ChromaVectorStore()
    if args.reset:
        logger.info("Resetting collection in vector store...")
        store.reset()

    pipeline = IngestionPipeline(store=store)
    input_path = Path(args.input_dir)
    logger.info("Starting ingestion from directory: %s", input_path.resolve())

    report = await pipeline.ingest_directory(input_path)
    logger.info(
        "Ingestion completed: scanned %d files, processed %d docs, "
        "created %d chunks, total in store: %d",
        report.total_files_scanned,
        report.total_documents_processed,
        report.total_chunks_created,
        report.total_chunks_indexed,
    )


if __name__ == "__main__":
    asyncio.run(run_cli())
