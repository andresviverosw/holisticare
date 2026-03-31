"""HTTP contract tests for session logging (US-SESS-001) — DB stubbed via dependency overrides."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.api.deps import AuthUser, get_current_user
from app.core.database import get_db
from app.main import app
from app.models.care_session import CareSession

PATIENT_ID = str(uuid.uuid4())
PRACTITIONER_ID = str(uuid.uuid4())


def _valid_session_body():
    return {
        "patient_id": PATIENT_ID,
        "practitioner_id": PRACTITIONER_ID,
        "session_log": {
            "profile_version": "clinical_session_v0",
            "session_at": "2026-04-01T14:30:00+00:00",
            "interventions": [
                {
                    "therapy_type": "fisioterapia",
                    "description": "Ejercicios de estabilización lumbar.",
                    "duration_minutes": 30,
                }
            ],
            "observations": "Buena tolerancia al ejercicio.",
        },
    }


def test_create_session_422_when_interventions_empty(client: TestClient):
    body = _valid_session_body()
    body["session_log"]["interventions"] = []
    r = client.post("/rag/sessions", json=body)
    assert r.status_code == 422


def test_create_session_422_when_observations_missing(client: TestClient):
    body = _valid_session_body()
    del body["session_log"]["observations"]
    r = client.post("/rag/sessions", json=body)
    assert r.status_code == 422


def test_create_session_200_persists_row(client: TestClient):
    db_session = AsyncMock()
    db_session.add = MagicMock()
    db_session.commit = AsyncMock()
    db_session.refresh = AsyncMock()

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.post("/rag/sessions", json=_valid_session_body())
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    data = r.json()
    assert data["patient_id"] == PATIENT_ID
    assert "session_id" in data
    assert data["session_log"]["observations"] == "Buena tolerancia al ejercicio."
    db_session.add.assert_called_once()
    added = db_session.add.call_args[0][0]
    assert isinstance(added, CareSession)
    assert str(added.patient_id) == PATIENT_ID
    assert added.session_json["profile_version"] == "clinical_session_v0"
    db_session.commit.assert_awaited_once()
    db_session.refresh.assert_awaited_once()


def test_list_sessions_200_newest_first(client: TestClient):
    pid = uuid.UUID(PATIENT_ID)
    older = CareSession(
        id=uuid.uuid4(),
        patient_id=pid,
        practitioner_id=None,
        occurred_at=datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),
        session_json={"profile_version": "clinical_session_v0", "session_at": "2026-03-01T10:00:00+00:00"},
    )
    newer = CareSession(
        id=uuid.uuid4(),
        patient_id=pid,
        practitioner_id=uuid.UUID(PRACTITIONER_ID),
        occurred_at=datetime(2026, 4, 1, 14, 30, tzinfo=timezone.utc),
        session_json={"profile_version": "clinical_session_v0", "session_at": "2026-04-01T14:30:00+00:00"},
    )
    db_session = AsyncMock()
    execute_result = MagicMock()
    execute_result.scalars.return_value.all.return_value = [newer, older]
    db_session.execute = AsyncMock(return_value=execute_result)

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.get(f"/rag/sessions/patient/{PATIENT_ID}")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    payload = r.json()
    assert payload["patient_id"] == PATIENT_ID
    assert len(payload["items"]) == 2
    assert payload["items"][0]["session_id"] == str(newer.id)
    assert payload["items"][1]["session_id"] == str(older.id)


def test_list_sessions_200_empty(client: TestClient):
    db_session = AsyncMock()
    execute_result = MagicMock()
    execute_result.scalars.return_value.all.return_value = []
    db_session.execute = AsyncMock(return_value=execute_result)

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.get(f"/rag/sessions/patient/{PATIENT_ID}")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    assert r.json() == {
        "patient_id": PATIENT_ID,
        "items": [],
        "limit": 50,
        "offset": 0,
    }


def test_create_session_401_when_not_authenticated(client: TestClient):
    app.dependency_overrides.pop(get_current_user, None)
    try:
        r = client.post("/rag/sessions", json=_valid_session_body())
    finally:
        app.dependency_overrides[get_current_user] = lambda: AuthUser(sub="test-user", role="clinician")
    assert r.status_code == 401


def test_list_sessions_401_when_not_authenticated(client: TestClient):
    app.dependency_overrides.pop(get_current_user, None)
    try:
        r = client.get(f"/rag/sessions/patient/{PATIENT_ID}")
    finally:
        app.dependency_overrides[get_current_user] = lambda: AuthUser(sub="test-user", role="clinician")
    assert r.status_code == 401
