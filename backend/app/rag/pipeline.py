"""
RAGPipeline — the top-level orchestrator.

Wires together all phases:
  intake_json
    → QueryBuilder.build_clinical_summary()
    → QueryBuilder.expand_queries()
    → VectorRetriever.retrieve()
    → Reranker.rerank()
    → PlanGenerator.generate()
    → structured plan dict (stored by API layer)
"""

import uuid
from datetime import datetime, timezone

from app.rag.generation.query_builder import QueryBuilder
from app.rag.retrieval.vector_search import VectorRetriever, RetrievalConfig
from app.rag.retrieval.reranker import get_reranker
from app.rag.generation.generator import PlanGenerator
from app.core.config import get_settings

settings = get_settings()


def build_insufficient_evidence_plan(
    patient_id: str,
    *,
    message_es: str,
    queries_used: list[str] | None,
    candidates_retrieved: int,
    reranker_backend: str,
) -> dict:
    """No LLM plan generation — explicit insufficiency for practitioner review."""
    return {
        "plan_id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "requires_practitioner_review": True,
        "status": "pending_review",
        "insufficient_evidence": True,
        "citations_used": [],
        "weeks": [],
        "confidence_note": message_es,
        "retrieval_metadata": {
            "queries_used": list(queries_used or []),
            "candidates_retrieved": candidates_retrieved,
            "chunks_passed_to_llm": 0,
            "reranker_backend": reranker_backend,
        },
    }


class RAGPipeline:
    def __init__(self):
        self.query_builder = QueryBuilder()
        self.retriever = VectorRetriever()
        self.reranker = get_reranker()
        self.generator = PlanGenerator()

    def generate_plan(
        self,
        patient_id: str,
        intake_json: dict,
        available_therapies: list[str] | None = None,
        preferred_language: str = "es",
        num_weeks: int = 4,
    ) -> dict:
        """
        Full pipeline — from raw intake to structured treatment plan.

        Returns:
            plan dict with status='pending_review', ready for DB insertion.
        """
        # Phase 2 — Query construction
        clinical_summary = self.query_builder.build_clinical_summary(intake_json)
        queries = self.query_builder.expand_queries(clinical_summary)

        # Phase 3 — Retrieval
        config = RetrievalConfig(
            therapy_types=available_therapies,
            language=preferred_language,
        )
        candidates = self.retriever.retrieve(
            queries=queries,
            config=config,
            top_k=settings.top_k_retrieval,
        )

        # Phase 3.2 — Reranking
        # Use the first (symptom-focused) query as the rerank anchor
        anchor_query = queries[0] if queries else clinical_summary
        reranked = self.reranker.rerank(
            query=anchor_query,
            candidates=candidates,
            top_k=settings.top_k_final,
        )

        if not reranked:
            return build_insufficient_evidence_plan(
                patient_id,
                message_es=(
                    "No se recuperó evidencia clínica indexada suficiente para generar un plan "
                    "multisemanal automático. Revise el corpus ingesta o amplíe la consulta. "
                    "El plan puede elaborarse manualmente; este borrador queda solo como registro."
                ),
                queries_used=queries,
                candidates_retrieved=len(candidates),
                reranker_backend=settings.reranker_backend,
            )

        # Phase 4 — Generation
        plan = self.generator.generate(
            patient_id=patient_id,
            clinical_summary=clinical_summary,
            chunks=reranked,
            num_weeks=num_weeks,
            language=preferred_language,
        )

        # Attach retrieval metadata for traceability
        plan["retrieval_metadata"] = {
            "queries_used": queries,
            "candidates_retrieved": len(candidates),
            "chunks_passed_to_llm": len(reranked),
            "reranker_backend": settings.reranker_backend,
        }

        return plan
