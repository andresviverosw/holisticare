"""US-OPS-HEALTH-001 — DB readiness helpers (pure + async check)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def ping_database(db: AsyncSession) -> None:
    """Raise if Postgres is unreachable or the session cannot execute."""
    await db.execute(text("SELECT 1"))


def check_ready(status_code: int, body: Any) -> list[str]:
    """Pure smoke helper for GET /ready."""
    errors: list[str] = []
    if status_code != 200:
        errors.append(f"ready status_code={status_code} expected 200")
        return errors
    if not isinstance(body, dict):
        errors.append("ready body must be JSON object")
        return errors
    if body.get("status") != "ready":
        errors.append(f"ready status={body.get('status')!r} expected 'ready'")
    if body.get("db") != "ok":
        errors.append(f"ready db={body.get('db')!r} expected 'ok'")
    return errors
