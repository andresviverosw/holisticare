"""HTTP contract tests for progress analytics (US-ANLY-001)."""

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


def _diary_row(pid: uuid.UUID, d: date, pain: int) -> PatientDiaryEntry:
    return PatientDiaryEntry(
        id=uuid.uuid4(),
        patient_id=pid,
        entry_date=d,
        diary_json={
            "profile_version": "patient_diary_v0",
            "checkin_date": d.isoformat(),
            "pain_nrs_0_10": pain,
            "sleep_quality_0_10": 5,
            "mood_0_10": 6,
            "function_0_10": 4,
        },
    )


def test_outcomes_trend_200_series_ascending_by_date(client: TestClient):
    pid = uuid.UUID(PATIENT_ID)
    early = _diary_row(pid, date(2026, 4, 1), pain=6)
    late = _diary_row(pid, date(2026, 4, 3), pain=3)
    db_session = AsyncMock()
    exec_result = MagicMock()
    exec_result.scalars.return_value.all.return_value = [early, late]
    db_session.execute = AsyncMock(return_value=exec_result)

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.get(
            f"/rag/analytics/patient/{PATIENT_ID}/outcomes-trend",
            params={"date_from": "2026-04-01", "date_to": "2026-04-03"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    payload = r.json()
    assert payload["patient_id"] == PATIENT_ID
    assert payload["source"] == "patient_diary_v0"
    assert [p["date"] for p in payload["series"]] == ["2026-04-01", "2026-04-03"]
    assert payload["series"][0]["pain_nrs_0_10"] == 6
    assert payload["series"][1]["pain_nrs_0_10"] == 3


def test_outcomes_trend_422_when_from_after_to(client: TestClient):
    r = client.get(
        f"/rag/analytics/patient/{PATIENT_ID}/outcomes-trend",
        params={"date_from": "2026-04-10", "date_to": "2026-04-01"},
    )
    assert r.status_code == 422


def test_outcomes_trend_422_when_range_exceeds_max(client: TestClient):
    r = client.get(
        f"/rag/analytics/patient/{PATIENT_ID}/outcomes-trend",
        params={"date_from": "2024-01-01", "date_to": "2026-04-01"},
    )
    assert r.status_code == 422


def test_outcomes_trend_401_when_not_authenticated(client: TestClient):
    app.dependency_overrides.pop(get_current_user, None)
    try:
        r = client.get(
            f"/rag/analytics/patient/{PATIENT_ID}/outcomes-trend",
            params={"date_from": "2026-04-01", "date_to": "2026-04-03"},
        )
    finally:
        app.dependency_overrides[get_current_user] = lambda: AuthUser(sub="test-user", role="clinician")
    assert r.status_code == 401


def test_outcomes_trend_403_for_patient_role(client: TestClient):
    app.dependency_overrides[get_current_user] = lambda: AuthUser(sub=PATIENT_ID, role="patient")
    try:
        r = client.get(
            f"/rag/analytics/patient/{PATIENT_ID}/outcomes-trend",
            params={"date_from": "2026-04-01", "date_to": "2026-04-03"},
        )
    finally:
        app.dependency_overrides[get_current_user] = lambda: AuthUser(sub="test-user", role="clinician")
    assert r.status_code == 403


def test_recovery_trajectory_200_returns_prediction_payload(client: TestClient):
    pid = uuid.UUID(PATIENT_ID)
    rows = [
        _diary_row(pid, date(2026, 4, 1), pain=8),
        _diary_row(pid, date(2026, 4, 3), pain=7),
        _diary_row(pid, date(2026, 4, 5), pain=6),
        _diary_row(pid, date(2026, 4, 7), pain=6),
        _diary_row(pid, date(2026, 4, 10), pain=5),
    ]
    db_session = AsyncMock()
    exec_result = MagicMock()
    exec_result.scalars.return_value.all.return_value = rows
    db_session.execute = AsyncMock(return_value=exec_result)

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.get(
            f"/rag/analytics/patient/{PATIENT_ID}/recovery-trajectory",
            params={"date_from": "2026-04-01", "date_to": "2026-04-10"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    payload = r.json()
    assert payload["patient_id"] == PATIENT_ID
    assert payload["analysis_status"] == "ok"
    assert payload["trajectory"]["label"] in {"improving", "stable", "worsening"}
    assert isinstance(payload["trajectory"]["rationale"], str)
    assert payload["data_points_used"] == 5


def test_recovery_trajectory_200_insufficient_data_when_few_points(client: TestClient):
    pid = uuid.UUID(PATIENT_ID)
    rows = [
        _diary_row(pid, date(2026, 4, 1), pain=6),
        _diary_row(pid, date(2026, 4, 3), pain=6),
        _diary_row(pid, date(2026, 4, 5), pain=5),
    ]
    db_session = AsyncMock()
    exec_result = MagicMock()
    exec_result.scalars.return_value.all.return_value = rows
    db_session.execute = AsyncMock(return_value=exec_result)

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.get(
            f"/rag/analytics/patient/{PATIENT_ID}/recovery-trajectory",
            params={"date_from": "2026-04-01", "date_to": "2026-04-05"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    payload = r.json()
    assert payload["analysis_status"] == "insufficient_data"
    assert payload["trajectory"] is None


def test_recovery_recommendations_200_returns_structured_recommendations(client: TestClient):
    pid = uuid.UUID(PATIENT_ID)
    rows = [
        _diary_row(pid, date(2026, 4, 1), pain=8),
        _diary_row(pid, date(2026, 4, 3), pain=8),
        _diary_row(pid, date(2026, 4, 5), pain=9),
        _diary_row(pid, date(2026, 4, 8), pain=9),
        _diary_row(pid, date(2026, 4, 10), pain=9),
    ]
    db_session = AsyncMock()
    exec_result = MagicMock()
    exec_result.scalars.return_value.all.return_value = rows
    db_session.execute = AsyncMock(return_value=exec_result)

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.get(
            f"/rag/analytics/patient/{PATIENT_ID}/recovery-recommendations",
            params={"date_from": "2026-04-01", "date_to": "2026-04-10"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    payload = r.json()
    assert payload["patient_id"] == PATIENT_ID
    assert payload["prediction"]["analysis_status"] == "ok"
    assert payload["recommendation_status"] == "ok"
    assert len(payload["recommendations"]) >= 1
