from unittest.mock import MagicMock

from llama_index.core.schema import TextNode

from app.rag.ingestion.embedder import Embedder
from app.rag.ingestion.loader import ChunkMetadata


def test_embedder_skips_empty_text_nodes(monkeypatch):
    emb = Embedder()
    monkeypatch.setattr(emb, "_get_existing_refs", lambda: set())
    mock_model = MagicMock()
    mock_model.get_text_embedding_batch = MagicMock(return_value=[[0.1, 0.2]])
    monkeypatch.setattr(emb, "embed_model", mock_model)
    mock_vs = MagicMock()
    monkeypatch.setattr(emb, "vector_store", mock_vs)

    m1 = ChunkMetadata(
        ref_id="REF-AAA11111",
        source_file="f.pdf",
        page_number=1,
        language="en",
    )
    m2 = ChunkMetadata(
        ref_id="REF-BBB22222",
        source_file="f.pdf",
        page_number=1,
        language="en",
    )
    pairs = [
        (TextNode(text="substantive chunk text here."), m1),
        (TextNode(text="   "), m2),
    ]
    stored = emb.embed_and_store(pairs, "f.pdf")
    assert stored == 1
    mock_model.get_text_embedding_batch.assert_called_once()
    args, _ = mock_model.get_text_embedding_batch.call_args
    assert args[0] == ["substantive chunk text here."]
    mock_vs.add.assert_called_once()
