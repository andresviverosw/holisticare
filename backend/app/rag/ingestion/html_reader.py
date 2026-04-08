"""Load HTML files as plain text for RAG (scripts/styles stripped)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fsspec import AbstractFileSystem
from llama_index.core.readers.base import BaseReader
from llama_index.core.readers.file.base import get_default_fs, is_default_fs
from llama_index.core.schema import Document


def html_file_to_text(path: Path) -> str:
    """Extract visible text from HTML; drop script/style/noscript."""
    from bs4 import BeautifulSoup

    raw = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    body = soup.find("body")
    root = body if body else soup
    text = root.get_text(separator="\n", strip=True)
    return "\n".join(line for line in text.splitlines() if line.strip())


class HolisticareHTMLReader(BaseReader):
    """
    One Document per HTML file (no page split). Metadata aligns with PDF chunks:
    ``file_name``, ``page_label`` = 1.
    """

    def __init__(self) -> None:
        super().__init__()

    def load_data(
        self,
        file: Union[Path, str],
        extra_info: Optional[Dict[str, Any]] = None,
        fs: Optional[AbstractFileSystem] = None,
    ) -> List[Document]:
        fs = fs or get_default_fs()
        if not isinstance(file, Path):
            file = Path(file)
        if not is_default_fs(fs):
            raise NotImplementedError("Non-default fs not supported for HTML reader")

        path = file
        text = html_file_to_text(path)
        metadata: Dict[str, Any] = {
            "file_name": path.name,
            "page_label": "1",
        }
        if extra_info:
            metadata.update(extra_info)
        return [Document(text=text, metadata=metadata)]
