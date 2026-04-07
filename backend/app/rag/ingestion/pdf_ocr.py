"""Hybrid PDF text extraction: native text first, Tesseract OCR for thin pages.

Used when LlamaIndex/PDFReader yields little or no text (common for scanned PDFs).
Requires optional system packages: Tesseract OCR (+ language data), see Dockerfile.
"""

from __future__ import annotations

import io
import logging
from pathlib import Path

import fitz  # PyMuPDF
import pytesseract
from llama_index.core.schema import Document
from PIL import Image

from app.core.config import Settings

logger = logging.getLogger(__name__)


def hybrid_documents_from_pdf(pdf_path: Path, settings: Settings) -> list[Document]:
    """
    Open a PDF with PyMuPDF. For each page, use native text if long enough;
    otherwise render the page and run Tesseract OCR (scanned pages).
    """
    doc = fitz.open(pdf_path)
    out: list[Document] = []
    try:
        for i in range(len(doc)):
            page = doc[i]
            text = page.get_text().strip()
            if len(text) < settings.pdf_ocr_min_page_chars:
                pix = page.get_pixmap(dpi=settings.pdf_ocr_dpi)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                text = pytesseract.image_to_string(
                    img,
                    lang=settings.pdf_ocr_lang,
                ).strip()
            out.append(
                Document(
                    text=text,
                    metadata={
                        "file_name": pdf_path.name,
                        "page_label": str(i + 1),
                    },
                )
            )
    finally:
        doc.close()
    return out


def pdf_ocr_available() -> bool:
    """Best-effort check for Tesseract on PATH (optional)."""
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False
