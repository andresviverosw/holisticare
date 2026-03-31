"""
Pytest bootstrap: CI-safe env before any app imports, and HTTP client fixtures
that never require PostgreSQL or external APIs for contract tests.

Run from repo root: `pytest` (see root pytest.ini) or from `backend/`: `pytest tests/ -q`
"""

from __future__ import annotations

import os


def _ensure_test_env() -> None:
    """Defaults so Settings and imports succeed without a local .env (CI, fresh clones)."""
    defaults = {
        "POSTGRES_USER": "ci_holisticare",
        "POSTGRES_PASSWORD": "ci",
        "POSTGRES_DB": "ci",
        "POSTGRES_HOST": "127.0.0.1",
        "ANTHROPIC_API_KEY": "sk-ant-api-ci-dummy-not-used-in-default-tests",
        "OPENAI_API_KEY": "sk-ci-dummy-not-used-in-default-tests",
        "SECRET_KEY": "ci-secret-key-for-tests-only-32chars-min",
    }
    for key, val in defaults.items():
        os.environ.setdefault(key, val)


_ensure_test_env()

import pytest  # noqa: E402
from unittest.mock import AsyncMock, MagicMock  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.api.deps import get_current_user, AuthUser  # noqa: E402
from app.core.database import get_db  # noqa: E402


def _mock_db_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


async def _mock_get_db():
    yield _mock_db_session()


@pytest.fixture
def client() -> TestClient:
    """HTTP client with DB session stubbed — no PostgreSQL required."""
    app.dependency_overrides[get_db] = _mock_get_db
    app.dependency_overrides[get_current_user] = lambda: AuthUser(sub="test-user", role="clinician")
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
