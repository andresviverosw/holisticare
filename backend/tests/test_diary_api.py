"""HTTP contract tests for patient diary (US-DIARY-001)."""

from __future__ import annotations

import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.api.deps import AuthUser, get_current_user
from app.core.database import get_db
from app.main import app
from app.models.patient_diary_entry import PatientDiaryEntry

PATIENT_ID = str(uuid.uuid4())
OTHER_PATIENT_ID = str(uuid.uuid4())


def _valid_body():
    return {
        "patient_id": PATIENT_ID,
        "checkin": {
            "profile_version": "patient_diary_v0",
            "checkin_date": "2026-04-02",
            "pain_nrs_0_10": 4,
            "sleep_quality_0_10": 6,
            "mood_0_10": 7,
            "function_0_10": 5,
            "notes_es": "Me sentí mejor hoy después de la caminata.",
        },
    }


def test_diary_post_422_pain_out_of_range(client: TestClient):
    body = _valid_body()
    body["checkin"]["pain_nrs_0_10"] = 11
    r = client.post("/rag/diary", json=body)
    assert r.status_code == 422


def test_diary_post_200_persists(client: TestClient):
    db_session = AsyncMock()
    db_session.add = MagicMock()
    db_session.commit = AsyncMock()
    db_session.refresh = AsyncMock()
    exec_select = MagicMock()
    exec_select.scalar_one_or_none.return_value = None
    db_session.execute = AsyncMock(return_value=exec_select)

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.post("/rag/diary", json=_valid_body())
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    data = r.json()
    assert data["patient_id"] == PATIENT_ID
    assert data["entry_date"] == "2026-04-02"
    assert data["checkin"]["pain_nrs_0_10"] == 4
    assert data["checkin"]["notes_es"] == "Me sentí mejor hoy después de la caminata."
    db_session.add.assert_called_once()
    added = db_session.add.call_args[0][0]
    assert isinstance(added, PatientDiaryEntry)


def test_diary_post_200_patient_when_sub_matches(client: TestClient):
    db_session = AsyncMock()
    db_session.add = MagicMock()
    db_session.commit = AsyncMock()
    db_session.refresh = AsyncMock()
    exec_select = MagicMock()
    exec_select.scalar_one_or_none.return_value = None
    db_session.execute = AsyncMock(return_value=exec_select)

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: AuthUser(sub=PATIENT_ID, role="patient")
    try:
        r = client.post("/rag/diary", json=_valid_body())
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides[get_current_user] = lambda: AuthUser(sub="test-user", role="clinician")

    assert r.status_code == 200


def test_diary_post_403_patient_wrong_patient(client: TestClient):
    app.dependency_overrides[get_current_user] = lambda: AuthUser(sub=OTHER_PATIENT_ID, role="patient")
    try:
        r = client.post("/rag/diary", json=_valid_body())
    finally:
        app.dependency_overrides[get_current_user] = lambda: AuthUser(sub="test-user", role="clinician")

    assert r.status_code == 403


def test_diary_post_401_when_not_authenticated(client: TestClient):
    app.dependency_overrides.pop(get_current_user, None)
    try:
        r = client.post("/rag/diary", json=_valid_body())
    finally:
        app.dependency_overrides[get_current_user] = lambda: AuthUser(sub="test-user", role="clinician")
    assert r.status_code == 401


def test_diary_list_200_newest_first(client: TestClient):
    pid = uuid.UUID(PATIENT_ID)
    newer = PatientDiaryEntry(
        id=uuid.uuid4(),
        patient_id=pid,
        entry_date=date(2026, 4, 3),
        diary_json={"profile_version": "patient_diary_v0", "checkin_date": "2026-04-03"},
    )
    older = PatientDiaryEntry(
        id=uuid.uuid4(),
        patient_id=pid,
        entry_date=date(2026, 4, 1),
        diary_json={"profile_version": "patient_diary_v0", "checkin_date": "2026-04-01"},
    )
    db_session = AsyncMock()
    exec_result = MagicMock()
    exec_result.scalars.return_value.all.return_value = [newer, older]
    db_session.execute = AsyncMock(return_value=exec_result)

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.get(f"/rag/diary/patient/{PATIENT_ID}")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    payload = r.json()
    assert payload["patient_id"] == PATIENT_ID
    assert [i["entry_id"] for i in payload["items"]] == [str(newer.id), str(older.id)]


def test_diary_list_403_patient_other_patient(client: TestClient):
    app.dependency_overrides[get_current_user] = lambda: AuthUser(sub=PATIENT_ID, role="patient")
    try:
        r = client.get(f"/rag/diary/patient/{OTHER_PATIENT_ID}")
    finally:
        app.dependency_overrides[get_current_user] = lambda: AuthUser(sub="test-user", role="clinician")
    assert r.status_code == 403

