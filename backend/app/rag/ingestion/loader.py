"""
Ingestion pipeline — Phase 1 of the RAG architecture.

Responsibilities:
- Load PDFs from a source directory
- Detect language per document
- Extract text with page metadata
- Chunk using SentenceSplitter
- Tag each chunk with clinical metadata
"""

import os
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from langdetect import detect, LangDetectException
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document, TextNode

from app.core.config import get_settings

settings = get_settings()


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
        reader = SimpleDirectoryReader(
            input_dir=source_dir,
            required_exts=[".pdf"],
            recursive=False,
        )
        documents = reader.load_data()
        return documents


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
            page_number = int(doc.metadata.get("page_label", 0))
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
