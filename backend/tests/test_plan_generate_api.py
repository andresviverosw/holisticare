"""HTTP contract tests for POST /rag/plan/generate — no PostgreSQL or LLM (overridden deps)."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_rag_pipeline
from app.core.database import get_db
from app.main import app
from app.models.intake_profile import IntakeProfile
from app.models.treatment_plan import TreatmentPlan
from app.rag.pipeline import RAGPipeline
from app.api.deps import get_ingestion_service

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


def _valid_intake_payload():
    return {
        "patient_id": PATIENT_ID,
        "intake_json": {
            "profile_version": "generic_holistic_v0",
            "chief_complaint": "Dolor lumbar mecánico.",
            "conditions": ["lumbalgia subaguda"],
            "goals": ["Reducir dolor"],
        },
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


def test_get_plan_200_returns_persisted_json(client: TestClient):
    plan_id = uuid.uuid4()
    persisted = TreatmentPlan(
        id=plan_id,
        patient_id=uuid.uuid4(),
        practitioner_id=None,
        status="pending_review",
        plan_json={
            "plan_id": str(plan_id),
            "status": "pending_review",
            "weeks": [],
            "citations_used": [],
        },
        citations_used=[],
    )
    db_session = AsyncMock()
    db_session.execute = AsyncMock()
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = persisted
    db_session.execute.return_value = execute_result

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.get(f"/rag/plan/{plan_id}")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    assert r.json()["plan_id"] == str(plan_id)
    assert r.json()["status"] == "pending_review"
    db_session.execute.assert_awaited_once()


def test_get_plan_404_when_not_found(client: TestClient):
    plan_id = uuid.uuid4()
    db_session = AsyncMock()
    db_session.execute = AsyncMock()
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None
    db_session.execute.return_value = execute_result

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.get(f"/rag/plan/{plan_id}")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 404


def test_get_plan_sources_200_returns_chunk_metadata(client: TestClient):
    plan_id = uuid.uuid4()
    persisted = TreatmentPlan(
        id=plan_id,
        patient_id=uuid.uuid4(),
        practitioner_id=None,
        status="pending_review",
        plan_json={"plan_id": str(plan_id), "citations_used": ["REF-A", "REF-B"]},
        citations_used=["REF-A", "REF-B"],
    )

    plan_result = MagicMock()
    plan_result.scalar_one_or_none.return_value = persisted

    chunks_result = MagicMock()
    chunks_result.mappings.return_value.all.return_value = [
        {
            "ref_id": "REF-B",
            "content": "Chunk B",
            "source_file": "guide-b.pdf",
            "page_number": 5,
            "section": "dosificacion",
            "language": "es",
            "evidence_level": "A",
            "has_contraindication": True,
        },
        {
            "ref_id": "REF-A",
            "content": "Chunk A",
            "source_file": "guide-a.pdf",
            "page_number": 2,
            "section": "contraindicaciones",
            "language": "es",
            "evidence_level": "B",
            "has_contraindication": False,
        },
    ]

    db_session = AsyncMock()
    db_session.execute = AsyncMock(side_effect=[plan_result, chunks_result])

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.get(f"/rag/plan/{plan_id}/sources")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    payload = r.json()
    assert payload["plan_id"] == str(plan_id)
    assert payload["citations_used"] == ["REF-A", "REF-B"]
    assert len(payload["sources"]) == 2
    # Response order must follow citations_used order.
    assert payload["sources"][0]["ref_id"] == "REF-A"
    assert payload["sources"][1]["ref_id"] == "REF-B"
    assert payload["sources"][1]["has_contraindication"] is True


def test_get_plan_sources_404_when_plan_missing(client: TestClient):
    plan_id = uuid.uuid4()
    plan_result = MagicMock()
    plan_result.scalar_one_or_none.return_value = None

    db_session = AsyncMock()
    db_session.execute = AsyncMock(return_value=plan_result)

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.get(f"/rag/plan/{plan_id}/sources")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 404


def test_get_plan_sources_200_empty_when_no_citations(client: TestClient):
    plan_id = uuid.uuid4()
    persisted = TreatmentPlan(
        id=plan_id,
        patient_id=uuid.uuid4(),
        practitioner_id=None,
        status="pending_review",
        plan_json={"plan_id": str(plan_id), "citations_used": []},
        citations_used=[],
    )
    plan_result = MagicMock()
    plan_result.scalar_one_or_none.return_value = persisted

    db_session = AsyncMock()
    db_session.execute = AsyncMock(return_value=plan_result)

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.get(f"/rag/plan/{plan_id}/sources")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    assert r.json()["sources"] == []


def test_approve_plan_200_updates_status_and_notes(client: TestClient):
    plan_id = uuid.uuid4()
    persisted = TreatmentPlan(
        id=plan_id,
        patient_id=uuid.uuid4(),
        practitioner_id=uuid.uuid4(),
        status="pending_review",
        plan_json={"plan_id": str(plan_id), "status": "pending_review"},
        citations_used=[],
    )
    db_session = AsyncMock()
    db_session.execute = AsyncMock()
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = persisted
    db_session.execute.return_value = execute_result
    db_session.commit = AsyncMock()
    db_session.refresh = AsyncMock()

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.patch(
            f"/rag/plan/{plan_id}/approve",
            json={
                "action": "approve",
                "practitioner_notes": "Aprobado con ajustes de intensidad.",
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    payload = r.json()
    assert payload["plan_id"] == str(plan_id)
    assert payload["status"] == "approved"
    assert payload["practitioner_notes"] == "Aprobado con ajustes de intensidad."
    assert payload["plan_json"]["status"] == "approved"
    assert payload["plan_json"]["practitioner_notes"] == "Aprobado con ajustes de intensidad."
    db_session.commit.assert_awaited_once()
    db_session.refresh.assert_awaited_once()


def test_approve_plan_200_reject_updates_status(client: TestClient):
    plan_id = uuid.uuid4()
    persisted = TreatmentPlan(
        id=plan_id,
        patient_id=uuid.uuid4(),
        practitioner_id=uuid.uuid4(),
        status="pending_review",
        plan_json={"plan_id": str(plan_id), "status": "pending_review"},
        citations_used=[],
    )
    db_session = AsyncMock()
    db_session.execute = AsyncMock()
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = persisted
    db_session.execute.return_value = execute_result
    db_session.commit = AsyncMock()
    db_session.refresh = AsyncMock()

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.patch(
            f"/rag/plan/{plan_id}/approve",
            json={"action": "reject", "practitioner_notes": "No alineado con evolución clínica."},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    payload = r.json()
    assert payload["status"] == "rejected"
    assert payload["plan_json"]["status"] == "rejected"


def test_approve_plan_404_when_not_found(client: TestClient):
    plan_id = uuid.uuid4()
    db_session = AsyncMock()
    db_session.execute = AsyncMock()
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None
    db_session.execute.return_value = execute_result

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.patch(f"/rag/plan/{plan_id}/approve", json={"action": "approve"})
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 404


def test_approve_plan_422_when_action_invalid(client: TestClient):
    plan_id = uuid.uuid4()
    r = client.patch(f"/rag/plan/{plan_id}/approve", json={"action": "other"})
    assert r.status_code == 422


def test_list_chunks_200_with_filters_and_pagination(client: TestClient):
    db_session = AsyncMock()
    db_session.execute = AsyncMock()
    execute_result = MagicMock()
    execute_result.mappings.return_value.all.return_value = [
        {
            "ref_id": "REF-10",
            "content": "Movilidad lumbar con progresion suave.",
            "therapy_type": ["fisioterapia"],
            "condition": ["lumbalgia"],
            "evidence_level": "B",
            "language": "es",
            "section": "protocolo",
            "has_contraindication": False,
            "source_file": "guia.pdf",
            "page_number": 4,
        }
    ]
    db_session.execute.return_value = execute_result

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.get(
            "/rag/chunks",
            params={
                "therapy_type": "fisioterapia",
                "language": "es",
                "has_contraindication": "false",
                "limit": 10,
                "offset": 5,
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    payload = r.json()
    assert payload["limit"] == 10
    assert payload["offset"] == 5
    assert len(payload["items"]) == 1
    assert payload["items"][0]["ref_id"] == "REF-10"
    db_session.execute.assert_awaited_once()


def test_list_chunks_200_without_filters(client: TestClient):
    db_session = AsyncMock()
    db_session.execute = AsyncMock()
    execute_result = MagicMock()
    execute_result.mappings.return_value.all.return_value = []
    db_session.execute.return_value = execute_result

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.get("/rag/chunks")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    assert r.json()["items"] == []


def test_list_chunks_422_when_limit_out_of_range(client: TestClient):
    r = client.get("/rag/chunks", params={"limit": 0})
    assert r.status_code == 422


def test_ingest_200_returns_summary(client: TestClient):
    fake_ingestion = MagicMock()
    fake_ingestion.ingest.return_value = {
        "files_processed": 2,
        "chunks_created": 15,
        "status": "success",
    }
    app.dependency_overrides[get_ingestion_service] = lambda: fake_ingestion
    try:
        r = client.post("/rag/ingest", json={"source_dir": "data/mock", "force_reindex": False})
    finally:
        app.dependency_overrides.pop(get_ingestion_service, None)

    assert r.status_code == 200
    assert r.json()["files_processed"] == 2
    assert r.json()["chunks_created"] == 15
    assert r.json()["status"] == "success"
    fake_ingestion.ingest.assert_called_once_with(source_dir="data/mock", force_reindex=False)


def test_ingest_400_when_source_dir_missing(client: TestClient):
    fake_ingestion = MagicMock()
    fake_ingestion.ingest.side_effect = FileNotFoundError("Source directory not found: nope")
    app.dependency_overrides[get_ingestion_service] = lambda: fake_ingestion
    try:
        r = client.post("/rag/ingest", json={"source_dir": "nope"})
    finally:
        app.dependency_overrides.pop(get_ingestion_service, None)

    assert r.status_code == 400
    assert "Source directory not found" in r.json()["detail"]


def test_ingest_200_forwards_force_reindex(client: TestClient):
    fake_ingestion = MagicMock()
    fake_ingestion.ingest.return_value = {
        "files_processed": 1,
        "chunks_created": 4,
        "status": "success",
    }
    app.dependency_overrides[get_ingestion_service] = lambda: fake_ingestion
    try:
        r = client.post("/rag/ingest", json={"source_dir": "data/mock", "force_reindex": True})
    finally:
        app.dependency_overrides.pop(get_ingestion_service, None)

    assert r.status_code == 200
    fake_ingestion.ingest.assert_called_once_with(source_dir="data/mock", force_reindex=True)


def test_save_intake_200_persists_payload(client: TestClient):
    db_session = AsyncMock()
    db_session.execute = AsyncMock()
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None
    db_session.execute.return_value = execute_result
    captured: list[object] = []
    db_session.add = MagicMock(side_effect=lambda o: captured.append(o))
    db_session.commit = AsyncMock()
    db_session.refresh = AsyncMock()

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.post("/rag/intake", json=_valid_intake_payload())
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    assert r.json()["patient_id"] == PATIENT_ID
    assert r.json()["intake_json"]["profile_version"] == "generic_holistic_v0"
    assert len(captured) == 1
    assert isinstance(captured[0], IntakeProfile)
    db_session.commit.assert_awaited_once()


def test_get_intake_200_returns_saved_payload(client: TestClient):
    intake = IntakeProfile(
        id=uuid.uuid4(),
        patient_id=uuid.UUID(PATIENT_ID),
        practitioner_id=None,
        intake_json={
            "profile_version": "generic_holistic_v0",
            "chief_complaint": "Dolor lumbar mecánico.",
            "conditions": ["lumbalgia subaguda"],
            "goals": ["Reducir dolor"],
        },
    )
    db_session = AsyncMock()
    db_session.execute = AsyncMock()
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = intake
    db_session.execute.return_value = execute_result

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.get(f"/rag/intake/{PATIENT_ID}")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    assert r.json()["patient_id"] == PATIENT_ID
    assert r.json()["intake_json"]["goals"] == ["Reducir dolor"]


def test_get_intake_404_when_missing(client: TestClient):
    db_session = AsyncMock()
    db_session.execute = AsyncMock()
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None
    db_session.execute.return_value = execute_result

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.get(f"/rag/intake/{PATIENT_ID}")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 404
