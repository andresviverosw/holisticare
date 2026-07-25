"""US-PRIV-001 — pipeline passes scrubbed intake to LLM stages; keeps real patient_id."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.rag.pipeline import RAGPipeline
from app.services.patient_anonymizer import PATIENT_TOKEN


@patch("app.rag.pipeline.PlanGenerator")
@patch("app.rag.pipeline.get_reranker")
@patch("app.rag.pipeline.VectorRetriever")
@patch("app.rag.pipeline.QueryBuilder")
def test_generate_plan_sends_anonymized_intake_to_query_builder(
    mock_qb_cls, mock_vr_cls, mock_rerank_cls, mock_gen_cls
):
    pid = "550e8400-e29b-41d4-a716-446655440000"
    qb = mock_qb_cls.return_value
    qb.build_clinical_summary.return_value = "summary"
    qb.expand_queries.return_value = ["q1"]

    mock_vr_cls.return_value.retrieve.return_value = [{"ref_id": "REF-1", "text": "c"}]
    mock_rerank_cls.return_value.rerank.return_value = [{"ref_id": "REF-1", "text": "c"}]
    mock_gen_cls.return_value.generate.return_value = {
        "plan_id": "p",
        "patient_id": pid,
        "generated_at": "now",
        "requires_practitioner_review": True,
        "status": "pending_review",
        "citations_used": ["REF-1"],
        "weeks": [],
        "confidence_note": "ok",
        "diet_recommendations": {"eat": [], "avoid": []},
    }

    pipe = RAGPipeline()
    result = pipe.generate_plan(
        patient_id=pid,
        intake_json={
            "patient_id": pid,
            "profile_version": "generic_holistic_v0",
            "chief_complaint": "dolor; email leak@test.com",
            "conditions": ["lumbalgia"],
            "goals": ["mejorar"],
            "email": "should-drop@x.com",
        },
    )

    safe = qb.build_clinical_summary.call_args.args[0]
    assert "patient_id" not in safe
    assert "email" not in safe
    assert "leak@test.com" not in str(safe)
    assert safe["chief_complaint"].find("[REDACTED_EMAIL]") >= 0

    gen_kw = mock_gen_cls.return_value.generate.call_args.kwargs
    assert gen_kw["patient_id"] == pid
    assert result["patient_id"] == pid
    assert result["retrieval_metadata"]["anonymization_applied"] is True


def test_generator_prompt_uses_patient_token_not_raw_id(monkeypatch):
    from app.rag.generation import generator as gen_mod

    captured: dict = {}

    def fake_complete(*, system, user, max_tokens):
        captured["user"] = user
        return """{
          "plan_id": "x",
          "patient_id": "ignored",
          "generated_at": "t",
          "requires_practitioner_review": true,
          "status": "pending_review",
          "insufficient_evidence": false,
          "citations_used": ["REF-1"],
          "weeks": [],
          "confidence_note": "ok",
          "diet_recommendations": {"eat": [], "avoid": []}
        }"""

    monkeypatch.setattr(gen_mod, "complete_claude_or_openai", fake_complete)
    g = gen_mod.PlanGenerator()
    real_pid = "550e8400-e29b-41d4-a716-446655440000"
    plan = g.generate(
        patient_id=real_pid,
        clinical_summary="summary",
        chunks=[{"ref_id": "REF-1", "text": "evidence"}],
        num_weeks=2,
        language="es",
    )
    assert real_pid not in captured["user"]
    assert PATIENT_TOKEN in captured["user"]
    assert plan["patient_id"] == real_pid
