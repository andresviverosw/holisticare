"""HTTP contract tests for POST /rag/plan/generate — no PostgreSQL or LLM (overridden deps)."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_rag_pipeline
from app.core.database import get_db
from app.main import app
from app.models.treatment_plan import TreatmentPlan
from app.rag.pipeline import RAGPipeline

PATIENT_ID = str(uuid.uuid4())


def _valid_body():
    return {
        "patient_id": PATIENT_ID,
        "intake_json": {
            "profile_version": "generic_holistic_v0",
            "chief_complaint": "Dolor lumbar mecánico.",
            "conditions": ["lumbalgia subaguda"],
            "goals": ["Reducir dolor"],
        },
        "available_therapies": ["fisioterapia", "acupuntura"],
        "preferred_language": "es",
    }


def test_plan_generate_422_when_available_therapies_empty(client: TestClient):
    body = _valid_body()
    body["available_therapies"] = []
    r = client.post("/rag/plan/generate", json=body)
    assert r.status_code == 422


def test_plan_generate_422_when_conditions_empty(client: TestClient):
    body = _valid_body()
    body["intake_json"]["conditions"] = []
    r = client.post("/rag/plan/generate", json=body)
    assert r.status_code == 422


def test_plan_generate_422_when_profile_version_invalid(client: TestClient):
    body = _valid_body()
    body["intake_json"]["profile_version"] = "wrong"
    r = client.post("/rag/plan/generate", json=body)
    assert r.status_code == 422


@pytest.fixture
def mock_plan():
    return {
        "plan_id": str(uuid.uuid4()),
        "patient_id": PATIENT_ID,
        "generated_at": "2026-01-01T00:00:00+00:00",
        "requires_practitioner_review": True,
        "status": "pending_review",
        "citations_used": ["REF-A"],
        "weeks": [
            {
                "week": 1,
                "goals": ["g"],
                "therapies": [],
                "contraindications_flagged": [],
                "outcome_checkpoints": [],
            }
        ],
        "confidence_note": "Nota",
        "retrieval_metadata": {
            "queries_used": [],
            "candidates_retrieved": 1,
            "chunks_passed_to_llm": 1,
            "reranker_backend": "crossencoder",
        },
    }


def test_plan_generate_200_delegates_to_pipeline(client: TestClient, mock_plan):
    fake_pipeline = MagicMock(spec=RAGPipeline)
    fake_pipeline.generate_plan.return_value = mock_plan
    app.dependency_overrides[get_rag_pipeline] = lambda: fake_pipeline
    try:
        r = client.post("/rag/plan/generate", json=_valid_body())
    finally:
        app.dependency_overrides.pop(get_rag_pipeline, None)

    assert r.status_code == 200
    data = r.json()
    assert data["patient_id"] == PATIENT_ID
    assert data["requires_practitioner_review"] is True
    assert data["status"] == "pending_review"
    fake_pipeline.generate_plan.assert_called_once()
    call_kw = fake_pipeline.generate_plan.call_args.kwargs
    assert call_kw["patient_id"] == PATIENT_ID
    assert call_kw["available_therapies"] == ["fisioterapia", "acupuntura"]
    assert call_kw["preferred_language"] == "es"
    assert call_kw["intake_json"]["profile_version"] == "generic_holistic_v0"


def test_plan_generate_persists_treatment_plan_row(client: TestClient, mock_plan):
    db_session = AsyncMock()
    captured: list[object] = []

    def _capture_add(obj: object) -> None:
        captured.append(obj)

    db_session.add = MagicMock(side_effect=_capture_add)
    db_session.commit = AsyncMock()
    db_session.refresh = AsyncMock()

    async def override_db():
        yield db_session

    fake_pipeline = MagicMock(spec=RAGPipeline)
    fake_pipeline.generate_plan.return_value = mock_plan
    app.dependency_overrides[get_rag_pipeline] = lambda: fake_pipeline
    app.dependency_overrides[get_db] = override_db
    try:
        practitioner_id = str(uuid.uuid4())
        body = _valid_body()
        body["practitioner_id"] = practitioner_id
        r = client.post("/rag/plan/generate", json=body)
    finally:
        app.dependency_overrides.pop(get_rag_pipeline, None)
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    assert len(captured) == 1
    row = captured[0]
    assert isinstance(row, TreatmentPlan)
    assert str(row.id) == mock_plan["plan_id"]
    assert str(row.patient_id) == PATIENT_ID
    assert str(row.practitioner_id) == practitioner_id
    assert row.status == "pending_review"
    assert row.plan_json == mock_plan
    db_session.commit.assert_awaited_once()
    db_session.refresh.assert_awaited_once()


def test_plan_generate_insufficient_evidence_still_persisted(client: TestClient):
    insufficient_plan = {
        "plan_id": str(uuid.uuid4()),
        "patient_id": PATIENT_ID,
        "generated_at": "2026-01-01T00:00:00+00:00",
        "requires_practitioner_review": True,
        "status": "pending_review",
        "insufficient_evidence": True,
        "citations_used": [],
        "weeks": [],
        "confidence_note": "No hay contexto clínico recuperado para generar un plan.",
        "retrieval_metadata": {
            "queries_used": ["q"],
            "candidates_retrieved": 0,
            "chunks_passed_to_llm": 0,
            "reranker_backend": "crossencoder",
        },
    }
    fake_pipeline = MagicMock(spec=RAGPipeline)
    fake_pipeline.generate_plan.return_value = insufficient_plan

    db_session = AsyncMock()
    captured: list[object] = []
    db_session.add = MagicMock(side_effect=lambda o: captured.append(o))
    db_session.commit = AsyncMock()
    db_session.refresh = AsyncMock()

    async def override_db():
        yield db_session

    app.dependency_overrides[get_rag_pipeline] = lambda: fake_pipeline
    app.dependency_overrides[get_db] = override_db
    try:
        r = client.post("/rag/plan/generate", json=_valid_body())
    finally:
        app.dependency_overrides.pop(get_rag_pipeline, None)
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    assert r.json()["insufficient_evidence"] is True
    assert r.json()["weeks"] == []
    assert len(captured) == 1
    row = captured[0]
    assert isinstance(row, TreatmentPlan)
    assert row.plan_json["insufficient_evidence"] is True
    db_session.commit.assert_awaited_once()
