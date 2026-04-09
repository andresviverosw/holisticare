"""
Ingestion pipeline — Phase 1 of the RAG architecture.

Responsibilities:
- Load PDFs from a source directory
- Detect language per document
- Extract text with page metadata
- Chunk using SentenceSplitter
- Tag each chunk with clinical metadata
"""

import hashlib
import logging
from collections import defaultdict
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from langdetect import detect, LangDetectException
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document, TextNode
from llama_index.readers.file import PDFReader

from app.core.config import Settings, get_settings
from app.rag.ingestion.html_reader import HolisticareHTMLReader
from app.rag.ingestion.pdf_ocr import hybrid_documents_from_pdf, pdf_ocr_available

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class ChunkMetadata:
    ref_id: str
    source_file: str
    page_number: int
    language: str
    therapy_type: list[str] = field(default_factory=list)
    condition: list[str] = field(default_factory=list)
    evidence_level: str = "C"
    section: str = "body"
    has_contraindication: bool = False


def detect_language(text: str) -> str:
    """Detect language of a text chunk. Returns 'en' or 'es', defaults to 'en'."""
    try:
        lang = detect(text)
        return lang if lang in ("en", "es") else "en"
    except LangDetectException:
        return "en"


def metadata_page_number(metadata: dict) -> int:
    """Coerce document metadata page_label to int; empty or invalid → 0."""
    raw = metadata.get("page_label", 0)
    if raw is None:
        return 0
    if isinstance(raw, int):
        return raw
    s = str(raw).strip()
    if not s:
        return 0
    try:
        return int(s)
    except ValueError:
        return 0


def compute_ref_id(source_file: str, page: int, chunk_index: int) -> str:
    """
    Deterministic REF-ID for a chunk. Stable across re-runs so
    citations in stored plans remain valid after re-ingestion.
    """
    key = f"{source_file}::p{page}::c{chunk_index}"
    short = hashlib.sha256(key.encode()).hexdigest()[:8].upper()
    return f"REF-{short}"


def contains_contraindication(text: str) -> bool:
    """
    Heuristic scan for contraindication signals.
    Will be replaced by LLM-based detection in a later phase.
    """
    signals = [
        "contraindica", "contraindicado", "avoid", "evitar",
        "not recommended", "no recomendado", "caution", "precaución",
        "adverse", "adverso", "riesgo", "risk"
    ]
    text_lower = text.lower()
    return any(s in text_lower for s in signals)


class DocumentLoader:
    """Loads and prepares documents from a source directory."""

    def load(self, source_dir: str) -> list[Document]:
        pdf_reader = PDFReader(return_full_document=False)
        html_reader = HolisticareHTMLReader()
        reader = SimpleDirectoryReader(
            input_dir=source_dir,
            required_exts=[".pdf", ".html", ".htm"],
            recursive=False,
            file_extractor={
                ".pdf": pdf_reader,
                ".html": html_reader,
                ".htm": html_reader,
            },
        )
        documents = reader.load_data()
        cfg = get_settings()

        if not cfg.pdf_ocr_fallback_enabled:
            return documents

        source_path = Path(source_dir)
        if not documents:
            return self._load_scanned_only_fallback(source_path, cfg)

        return self._maybe_replace_thin_files(source_path, documents, cfg)

    def _load_scanned_only_fallback(
        self, source_path: Path, cfg: Settings
    ) -> list[Document]:
        """PDFReader returned nothing (common for image-only PDFs). Try hybrid OCR per file."""
        out: list[Document] = []
        for pdf_path in sorted(source_path.glob("*.pdf")):
            if not pdf_ocr_available():
                logger.warning(
                    "No text from PDF reader and Tesseract is not available; skip %s",
                    pdf_path.name,
                )
                continue
            try:
                out.extend(hybrid_documents_from_pdf(pdf_path, cfg))
            except Exception as exc:
                logger.warning("OCR fallback failed for %s: %s", pdf_path.name, exc)
        return out

    def _maybe_replace_thin_files(
        self, source_path: Path, documents: list[Document], cfg: Settings
    ) -> list[Document]:
        """If native extraction yields very little text for a file, re-ingest with hybrid OCR."""
        groups: dict[str, list[Document]] = defaultdict(list)
        for d in documents:
            fn = d.metadata.get("file_name", "unknown")
            if isinstance(fn, str) and ("/" in fn or "\\" in fn):
                fn = Path(fn).name
            groups[str(fn)].append(d)

        result: list[Document] = []
        for fn, group in groups.items():
            total = sum(len(x.text.strip()) for x in group)
            if total >= cfg.pdf_ocr_min_text_chars:
                result.extend(group)
                continue
            if not str(fn).lower().endswith(".pdf"):
                result.extend(group)
                continue
            pdf_path = source_path / fn
            if not pdf_path.is_file():
                result.extend(group)
                continue
            if not pdf_ocr_available():
                logger.warning(
                    "Little text extracted from %s; Tesseract unavailable, keeping native text",
                    fn,
                )
                result.extend(group)
                continue
            try:
                result.extend(hybrid_documents_from_pdf(pdf_path, cfg))
            except Exception as exc:
                logger.warning("OCR fallback failed for %s: %s", fn, exc)
                result.extend(group)
        return result


class ChunkingPipeline:
    """
    Splits documents into chunks and attaches metadata.
    Each chunk becomes one row in clinical_chunks.
    """

    def __init__(self):
        self.splitter = SentenceSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

    def process(self, documents: list[Document]) -> list[tuple[TextNode, ChunkMetadata]]:
        """Returns (node, metadata) pairs ready for embedding."""
        results = []

        for doc in documents:
            source_file = Path(doc.metadata.get("file_name", "unknown")).name
            page_number = metadata_page_number(doc.metadata)
            doc_language = detect_language(doc.text)

            nodes = self.splitter.get_nodes_from_documents([doc])

            for i, node in enumerate(nodes):
                ref_id = compute_ref_id(source_file, page_number, i)
                metadata = ChunkMetadata(
                    ref_id=ref_id,
                    source_file=source_file,
                    page_number=page_number,
                    language=doc_language,
                    has_contraindication=contains_contraindication(node.text),
                    # therapy_type, condition, evidence_level → set manually
                    # or via LLM tagger in a later phase
                )
                results.append((node, metadata))

        return results
