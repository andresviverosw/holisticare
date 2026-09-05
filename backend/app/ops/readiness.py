"""US-OPS-HEALTH-001 — DB readiness ping for GET /ready.

Pure HTTP contract checks for smoke live in `public_demo_smoke.check_ready`
so CD can run with httpx-only installs (no SQLAlchemy).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def ping_database(db: "AsyncSession") -> None:
    """Raise if Postgres is unreachable or the session cannot execute."""
    from sqlalchemy import text

    await db.execute(text("SELECT 1"))


# Back-compat for tests that imported check_ready from this module.
from app.ops.public_demo_smoke import check_ready as check_ready  # noqa: E402

__all__ = ["ping_database", "check_ready"]
