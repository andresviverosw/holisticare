from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.ingestion_service import IngestionService


def _doc(file_name: str) -> SimpleNamespace:
    return SimpleNamespace(metadata={"file_name": file_name})


def test_ingestion_service_force_reindex_removes_existing(monkeypatch, tmp_path):
    service = IngestionService()
    service.loader = MagicMock()
    service.chunker = MagicMock()
    service.embedder = MagicMock()
    service.loader.find_invalid_pdfs.return_value = []
    service.loader.load.return_value = [_doc("a.pdf")]
    service.chunker.process.return_value = [("n1", "m1"), ("n2", "m2")]
    service.embedder.embed_and_store.return_value = 2

    result = service.ingest(str(tmp_path), force_reindex=True)

    assert result["files_processed"] == 1
    assert result["chunks_created"] == 2
    service.embedder.remove_existing_for_source.assert_called_once_with("a.pdf")
    service.embedder.embed_and_store.assert_called_once_with(
        [("n1", "m1"), ("n2", "m2")], "a.pdf"
    )


def test_ingestion_service_force_reindex_deletes_once_per_source_file(tmp_path):
    """Multi-page PDFs load as many documents with the same file_name."""
    service = IngestionService()
    service.loader = MagicMock()
    service.chunker = MagicMock()
    service.embedder = MagicMock()
    service.loader.find_invalid_pdfs.return_value = []
    service.loader.load.return_value = [_doc("a.pdf"), _doc("a.pdf"), _doc("b.pdf")]
    service.chunker.process.return_value = [("n", "m")]
    service.embedder.embed_and_store.return_value = 1

    result = service.ingest(str(tmp_path), force_reindex=True)

    assert result["chunks_created"] == 3
    assert service.embedder.remove_existing_for_source.call_count == 2
    service.embedder.remove_existing_for_source.assert_any_call("a.pdf")
    service.embedder.remove_existing_for_source.assert_any_call("b.pdf")


def test_ingestion_service_partial_when_one_document_fails(tmp_path):
    service = IngestionService()
    service.loader = MagicMock()
    service.chunker = MagicMock()
    service.embedder = MagicMock()
    service.loader.find_invalid_pdfs.return_value = []
    service.loader.load.return_value = [_doc("ok.pdf"), _doc("bad.pdf")]
    service.chunker.process.side_effect = [[("n", "m")], Exception("boom")]
    service.embedder.embed_and_store.return_value = 1

    result = service.ingest(str(tmp_path), force_reindex=False)

    assert result == {"files_processed": 2, "chunks_created": 1, "status": "partial"}
    service.embedder.log_ingestion.assert_any_call("ok.pdf", 1, "success")
    service.embedder.log_ingestion.assert_any_call("bad.pdf", 0, "failed", "boom")


def test_ingestion_service_fails_fast_on_malformed_pdfs(tmp_path):
    service = IngestionService()
    service.loader = MagicMock()
    service.chunker = MagicMock()
    service.embedder = MagicMock()
    service.loader.find_invalid_pdfs.return_value = ["bad.pdf"]

    try:
        service.ingest(str(tmp_path), force_reindex=False)
        raise AssertionError("Expected ValueError for malformed PDF")
    except ValueError as exc:
        assert "bad.pdf" in str(exc)

    service.loader.load.assert_not_called()
    service.chunker.process.assert_not_called()
    service.embedder.embed_and_store.assert_not_called()
