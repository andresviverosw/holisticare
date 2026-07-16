"""Dev-only JWT issuance for local / SPA testing (disabled by default)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
import jwt

from app.core.config import get_settings
from app.main import create_app

PATIENT_UUID = "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture(autouse=True)
def reset_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_dev_login_route_absent_when_disabled(monkeypatch):
    monkeypatch.setenv("ALLOW_DEV_AUTH", "false")
    get_settings.cache_clear()
    client = TestClient(create_app())
    r = client.post("/auth/dev-login", json={"role": "clinician"})
    assert r.status_code == 404


def test_dev_login_200_returns_valid_jwt(monkeypatch):
    monkeypatch.setenv("ALLOW_DEV_AUTH", "true")
    get_settings.cache_clear()
    client = TestClient(create_app())
    r = client.post("/auth/dev-login", json={"role": "clinician", "sub": "cli-1"})
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["role"] == "clinician"
    payload = jwt.decode(body["access_token"], get_settings().secret_key, algorithms=["HS256"])
    assert payload["sub"] == "cli-1"
    assert payload["role"] == "clinician"


def test_dev_login_rejects_unknown_role(monkeypatch):
    monkeypatch.setenv("ALLOW_DEV_AUTH", "true")
    get_settings.cache_clear()
    client = TestClient(create_app())
    r = client.post("/auth/dev-login", json={"role": "superuser"})
    assert r.status_code == 422


def test_dev_login_patient_requires_uuid_v4_sub(monkeypatch):
    """US-DIARY-UI-PATIENT: patient tokens must bind to a UUID v4 patient id."""
    monkeypatch.setenv("ALLOW_DEV_AUTH", "true")
    get_settings.cache_clear()
    client = TestClient(create_app())
    r = client.post("/auth/dev-login", json={"role": "patient", "sub": "not-a-uuid"})
    assert r.status_code == 422


def test_dev_login_patient_200_with_uuid_v4_sub(monkeypatch):
    """US-DIARY-UI-PATIENT: valid patient + UUID sub yields bearer JWT."""
    monkeypatch.setenv("ALLOW_DEV_AUTH", "true")
    get_settings.cache_clear()
    client = TestClient(create_app())
    r = client.post("/auth/dev-login", json={"role": "patient", "sub": PATIENT_UUID})
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["role"] == "patient"
    assert body["sub"] == PATIENT_UUID
    payload = jwt.decode(body["access_token"], get_settings().secret_key, algorithms=["HS256"])
    assert payload["sub"] == PATIENT_UUID
    assert payload["role"] == "patient"
