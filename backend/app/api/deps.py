"""FastAPI dependencies — override in tests via app.dependency_overrides for CI-safe runs."""

from app.rag.pipeline import RAGPipeline
from app.services.ingestion_service import IngestionService


def get_rag_pipeline() -> RAGPipeline:
    """Default: real pipeline (requires DB + APIs unless subsystems are mocked)."""
    return RAGPipeline()


def get_ingestion_service() -> IngestionService:
    """Default: real ingestion service (can be overridden in tests)."""
    return IngestionService()
