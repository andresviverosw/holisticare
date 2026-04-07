from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "db"
    postgres_port: int = 5432

    # LLM
    anthropic_api_key: str
    claude_model: str = "claude-sonnet-4-20250514"

    # Embeddings
    openai_api_key: str
    embedding_model: str = "text-embedding-3-small"
    embedding_dims: int = 1536

    # RAG
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k_retrieval: int = 20
    top_k_final: int = 8
    num_query_variants: int = 4
    min_evidence_level: str = "B"

    # PDF ingestion — OCR fallback for scanned / image-heavy pages (PyMuPDF + Tesseract)
    pdf_ocr_fallback_enabled: bool = True
    # If total native text per file is below this, run hybrid OCR for that PDF (chars).
    pdf_ocr_min_text_chars: int = 80
    # Per-page: if native text shorter than this, OCR that page (hybrid path).
    pdf_ocr_min_page_chars: int = 50
    pdf_ocr_lang: str = "spa+eng"
    pdf_ocr_dpi: int = 200

    # Reranker
    reranker_backend: str = "crossencoder"
    crossencoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    cohere_api_key: str | None = None

    # App
    debug: bool = False
    allow_dev_auth: bool = False
    secret_key: str
    cors_origins: str = "http://localhost:5173"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
