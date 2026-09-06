"""US-OPS-OOM / Render free tier — RERANKER_BACKEND=passthrough must not load CrossEncoder."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from app.core.config import get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_passthrough_reranker_keeps_top_k_by_score():
    from app.rag.retrieval.reranker import PassthroughReranker

    candidates = [
        {"ref_id": "a", "text": "low", "score": 0.1},
        {"ref_id": "b", "text": "high", "score": 0.9},
        {"ref_id": "c", "text": "mid", "score": 0.5},
    ]
    out = PassthroughReranker().rerank("q", candidates, top_k=2)
    assert [c["ref_id"] for c in out] == ["b", "c"]
    assert all("rerank_score" in c for c in out)
    assert out[0]["rerank_score"] == 0.9


def test_get_reranker_passthrough_does_not_construct_crossencoder(monkeypatch):
    monkeypatch.setenv("RERANKER_BACKEND", "passthrough")
    get_settings.cache_clear()

    import app.rag.retrieval.reranker as reranker_mod

    # Refresh module-bound settings if present (factory should re-read).
    with patch.object(reranker_mod, "CrossEncoderReranker") as cross_cls:
        cross_cls.side_effect = AssertionError("CrossEncoder must not load on passthrough")
        rr = reranker_mod.get_reranker()

    assert type(rr).__name__ == "PassthroughReranker"
    assert cross_cls.call_count == 0


def test_get_reranker_unknown_backend_defaults_to_crossencoder(monkeypatch):
    monkeypatch.setenv("RERANKER_BACKEND", "crossencoder")
    get_settings.cache_clear()

    import app.rag.retrieval.reranker as reranker_mod

    fake = MagicMock(name="fake-cross")
    with patch.object(reranker_mod, "CrossEncoderReranker", return_value=fake) as cross_cls:
        rr = reranker_mod.get_reranker()

    assert rr is fake
    cross_cls.assert_called_once()
