"""
Reranker — Phase 3.2 of the RAG architecture.

Provides a unified Reranker interface with two backends:
- CrossEncoderReranker (default, free): sentence-transformers ms-marco-MiniLM-L-6-v2
- CohereReranker (optional, paid): Cohere Rerank v3

Backend is selected via RERANKER_BACKEND env var.
"""

from abc import ABC, abstractmethod
from app.core.config import get_settings

settings = get_settings()


class BaseReranker(ABC):
    @abstractmethod
    def rerank(self, query: str, candidates: list[dict], top_k: int) -> list[dict]:
        """
        Args:
            query: The original or representative query string
            candidates: list of {ref_id, text, score, metadata}
            top_k: number of results to return

        Returns:
            Top-k candidates sorted by rerank score descending,
            each with an added 'rerank_score' key.
        """


class CrossEncoderReranker(BaseReranker):
    """
    Free reranker using sentence-transformers cross-encoder.
    Model: cross-encoder/ms-marco-MiniLM-L-6-v2
    Loaded once at startup (singleton pattern).
    """

    _model = None  # class-level cache

    def __init__(self):
        if CrossEncoderReranker._model is None:
            from sentence_transformers import CrossEncoder
            CrossEncoderReranker._model = CrossEncoder(settings.crossencoder_model)
        self.model = CrossEncoderReranker._model

    def rerank(self, query: str, candidates: list[dict], top_k: int) -> list[dict]:
        if not candidates:
            return []

        pairs = [(query, c["text"]) for c in candidates]
        scores = self.model.predict(pairs)

        for candidate, score in zip(candidates, scores):
            candidate["rerank_score"] = float(score)

        reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
        return reranked[:top_k]


class CohereReranker(BaseReranker):
    """
    Paid reranker using Cohere Rerank v3.
    Requires COHERE_API_KEY in environment.
    """

    def __init__(self):
        import cohere
        if not settings.cohere_api_key:
            raise ValueError("COHERE_API_KEY must be set to use CohereReranker")
        self.client = cohere.Client(settings.cohere_api_key)

    def rerank(self, query: str, candidates: list[dict], top_k: int) -> list[dict]:
        if not candidates:
            return []

        docs = [c["text"] for c in candidates]
        response = self.client.rerank(
            query=query,
            documents=docs,
            top_n=top_k,
            model="rerank-multilingual-v3.0",  # supports EN + ES
        )

        reranked = []
        for result in response.results:
            candidate = candidates[result.index].copy()
            candidate["rerank_score"] = result.relevance_score
            reranked.append(candidate)

        return reranked


def get_reranker() -> BaseReranker:
    """Factory — returns the correct reranker based on config."""
    backend = settings.reranker_backend.lower()
    if backend == "cohere":
        return CohereReranker()
    return CrossEncoderReranker()
