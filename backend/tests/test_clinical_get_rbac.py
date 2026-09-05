"""US-SEC-RBAC-001 — clinical GET endpoints must require clinician/admin JWT."""

from __future__ import annotations

import uuid

import jwt
import pytest
from fastapi.testclient import TestClient

from app.api.deps import AuthUser, get_current_user
from app.core.config import get_settings
from app.main import app

PATIENT_ID = str(uuid.uuid4())
PLAN_ID = str(uuid.uuid4())

CLINICAL_GETS = (
    f"/rag/intake/{PATIENT_ID}",
    f"/rag/intake/{PATIENT_ID}/risk-flags",
    f"/rag/plan/{PLAN_ID}",
    f"/rag/plan/{PLAN_ID}/sources",
    "/rag/chunks",
)


def _auth_header(role: str, sub: str = "user-1") -> dict[str, str]:
    token = jwt.encode(
        {"sub": sub, "role": role},
        get_settings().secret_key,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize("path", CLINICAL_GETS)
def test_clinical_get_401_when_unauthenticated(client: TestClient, path: str):
    app.dependency_overrides.pop(get_current_user, None)
    try:
        response = client.get(path)
    finally:
        app.dependency_overrides[get_current_user] = lambda: AuthUser(
            sub="test-user", role="clinician"
        )
    assert response.status_code == 401


@pytest.mark.parametrize("path", CLINICAL_GETS)
def test_clinical_get_403_when_patient_role(client: TestClient, path: str):
    app.dependency_overrides.pop(get_current_user, None)
    try:
        response = client.get(path, headers=_auth_header("patient", sub=PATIENT_ID))
    finally:
        app.dependency_overrides[get_current_user] = lambda: AuthUser(
            sub="test-user", role="clinician"
        )
    assert response.status_code == 403
