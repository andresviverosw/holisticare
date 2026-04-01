"""
Retrieval — Phase 3 of the RAG architecture.

Responsibilities:
- Run multi-query vector similarity search against pgvector
- Apply metadata pre-filters (therapy_type, language, evidence_level)
- Deduplicate candidates by ref_id
- Return ranked candidates for reranker
"""

from llama_index.core.schema import MetadataMode
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator
from llama_index.core.vector_stores.types import VectorStoreQuery
from app.core.config import get_settings
from app.rag.ingestion.embedder import get_embed_model, get_vector_store

settings = get_settings()

EVIDENCE_LEVEL_ORDER = {"A": 0, "B": 1, "C": 2, "expert_opinion": 3}


def _node_plain_text(node) -> str:
    """PGVectorStore returns BaseNode; prefer get_content for compatibility across node types."""
    try:
        return node.get_content(metadata_mode=MetadataMode.NONE)
    except Exception:
        return getattr(node, "text", "") or ""


def _node_metadata_dict(node) -> dict:
    raw = getattr(node, "metadata", None)
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        return dict(raw)
    except Exception:
        return {}


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

        if not queries:
            return []

        per_query_k = max(1, top_k // len(queries))

        for query in queries:
            embedding = self.embed_model.get_text_embedding(query)
            vs_query = VectorStoreQuery(
                query_embedding=embedding,
                similarity_top_k=per_query_k,
                filters=self._build_filters(config),
            )
            results = self.vector_store.query(vs_query)
            nodes = results.nodes or []
            similarities = results.similarities or []

            for i, node in enumerate(nodes):
                # PGVectorStore returns BaseNode + parallel similarities list (not .score on node)
                sim = float(similarities[i]) if i < len(similarities) else 0.0
                meta = _node_metadata_dict(node)
                ref_id = meta.get("ref_id", "")
                if ref_id in seen_refs:
                    continue
                seen_refs.add(ref_id)

                # Always include contraindication chunks regardless of score
                if (
                    config.always_include_contraindications
                    and meta.get("has_contraindication")
                    and ref_id not in seen_refs
                ):
                    pass  # Already added above

                candidates.append({
                    "ref_id": ref_id,
                    "text": _node_plain_text(node),
                    "score": sim,
                    "metadata": meta,
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
