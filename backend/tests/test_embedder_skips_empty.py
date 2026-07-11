from unittest.mock import MagicMock

import psycopg2
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


def test_get_existing_refs_returns_empty_when_pgvector_table_missing(monkeypatch):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_cur.execute.side_effect = psycopg2.errors.UndefinedTable(
        'relation "data_clinical_chunks" does not exist'
    )
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_conn.cursor.return_value.__exit__.return_value = False

    monkeypatch.setattr(
        "app.rag.ingestion.embedder.psycopg2.connect",
        lambda *_args, **_kwargs: mock_conn,
    )

    embedder = Embedder.__new__(Embedder)
    assert embedder._get_existing_refs() == set()
    mock_conn.rollback.assert_called_once()


def test_remove_existing_for_source_noop_when_pgvector_table_missing(monkeypatch):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_cur.execute.side_effect = psycopg2.errors.UndefinedTable(
        'relation "data_clinical_chunks" does not exist'
    )
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_conn.cursor.return_value.__exit__.return_value = False

    monkeypatch.setattr(
        "app.rag.ingestion.embedder.psycopg2.connect",
        lambda *_args, **_kwargs: mock_conn,
    )

    embedder = Embedder.__new__(Embedder)
    assert embedder.remove_existing_for_source("ci_reference.html") == 0
    mock_conn.rollback.assert_called_once()
