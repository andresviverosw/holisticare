"""API tests for clinician password login (US-AUTH-CLINICIAN-PROD)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.database import get_db
from app.main import app, create_app
from app.models.app_user import AppUser
from app.services.user_service import hash_password


@pytest.fixture(autouse=True)
def _clear_overrides():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
    app.dependency_overrides.clear()


def _mock_db_with_user(user: AppUser | None):
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    exec_result = MagicMock()
    exec_result.scalar_one_or_none.return_value = user
    session.execute = AsyncMock(return_value=exec_result)
    return session


def test_password_login_200_returns_jwt_with_exp():
    user = AppUser(
        id=uuid.uuid4(),
        username="clinician1",
        password_hash=hash_password("s3cret"),
        role="clinician",
        is_active=True,
    )
    db = _mock_db_with_user(user)

    async def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as client:
        r = client.post("/auth/login", json={"username": "clinician1", "password": "s3cret"})
        assert r.status_code == 200
        body = r.json()
        assert body["role"] == "clinician"
        assert body["sub"] == str(user.id)
        payload = jwt.decode(body["access_token"], get_settings().secret_key, algorithms=["HS256"])
        assert payload["role"] == "clinician"
        assert payload["sub"] == str(user.id)
        assert "exp" in payload


def test_password_login_401_wrong_password():
    user = AppUser(
        id=uuid.uuid4(),
        username="clinician1",
        password_hash=hash_password("s3cret"),
        role="clinician",
        is_active=True,
    )
    db = _mock_db_with_user(user)

    async def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as client:
        r = client.post("/auth/login", json={"username": "clinician1", "password": "nope"})
        assert r.status_code == 401
        assert "Invalid" in r.json()["detail"]


def test_password_login_401_inactive_user():
    user = AppUser(
        id=uuid.uuid4(),
        username="clinician1",
        password_hash=hash_password("s3cret"),
        role="clinician",
        is_active=False,
    )
    db = _mock_db_with_user(user)

    async def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as client:
        r = client.post("/auth/login", json={"username": "clinician1", "password": "s3cret"})
        assert r.status_code == 401


def test_password_login_available_when_dev_auth_disabled(monkeypatch):
    monkeypatch.setenv("ALLOW_DEV_AUTH", "false")
    get_settings.cache_clear()
    local_app = create_app()

    user = AppUser(
        id=uuid.uuid4(),
        username="admin1",
        password_hash=hash_password("admin-pass"),
        role="admin",
        is_active=True,
    )
    db = _mock_db_with_user(user)

    async def override_db():
        yield db

    local_app.dependency_overrides[get_db] = override_db
    with TestClient(local_app) as client:
        assert client.post("/auth/dev-login", json={"role": "clinician"}).status_code == 404
        r = client.post("/auth/login", json={"username": "admin1", "password": "admin-pass"})
        assert r.status_code == 200
        assert r.json()["role"] == "admin"
