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
import re
import unicodedata
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


def _as_lowered_terms(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    terms: list[str] = []
    for value in values:
        if not isinstance(value, str):
            continue
        term = value.strip().lower()
        if term:
            terms.append(term)
    return terms


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    no_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    lowered = no_accents.lower()
    return re.sub(r"[^a-z0-9]+", " ", lowered).strip()


def _token_set(value: str) -> set[str]:
    normalized = _normalize_text(value)
    return {tok for tok in normalized.split(" ") if tok}


NUTRITION_TERM_SYNONYMS: dict[str, set[str]] = {
    "pescado": {"pescado", "atun", "atún", "salmon", "salmón", "mariscos"},
    "frutas": {"fruta", "frutas"},
    "lacteos": {"lacteos", "lácteos", "leche", "queso", "yogurt", "yoghurt"},
    "gluten": {"gluten", "trigo", "cebada", "centeno"},
    "nueces": {"nuez", "nueces", "almendra", "almendras", "cacahuate", "mani", "mani"},
}


def _expand_term_tokens(term: str) -> set[str]:
    tokens = _token_set(term)
    expanded: set[str] = set(tokens)
    for token in list(tokens):
        for key, synonyms in NUTRITION_TERM_SYNONYMS.items():
            normalized_key = _normalize_text(key)
            normalized_synonyms = {_normalize_text(s) for s in synonyms}
            if token == normalized_key or token in normalized_synonyms:
                expanded.add(normalized_key)
                expanded.update(normalized_synonyms)
    return expanded


def apply_nutrition_safety_guards(plan: dict, intake_json: dict) -> dict:
    """
    Flag and block obvious dietary conflicts against contraindications/allergies.

    Strategy:
    - Scan each "eat"/"avoid" item+rationale text.
    - If it contains a contraindication/allergy term from intake, remove it from output.
    - Add a safety flag for clinician review.
    """
    diet = plan.get("diet_recommendations")
    if not isinstance(diet, dict):
        return plan

    contraindications = _as_lowered_terms(intake_json.get("contraindications"))
    allergies = _as_lowered_terms(intake_json.get("allergies"))
    blocked_terms = list(dict.fromkeys(contraindications + allergies))
    if not blocked_terms:
        return plan
    blocked_term_tokens = {term: _expand_term_tokens(term) for term in blocked_terms}

    safety_flags: list[dict] = plan.setdefault("nutrition_safety_flags", [])
    for section in ("eat", "avoid"):
        entries = diet.get(section)
        if not isinstance(entries, list):
            diet[section] = []
            continue

        kept: list[dict] = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            text = f"{entry.get('item', '')} {entry.get('rationale', '')}"
            entry_tokens = _token_set(text)
            matched = [
                term
                for term, term_tokens in blocked_term_tokens.items()
                if entry_tokens.intersection(term_tokens)
            ]
            if matched:
                safety_flags.append(
                    {
                        "section": section,
                        "item": str(entry.get("item", "")),
                        "matched_terms": matched,
                        "action": "blocked",
                        "message": "Diet recommendation blocked due to intake contraindication/allergy match.",
                    }
                )
                continue
            kept.append(entry)
        diet[section] = kept

    return plan


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
        plan = apply_nutrition_safety_guards(plan, intake_json)

        return plan
