"""US-PRIV-001 — RAGPipeline scrub before LLM; persisted patient_id unchanged."""

import json
import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.rag.pipeline import RAGPipeline
from app.services.patient_anonymizer import PATIENT_TOKEN, AnonymizationError


PATIENT_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"


def _intake_with_pii() -> dict:
    return {
        "patient_id": PATIENT_ID,
        "profile_version": "generic_holistic_v0",
        "chief_complaint": f"Dolor. Email paciente@ejemplo.com UUID {PATIENT_ID}",
        "conditions": ["lumbalgia"],
        "goals": ["mejorar función"],
        "contraindications": [],
        "allergies": [],
    }


@patch("app.rag.generation.generator.complete_claude_or_openai")
@patch("app.rag.generation.query_builder.complete_claude_or_openai")
@patch("app.rag.pipeline.get_reranker")
@patch("app.rag.pipeline.VectorRetriever")
def test_pipeline_llm_calls_omit_patient_identifiers(
    mock_ret_cls, mock_get_rerank, mock_qb_llm, mock_gen_llm
):
    mock_qb_llm.side_effect = ["Resumen clínico anonymizado", '["q1", "q2", "q3", "q4"]']
    mock_gen_llm.return_value = json.dumps(
        {
            "weeks": [],
            "confidence_note": "ok",
            "citations_used": ["REF-A"],
            "diet_recommendations": {"eat": [], "avoid": []},
            "requires_practitioner_review": True,
        }
    )

    mock_ret_cls.return_value.retrieve.return_value = [
        {"ref_id": "REF-A", "text": "evidencia", "metadata": {}}
    ]
    mock_reranker = MagicMock()
    mock_reranker.rerank.return_value = [
        {"ref_id": "REF-A", "text": "evidencia", "metadata": {}, "rerank_score": 0.9}
    ]
    mock_get_rerank.return_value = mock_reranker

    pipeline = RAGPipeline()
    plan = pipeline.generate_plan(
        patient_id=PATIENT_ID,
        intake_json=_intake_with_pii(),
        available_therapies=["fisioterapia"],
        preferred_language="es",
    )

    assert plan["patient_id"] == PATIENT_ID
    assert plan["requires_practitioner_review"] is True
    assert plan.get("retrieval_metadata", {}).get("anonymization_applied") is True

    all_user_payloads = []
    for call in mock_qb_llm.call_args_list + mock_gen_llm.call_args_list:
        kwargs = call.kwargs
        all_user_payloads.append(kwargs.get("user") or (call.args[1] if len(call.args) > 1 else ""))

    joined = "\n".join(str(p) for p in all_user_payloads)
    assert PATIENT_ID not in joined
    assert "paciente@ejemplo.com" not in joined
    assert PATIENT_TOKEN in joined


@patch("app.rag.pipeline.prepare_intake_for_llm")
@patch("app.rag.pipeline.PlanGenerator")
@patch("app.rag.pipeline.get_reranker")
@patch("app.rag.pipeline.VectorRetriever")
@patch("app.rag.pipeline.QueryBuilder")
def test_pipeline_skips_llm_when_anonymization_fails(
    mock_qb_cls, mock_ret_cls, mock_get_rerank, mock_gen_cls, mock_prepare
):
    mock_prepare.side_effect = AnonymizationError("residual PII")
    pipeline = RAGPipeline()
    with pytest.raises(AnonymizationError):
        pipeline.generate_plan(
            patient_id=PATIENT_ID,
            intake_json=_intake_with_pii(),
        )
    mock_qb_cls.return_value.build_clinical_summary.assert_not_called()
    mock_gen_cls.return_value.generate.assert_not_called()
