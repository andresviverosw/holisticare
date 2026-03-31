"""
Embedder — Phase 1.5 of the RAG architecture.

Responsibilities:
- Embed text chunks using OpenAI text-embedding-3-small
- Upsert chunks + embeddings into pgvector via LlamaIndex PGVectorStore
- Track ingestion in ingestion_log table
"""

import psycopg2
from datetime import datetime, timezone

from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core.schema import TextNode

from app.core.config import get_settings
from app.rag.ingestion.loader import ChunkMetadata

settings = get_settings()


def get_embed_model() -> OpenAIEmbedding:
    return OpenAIEmbedding(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )


def get_vector_store() -> PGVectorStore:
    return PGVectorStore.from_params(
        database=settings.postgres_db,
        host=settings.postgres_host,
        port=str(settings.postgres_port),
        user=settings.postgres_user,
        password=settings.postgres_password,
        table_name="clinical_chunks",
        embed_dim=settings.embedding_dims,
    )


class Embedder:
    """Embeds chunks and upserts them into pgvector."""

    def __init__(self):
        self.embed_model = get_embed_model()
        self.vector_store = get_vector_store()

    def embed_and_store(
        self,
        pairs: list[tuple[TextNode, ChunkMetadata]],
        source_file: str,
    ) -> int:
        """
        Embeds all chunks for a document and stores them.
        Returns number of chunks stored.
        Skips chunks whose ref_id already exists (idempotent).
        """
        existing_refs = self._get_existing_refs()
        nodes_to_store = []

        for node, meta in pairs:
            if meta.ref_id in existing_refs:
                continue  # already indexed

            # Attach metadata so LlamaIndex stores it alongside the vector
            node.metadata = {
                "ref_id": meta.ref_id,
                "source_file": meta.source_file,
                "page_number": meta.page_number,
                "language": meta.language,
                "therapy_type": meta.therapy_type,
                "condition": meta.condition,
                "evidence_level": meta.evidence_level,
                "section": meta.section,
                "has_contraindication": meta.has_contraindication,
            }
            nodes_to_store.append(node)

        if not nodes_to_store:
            return 0

        # Embed in batch
        texts = [n.text for n in nodes_to_store]
        embeddings = self.embed_model.get_text_embedding_batch(texts)

        for node, embedding in zip(nodes_to_store, embeddings):
            node.embedding = embedding

        self.vector_store.add(nodes_to_store)
        return len(nodes_to_store)

    def _get_existing_refs(self) -> set[str]:
        """Fetch all ref_ids already in the DB for idempotency check."""
        conn = psycopg2.connect(settings.database_url_sync)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT ref_id FROM clinical_chunks")
                return {row[0] for row in cur.fetchall()}
        finally:
            conn.close()

    def log_ingestion(self, source_file: str, chunk_count: int, status: str, error: str | None = None):
        conn = psycopg2.connect(settings.database_url_sync)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO ingestion_log (source_file, chunk_count, status, error_msg)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (source_file, chunk_count, status, error),
                )
            conn.commit()
        finally:
            conn.close()
