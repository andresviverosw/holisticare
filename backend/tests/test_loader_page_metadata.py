from llama_index.core.schema import Document

from app.rag.ingestion.loader import ChunkingPipeline, metadata_page_number


def test_metadata_page_number_empty_string():
    assert metadata_page_number({"page_label": ""}) == 0


def test_metadata_page_number_whitespace():
    assert metadata_page_number({"page_label": "  \t  "}) == 0


def test_metadata_page_number_valid_string():
    assert metadata_page_number({"page_label": "12"}) == 12


def test_metadata_page_number_int():
    assert metadata_page_number({"page_label": 5}) == 5


def test_metadata_page_number_invalid_string_falls_back_to_zero():
    assert metadata_page_number({"page_label": "iv"}) == 0


def test_chunking_pipeline_accepts_empty_page_label():
    pipeline = ChunkingPipeline()
    filler = "hello world. " * 80
    doc = Document(
        text=filler,
        metadata={"file_name": "chart.pdf", "page_label": ""},
    )
    pairs = pipeline.process([doc])
    assert pairs
    assert all(m.page_number == 0 for _, m in pairs)
