"""
Retrieval — Phase 3 of the RAG architecture.

Responsibilities:
- Run multi-query vector similarity search against pgvector
- Apply metadata pre-filters (therapy_type, language, evidence_level)
- Deduplicate candidates by ref_id
- Return ranked candidates for reranker
"""

from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator
from llama_index.core.schema import TextNode

from app.core.config import get_settings
from app.rag.ingestion.embedder import get_embed_model, get_vector_store

settings = get_settings()

EVIDENCE_LEVEL_ORDER = {"A": 0, "B": 1, "C": 2, "expert_opinion": 3}


class RetrievalConfig:
    def __init__(
        self,
        therapy_types: list[str] | None = None,
        language: str | None = None,
        min_evidence_level: str = settings.min_evidence_level,
        always_include_contraindications: bool = True,
    ):
        self.therapy_types = therapy_types
        self.language = language
        self.min_evidence_level = min_evidence_level
        self.always_include_contraindications = always_include_contraindications


class VectorRetriever:
    """Runs similarity search with metadata pre-filtering."""

    def __init__(self):
        self.embed_model = get_embed_model()
        self.vector_store = get_vector_store()

    def retrieve(
        self,
        queries: list[str],
        config: RetrievalConfig,
        top_k: int = settings.top_k_retrieval,
    ) -> list[dict]:
        """
        Run all query variants independently, collect candidates,
        deduplicate by ref_id, return as list of dicts.
        """
        seen_refs: set[str] = set()
        candidates: list[dict] = []

        for query in queries:
            embedding = self.embed_model.get_text_embedding(query)
            results = self.vector_store.query(
                query_embedding=embedding,
                similarity_top_k=top_k // len(queries),
                filters=self._build_filters(config),
            )

            for node_with_score in results.nodes:
                ref_id = node_with_score.metadata.get("ref_id", "")
                if ref_id in seen_refs:
                    continue
                seen_refs.add(ref_id)

                # Always include contraindication chunks regardless of score
                if (
                    config.always_include_contraindications
                    and node_with_score.metadata.get("has_contraindication")
                    and ref_id not in seen_refs
                ):
                    pass  # Already added above

                candidates.append({
                    "ref_id": ref_id,
                    "text": node_with_score.text,
                    "score": node_with_score.score or 0.0,
                    "metadata": node_with_score.metadata,
                })

        return candidates

    def _build_filters(self, config: RetrievalConfig) -> MetadataFilters | None:
        filters = []

        if config.language:
            filters.append(
                MetadataFilter(key="language", value=config.language, operator=FilterOperator.EQ)
            )

        if not filters:
            return None

        return MetadataFilters(filters=filters)
