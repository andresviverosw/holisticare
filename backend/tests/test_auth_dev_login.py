"""Dev-only JWT issuance for local / SPA testing (disabled by default)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.core.config import get_settings
from app.main import app


@pytest.fixture(autouse=True)
def reset_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_dev_login_403_when_disabled(monkeypatch):
    monkeypatch.setenv("ALLOW_DEV_AUTH", "false")
    get_settings.cache_clear()
    client = TestClient(app)
    r = client.post("/auth/dev-login", json={"role": "clinician"})
    assert r.status_code == 403


def test_dev_login_200_returns_valid_jwt(monkeypatch):
    monkeypatch.setenv("ALLOW_DEV_AUTH", "true")
    get_settings.cache_clear()
    client = TestClient(app)
    r = client.post("/auth/dev-login", json={"role": "clinician", "sub": "cli-1"})
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["role"] == "clinician"
    payload = jwt.decode(body["access_token"], get_settings().secret_key, algorithms=["HS256"])
    assert payload["sub"] == "cli-1"
    assert payload["role"] == "clinician"


def test_dev_login_rejects_non_clinician_role(monkeypatch):
    monkeypatch.setenv("ALLOW_DEV_AUTH", "true")
    get_settings.cache_clear()
    client = TestClient(app)
    r = client.post("/auth/dev-login", json={"role": "patient"})
    assert r.status_code == 422
