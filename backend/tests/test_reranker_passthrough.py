from app.rag.retrieval.reranker import PassthroughReranker, get_reranker


def test_passthrough_reranker_preserves_vector_order():
    reranker = PassthroughReranker()
    candidates = [
        {"ref_id": "A", "text": "a", "score": 0.5},
        {"ref_id": "B", "text": "b", "score": 0.9},
        {"ref_id": "C", "text": "c", "score": 0.7},
    ]
    out = reranker.rerank("query", candidates, top_k=2)
    assert [c["ref_id"] for c in out] == ["B", "C"]
    assert out[0]["rerank_score"] == 0.9


def test_get_reranker_passthrough_backend(monkeypatch):
    monkeypatch.setattr(
        "app.rag.retrieval.reranker.settings.reranker_backend",
        "passthrough",
    )
    assert isinstance(get_reranker(), PassthroughReranker)
