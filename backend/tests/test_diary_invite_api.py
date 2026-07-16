"""API tests for patient diary invites (US-DIARY-AUTH-PROD)."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import jwt
import pytest
from fastapi.testclient import TestClient

from app.api.deps import AuthUser, get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.main import app, create_app
from app.models.patient_diary_invite import PatientDiaryInvite
from app.services.diary_invite_service import hash_invite_token

PATIENT_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
NOW = datetime(2026, 7, 16, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _clear_settings():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
    app.dependency_overrides.clear()


def _mock_db():
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


async def _yield_db(session):
    yield session


def test_create_invite_201_returns_token_once(client: TestClient):
    db = _mock_db()

    async def refresh_side_effect(row):
        if getattr(row, "expires_at", None) is None:
            row.expires_at = NOW + timedelta(hours=168)

    db.refresh = AsyncMock(side_effect=refresh_side_effect)

    async def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db

    r = client.post("/rag/diary/invites", json={"patient_id": str(PATIENT_ID)})
    assert r.status_code == 200
    body = r.json()
    assert body["patient_id"] == str(PATIENT_ID)
    assert body["token"]
    assert body["redeem_path"].startswith("/login?invite=")
    assert body["token"] in body["redeem_path"]
    db.add.assert_called_once()
    stored = db.add.call_args[0][0]
    assert stored.token_hash == hash_invite_token(body["token"])
    assert body["token"] not in stored.token_hash


def test_create_invite_403_for_patient_role(client: TestClient):
    app.dependency_overrides[get_current_user] = lambda: AuthUser(
        sub=str(PATIENT_ID), role="patient"
    )
    r = client.post("/rag/diary/invites", json={"patient_id": str(PATIENT_ID)})
    assert r.status_code == 403


def test_redeem_invite_200_returns_patient_jwt_with_exp():
    token = "plaintext-invite-token"
    invite = PatientDiaryInvite(
        id=uuid.uuid4(),
        patient_id=PATIENT_ID,
        token_hash=hash_invite_token(token),
        expires_at=NOW + timedelta(days=1),
        redeemed_at=None,
        created_by_sub="clin-1",
    )
    db = _mock_db()
    exec_result = MagicMock()
    exec_result.scalar_one_or_none.return_value = invite
    db.execute = AsyncMock(return_value=exec_result)

    async def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides.pop(get_current_user, None)

    with TestClient(app) as client:
        resp = client.post("/auth/redeem-invite", json={"token": token})
        assert resp.status_code == 200
        body = resp.json()
        assert body["role"] == "patient"
        assert body["sub"] == str(PATIENT_ID)
        payload = jwt.decode(body["access_token"], get_settings().secret_key, algorithms=["HS256"])
        assert payload["role"] == "patient"
        assert payload["sub"] == str(PATIENT_ID)
        assert "exp" in payload
        assert invite.redeemed_at is not None


def test_redeem_invite_410_when_already_used():
    token = "used-token"
    invite = PatientDiaryInvite(
        id=uuid.uuid4(),
        patient_id=PATIENT_ID,
        token_hash=hash_invite_token(token),
        expires_at=NOW + timedelta(days=1),
        redeemed_at=NOW,
        created_by_sub="clin-1",
    )
    db = _mock_db()
    exec_result = MagicMock()
    exec_result.scalar_one_or_none.return_value = invite
    db.execute = AsyncMock(return_value=exec_result)

    async def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides.pop(get_current_user, None)

    with TestClient(app) as client:
        resp = client.post("/auth/redeem-invite", json={"token": token})
        assert resp.status_code == 410


def test_redeem_invite_410_when_expired():
    token = "expired-token"
    invite = PatientDiaryInvite(
        id=uuid.uuid4(),
        patient_id=PATIENT_ID,
        token_hash=hash_invite_token(token),
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        redeemed_at=None,
        created_by_sub="clin-1",
    )
    db = _mock_db()
    exec_result = MagicMock()
    exec_result.scalar_one_or_none.return_value = invite
    db.execute = AsyncMock(return_value=exec_result)

    async def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides.pop(get_current_user, None)

    with TestClient(app) as client:
        resp = client.post("/auth/redeem-invite", json={"token": token})
        assert resp.status_code == 410


def test_redeem_invite_available_when_dev_auth_disabled(monkeypatch):
    monkeypatch.setenv("ALLOW_DEV_AUTH", "false")
    get_settings.cache_clear()
    local_app = create_app()

    token = "dev-off-token"
    invite = PatientDiaryInvite(
        id=uuid.uuid4(),
        patient_id=PATIENT_ID,
        token_hash=hash_invite_token(token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        redeemed_at=None,
        created_by_sub="clin-1",
    )
    db = _mock_db()
    exec_result = MagicMock()
    exec_result.scalar_one_or_none.return_value = invite
    db.execute = AsyncMock(return_value=exec_result)

    async def override_db():
        yield db

    local_app.dependency_overrides[get_db] = override_db
    with TestClient(local_app) as client:
        assert client.post("/auth/dev-login", json={"role": "clinician"}).status_code == 404
        resp = client.post("/auth/redeem-invite", json={"token": token})
        assert resp.status_code == 200
        assert resp.json()["role"] == "patient"


def test_expired_patient_jwt_rejected_on_protected_route(client: TestClient):
    app.dependency_overrides.pop(get_current_user, None)
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    token = jwt.encode(
        {"sub": str(PATIENT_ID), "role": "patient", "exp": past},
        get_settings().secret_key,
        algorithm="HS256",
    )
    r = client.get(
        f"/rag/diary/patient/{PATIENT_ID}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 401
