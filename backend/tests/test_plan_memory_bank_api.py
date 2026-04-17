"""HTTP contract tests for plan memory bank (US-PLAN-004) — mocked DB."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models.plan_memory_bank import PlanMemoryBankEntry
from app.models.treatment_plan import TreatmentPlan


def _auth() -> dict[str, str]:
    from jose import jwt

    from app.core.config import get_settings

    token = jwt.encode({"sub": "clin-1", "role": "clinician"}, get_settings().secret_key, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client() -> TestClient:
    from app.api.deps import get_current_user, AuthUser

    app.dependency_overrides[get_db] = _mock_get_db_factory(AsyncMock())
    app.dependency_overrides[get_current_user] = lambda: AuthUser(sub="clin-1", role="clinician")
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _mock_get_db_factory(db_session: AsyncMock):
    async def _gen():
        yield db_session

    return _gen


def test_memory_bank_add_404_when_plan_missing(client: TestClient):
    db_session = AsyncMock()
    db_session.execute = AsyncMock()
    exec_res = MagicMock()
    exec_res.scalar_one_or_none.return_value = None
    db_session.execute.return_value = exec_res
    db_session.commit = AsyncMock()
    db_session.refresh = AsyncMock()

    app.dependency_overrides[get_db] = _mock_get_db_factory(db_session)
    try:
        r = client.post(
            "/rag/plan/memory-bank",
            json={
                "source_plan_id": str(uuid.uuid4()),
                "title": "Plantilla lumbar",
                "tags": ["lumbalgia"],
            },
            headers=_auth(),
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 404


def test_memory_bank_add_400_when_plan_not_approved(client: TestClient):
    db_session = AsyncMock()
    db_session.execute = AsyncMock()
    plan = TreatmentPlan(
        id=uuid.uuid4(),
        patient_id=uuid.uuid4(),
        practitioner_id=None,
        status="pending_review",
        plan_json={"plan_id": str(uuid.uuid4()), "weeks": []},
        citations_used=[],
    )
    exec_res = MagicMock()
    exec_res.scalar_one_or_none.return_value = plan
    db_session.execute.return_value = exec_res

    app.dependency_overrides[get_db] = _mock_get_db_factory(db_session)
    try:
        r = client.post(
            "/rag/plan/memory-bank",
            json={
                "source_plan_id": str(plan.id),
                "title": "X",
                "tags": [],
            },
            headers=_auth(),
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 400
    assert "aprobados" in r.json()["detail"].lower()


def test_memory_bank_add_200_creates_entry(client: TestClient):
    db_session = AsyncMock()
    db_session.execute = AsyncMock()
    plan_id = uuid.uuid4()
    plan = TreatmentPlan(
        id=plan_id,
        patient_id=uuid.uuid4(),
        practitioner_id=None,
        status="approved",
        plan_json={
            "plan_id": str(plan_id),
            "patient_id": str(uuid.uuid4()),
            "weeks": [{"week": 1, "therapies": [{"type": "fisioterapia", "rationale": "r"}]}],
        },
        citations_used=["REF-A"],
    )
    exec_res = MagicMock()
    exec_res.scalar_one_or_none.return_value = plan
    db_session.execute.return_value = exec_res
    captured: list[object] = []
    db_session.add = MagicMock(side_effect=lambda o: captured.append(o))
    db_session.commit = AsyncMock()
    db_session.refresh = AsyncMock()

    app.dependency_overrides[get_db] = _mock_get_db_factory(db_session)
    try:
        r = client.post(
            "/rag/plan/memory-bank",
            json={
                "source_plan_id": str(plan_id),
                "title": "Lumbalgia estándar",
                "tags": ["demo"],
            },
            headers=_auth(),
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Lumbalgia estándar"
    assert len(captured) == 1
    assert isinstance(captured[0], PlanMemoryBankEntry)
    assert captured[0].snapshot_json.get("memory_bank_snapshot") is True


def test_memory_bank_list_200(client: TestClient):
    db_session = AsyncMock()
    entry = PlanMemoryBankEntry(
        id=uuid.uuid4(),
        source_plan_id=uuid.uuid4(),
        title="T1",
        tags=["a"],
        therapy_types=["fisioterapia"],
        language="es",
        snapshot_json={"weeks": []},
        created_by_sub="clin-1",
    )
    exec_res = MagicMock()
    scal = MagicMock()
    scal.all.return_value = [entry]
    exec_res.scalars.return_value = scal
    db_session.execute.return_value = exec_res

    app.dependency_overrides[get_db] = _mock_get_db_factory(db_session)
    try:
        r = client.get("/rag/plan/memory-bank", headers=_auth())
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "T1"


def test_memory_bank_instantiate_404_when_template_missing(client: TestClient):
    db_session = AsyncMock()
    db_session.execute = AsyncMock()
    exec_res = MagicMock()
    exec_res.scalar_one_or_none.return_value = None
    db_session.execute.return_value = exec_res

    app.dependency_overrides[get_db] = _mock_get_db_factory(db_session)
    try:
        r = client.post(
            f"/rag/plan/memory-bank/{uuid.uuid4()}/instantiate",
            json={"patient_id": str(uuid.uuid4())},
            headers=_auth(),
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 404
