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
        _ = force_reindex  # reserved for future reindex strategy
        source_path = Path(source_dir)
        if not source_path.exists() or not source_path.is_dir():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")

        documents = self.loader.load(source_dir)
        files_processed = len(documents)
        chunks_created = 0
        status = "success"

        for doc in documents:
            source_file = doc.metadata.get("file_name", "unknown")
            try:
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
