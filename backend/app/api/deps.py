"""FastAPI dependencies — override in tests via app.dependency_overrides for CI-safe runs."""

from app.rag.pipeline import RAGPipeline


def get_rag_pipeline() -> RAGPipeline:
    """Default: real pipeline (requires DB + APIs unless subsystems are mocked)."""
    return RAGPipeline()
