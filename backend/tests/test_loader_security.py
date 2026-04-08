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
    assert set(kwargs["required_exts"]) == {".pdf", ".html", ".htm"}
    assert kwargs["recursive"] is False
    fe = kwargs["file_extractor"]
    assert ".pdf" in fe and ".html" in fe and ".htm" in fe
    assert fe[".html"] is fe[".htm"]

