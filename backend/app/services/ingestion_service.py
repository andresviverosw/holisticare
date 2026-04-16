from __future__ import annotations

from pathlib import Path
from typing import Any

from app.rag.ingestion.embedder import Embedder
from app.rag.ingestion.loader import ChunkingPipeline, DocumentLoader


class IngestionService:
    """Orchestrates PDF loading, chunking, and vector indexing."""

    def __init__(self) -> None:
        self.loader = DocumentLoader()
        self.chunker = ChunkingPipeline()
        self.embedder = Embedder()

    def ingest(self, source_dir: str, force_reindex: bool = False) -> dict[str, Any]:
        source_path = Path(source_dir)
        if not source_path.exists() or not source_path.is_dir():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")
        invalid_pdfs = self.loader.find_invalid_pdfs(source_dir)
        if invalid_pdfs:
            raise ValueError(
                "Malformed PDF files detected before ingest: "
                + ", ".join(invalid_pdfs)
                + ". Fix or remove them and retry."
            )

        documents = self.loader.load(source_dir)
        files_processed = len(documents)
        chunks_created = 0
        status = "success"
        # PDFReader yields one Document per page sharing the same file_name; deleting
        # on every page would remove chunks indexed for earlier pages of the same file.
        reindexed_sources: set[str] = set()

        for doc in documents:
            raw_name = doc.metadata.get("file_name", "unknown")
            source_file = (
                Path(raw_name).name if isinstance(raw_name, str) else str(raw_name)
            )
            try:
                if force_reindex and source_file not in reindexed_sources:
                    self.embedder.remove_existing_for_source(source_file)
                    reindexed_sources.add(source_file)
                pairs = self.chunker.process([doc])
                stored = self.embedder.embed_and_store(pairs, source_file)
                self.embedder.log_ingestion(source_file, stored, "success")
                chunks_created += stored
            except Exception as exc:  # keep ingest best-effort per file
                status = "partial"
                self.embedder.log_ingestion(source_file, 0, "failed", str(exc))

        return {
            "files_processed": files_processed,
            "chunks_created": chunks_created,
            "status": status,
        }
