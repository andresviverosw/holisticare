from unittest.mock import MagicMock


def test_document_loader_configures_pdf_reader(monkeypatch):
    captured = {}

    class FakeReader:
        def __init__(self, **kwargs):
            captured["kwargs"] = kwargs

        def load_data(self):
            return []

    monkeypatch.setattr("app.rag.ingestion.loader.SimpleDirectoryReader", FakeReader)

    from app.rag.ingestion.loader import DocumentLoader

    out = DocumentLoader().load("data/mock")
    assert out == []

    kwargs = captured["kwargs"]
    assert kwargs["input_dir"] == "data/mock"
    assert kwargs["required_exts"] == [".pdf"]
    assert kwargs["recursive"] is False
    assert ".pdf" in kwargs["file_extractor"]
    assert kwargs["file_extractor"][".pdf"] is not None

