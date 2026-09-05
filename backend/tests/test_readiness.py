"""US-OPS-HEALTH-001 — readiness probe contract tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.ops.readiness import check_ready


def test_check_ready_ok():
    assert check_ready(200, {"status": "ready", "db": "ok"}) == []


def test_check_ready_rejects_non_200():
    errs = check_ready(503, {"status": "ready", "db": "ok"})
    assert any("status_code" in e for e in errs)


def test_check_ready_rejects_bad_payload():
    errs = check_ready(200, {"status": "ok"})
    assert errs


def test_ready_200_when_db_ping_succeeds(client: TestClient):
    session = AsyncMock()
    session.execute = AsyncMock(return_value=MagicMock())

    async def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json() == {"status": "ready", "db": "ok"}
    session.execute.assert_awaited()


def test_ready_503_when_db_ping_fails(client: TestClient):
    session = AsyncMock()
    session.execute = AsyncMock(side_effect=RuntimeError("connection refused"))

    async def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    r = client.get("/ready")
    assert r.status_code == 503
    assert r.json()["detail"] == "database_unavailable"
