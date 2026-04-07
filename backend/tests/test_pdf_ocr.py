"""Tests for PDF OCR hybrid path (scanned documents)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from llama_index.core.schema import Document

from app.core.config import get_settings


@pytest.fixture
def clear_settings_cache(monkeypatch):
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_pdf_ocr_available_false_when_tesseract_missing(
    clear_settings_cache, monkeypatch
):
    def _boom():
        raise EnvironmentError("tesseract not found")

    import app.rag.ingestion.pdf_ocr as pdf_ocr_mod

    monkeypatch.setattr(pdf_ocr_mod.pytesseract, "get_tesseract_version", _boom)
    assert pdf_ocr_mod.pdf_ocr_available() is False


def test_hybrid_documents_from_pdf_uses_ocr_when_page_text_empty(
    clear_settings_cache, monkeypatch, tmp_path: Path
):
    monkeypatch.setenv("PDF_OCR_MIN_PAGE_CHARS", "50")
    cfg = get_settings()

    pdf_path = tmp_path / "scan.pdf"
    pdf_path.write_bytes(b"%PDF-1.4")

    mock_page = MagicMock()
    mock_page.get_text.return_value = ""
    mock_pix = MagicMock()
    mock_pix.tobytes.return_value = b"\x89PNG\r\n\x1a\n"
    mock_page.get_pixmap.return_value = mock_pix

    mock_fitz_doc = MagicMock()
    mock_fitz_doc.__len__ = MagicMock(return_value=1)
    mock_fitz_doc.__getitem__ = MagicMock(return_value=mock_page)
    mock_fitz_doc.close = MagicMock()

    with (
        patch("app.rag.ingestion.pdf_ocr.fitz.open", return_value=mock_fitz_doc),
        patch("app.rag.ingestion.pdf_ocr.Image.open", return_value=MagicMock()),
        patch(
            "app.rag.ingestion.pdf_ocr.pytesseract.image_to_string",
            return_value="Texto reconocido por OCR",
        ),
    ):
        from app.rag.ingestion.pdf_ocr import hybrid_documents_from_pdf

        out = hybrid_documents_from_pdf(pdf_path, cfg)

    assert len(out) == 1
    assert "OCR" in out[0].text
    assert out[0].metadata.get("file_name") == "scan.pdf"
    mock_fitz_doc.close.assert_called_once()


def test_document_loader_replaces_thin_file_with_hybrid(
    clear_settings_cache, monkeypatch, tmp_path: Path
):
    monkeypatch.setenv("PDF_OCR_MIN_TEXT_CHARS", "80")
    thin_docs = [
        Document(
            text="x",
            metadata={"file_name": "thin.pdf", "page_label": "1"},
        )
    ]

    class FakeReader:
        def __init__(self, **kwargs):
            pass

        def load_data(self):
            return thin_docs

    hybrid_out = [
        Document(
            text="much longer ocr content for chunking " * 5,
            metadata={"file_name": "thin.pdf", "page_label": "1"},
        )
    ]

    monkeypatch.setattr(
        "app.rag.ingestion.loader.SimpleDirectoryReader", FakeReader
    )
    monkeypatch.setattr(
        "app.rag.ingestion.loader.pdf_ocr_available",
        lambda: True,
    )
    monkeypatch.setattr(
        "app.rag.ingestion.loader.hybrid_documents_from_pdf",
        lambda path, s: hybrid_out if path.name == "thin.pdf" else [],
    )

    from app.rag.ingestion.loader import DocumentLoader

    (tmp_path / "thin.pdf").write_bytes(b"%PDF-1.4")
    out = DocumentLoader().load(str(tmp_path))
    assert len(out) == 1
    assert "ocr" in out[0].text.lower()
