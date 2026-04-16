"""HTML document loading for RAG ingestion."""

from pathlib import Path

import pytest

from app.core.config import get_settings
from app.rag.ingestion.html_reader import HolisticareHTMLReader, html_file_to_text
from app.rag.ingestion.loader import DocumentLoader


def test_html_file_to_text_strips_scripts_and_styles(tmp_path: Path):
    p = tmp_path / "a.html"
    p.write_text(
        """<!DOCTYPE html><html><head><style>.x{display:none}</style></head>
        <body><script>alert(1)</script><p>Visible clinical text.</p></body></html>""",
        encoding="utf-8",
    )
    text = html_file_to_text(p)
    assert "Visible clinical" in text
    assert "alert" not in text
    assert "display" not in text


def test_holisticare_html_reader_produces_one_document_with_metadata(tmp_path: Path):
    p = tmp_path / "guide.html"
    p.write_text("<html><body><p>Paragraph one.</p></body></html>", encoding="utf-8")
    docs = HolisticareHTMLReader().load_data(p)
    assert len(docs) == 1
    assert "Paragraph" in docs[0].text
    assert docs[0].metadata.get("file_name") == "guide.html"
    assert docs[0].metadata.get("page_label") == "1"


@pytest.fixture
def ocr_off(monkeypatch):
    monkeypatch.setenv("PDF_OCR_FALLBACK_ENABLED", "false")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_document_loader_registers_pdf_and_html_extensions(
    monkeypatch, tmp_path: Path, ocr_off
):
    captured = {}

    class FakeReader:
        def __init__(self, **kwargs):
            captured["kwargs"] = kwargs

        def load_data(self):
            return []

    monkeypatch.setattr("app.rag.ingestion.loader.SimpleDirectoryReader", FakeReader)

    DocumentLoader().load(str(tmp_path))

    kwargs = captured["kwargs"]
    assert kwargs["input_dir"] == str(tmp_path)
    assert set(kwargs["required_exts"]) == {".pdf", ".html", ".htm"}
    assert kwargs["recursive"] is False
    fe = kwargs["file_extractor"]
    assert ".pdf" in fe and ".html" in fe and ".htm" in fe
    assert fe[".html"] is fe[".htm"]


def test_document_loader_end_to_end_html(tmp_path: Path, ocr_off):
    (tmp_path / "note.html").write_text(
        "<html><body><p>Rehab guidance for lumbar pain.</p></body></html>",
        encoding="utf-8",
    )
    docs = DocumentLoader().load(str(tmp_path))
    assert len(docs) == 1
    assert "lumbar" in docs[0].text
    assert docs[0].metadata.get("file_name") == "note.html"


def test_document_loader_find_invalid_pdfs_detects_bad_header_and_eof(tmp_path: Path):
    good = tmp_path / "good.pdf"
    good.write_bytes(b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\n%%EOF")
    bad_header = tmp_path / "bad-header.pdf"
    bad_header.write_bytes(b"not-a-pdf")
    bad_eof = tmp_path / "bad-eof.pdf"
    bad_eof.write_bytes(b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\n")

    invalid = DocumentLoader().find_invalid_pdfs(str(tmp_path))
    assert invalid == ["bad-eof.pdf", "bad-header.pdf"]
