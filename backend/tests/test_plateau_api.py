"""HTTP contract tests for plateau analytics (US-ANLY-002)."""

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


def test_plateau_403_for_patient_role(client: TestClient):
    app.dependency_overrides[get_current_user] = lambda: AuthUser(sub=PATIENT_ID, role="patient")
    try:
        r = client.get(
            f"/rag/analytics/patient/{PATIENT_ID}/plateau-flags",
            params={"date_from": "2026-04-01", "date_to": "2026-04-14"},
        )
    finally:
        app.dependency_overrides[get_current_user] = lambda: AuthUser(sub="test-user", role="clinician")
    assert r.status_code == 403


def test_plateau_200_insufficient_data_when_few_rows(client: TestClient):
    pid = uuid.UUID(PATIENT_ID)
    rows = [
        PatientDiaryEntry(
            id=uuid.uuid4(),
            patient_id=pid,
            entry_date=date(2026, 4, 1),
            diary_json={"pain_nrs_0_10": 3},
        )
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
            f"/rag/analytics/patient/{PATIENT_ID}/plateau-flags",
            params={"date_from": "2026-04-01", "date_to": "2026-04-14"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    body = r.json()
    assert body["analysis_status"] == "insufficient_data"
    assert body["flags"] == []


def test_plateau_200_returns_flag_when_worsening(client: TestClient):
    pid = uuid.UUID(PATIENT_ID)
    rows = []
    pains = [3, 3, 3, 3, 8, 8, 8, 8]
    for i, p in enumerate(pains):
        rows.append(
            PatientDiaryEntry(
                id=uuid.uuid4(),
                patient_id=pid,
                entry_date=date(2026, 4, i + 1),
                diary_json={
                    "profile_version": "patient_diary_v0",
                    "pain_nrs_0_10": p,
                    "function_0_10": 6,
                },
            )
        )
    db_session = AsyncMock()
    exec_result = MagicMock()
    exec_result.scalars.return_value.all.return_value = rows
    db_session.execute = AsyncMock(return_value=exec_result)

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        r = client.get(
            f"/rag/analytics/patient/{PATIENT_ID}/plateau-flags",
            params={"date_from": "2026-04-01", "date_to": "2026-04-10"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    body = r.json()
    assert body["analysis_status"] == "ok"
    assert any(f.get("code") == "PAIN_WORSENING" for f in body["flags"])
