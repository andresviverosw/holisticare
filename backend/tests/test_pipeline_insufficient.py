"""RAGPipeline returns insufficient-evidence plan when retrieval yields no chunks."""

from unittest.mock import MagicMock, patch

from app.rag.pipeline import RAGPipeline


@patch("app.rag.pipeline.PlanGenerator")
@patch("app.rag.pipeline.get_reranker")
@patch("app.rag.pipeline.VectorRetriever")
@patch("app.rag.pipeline.QueryBuilder")
def test_pipeline_insufficient_when_no_chunks_after_rerank(
    mock_qb_cls, mock_ret_cls, mock_get_rerank, mock_gen_cls
):
    mock_qb_cls.return_value.build_clinical_summary.return_value = "Resumen clínico"
    mock_qb_cls.return_value.expand_queries.return_value = ["consulta 1"]

    mock_ret_cls.return_value.retrieve.return_value = []

    mock_reranker = MagicMock()
    mock_reranker.rerank.return_value = []
    mock_get_rerank.return_value = mock_reranker

    pipeline = RAGPipeline()
    intake = {
        "profile_version": "generic_holistic_v0",
        "chief_complaint": "Dolor",
        "conditions": ["c"],
        "goals": ["g"],
    }

    plan = pipeline.generate_plan(
        patient_id="00000000-0000-0000-0000-000000000001",
        intake_json=intake,
        available_therapies=["fisioterapia"],
        preferred_language="es",
    )

    assert plan.get("insufficient_evidence") is True
    assert plan["weeks"] == []
    assert plan["citations_used"] == []
    assert plan["requires_practitioner_review"] is True
    assert "No hay" in (plan.get("confidence_note") or "") or "evidencia" in (plan.get("confidence_note") or "").lower()

    mock_gen_cls.return_value.generate.assert_not_called()
