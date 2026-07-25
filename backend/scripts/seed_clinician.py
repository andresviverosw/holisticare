"""
seed_clinician.py — bootstrap one clinician/admin user (US-AUTH-CLINICIAN-PROD).

Usage (from repo / compose):
    SEED_CLINICIAN_USERNAME=clinician \\
    SEED_CLINICIAN_PASSWORD='strong-password' \\
    SEED_CLINICIAN_ROLE=clinician \\
    python -m scripts.seed_clinician

Idempotent: re-running updates password/role for the same username.
Never commit real passwords.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal  # noqa: E402
from app.services.user_service import ALLOWED_ROLES, create_or_update_user  # noqa: E402


async def _run() -> int:
    username = (os.environ.get("SEED_CLINICIAN_USERNAME") or "").strip()
    password = os.environ.get("SEED_CLINICIAN_PASSWORD") or ""
    role = (os.environ.get("SEED_CLINICIAN_ROLE") or "clinician").strip().lower()

    if not username or not password:
        print(
            "ERROR: Set SEED_CLINICIAN_USERNAME and SEED_CLINICIAN_PASSWORD "
            "(and optionally SEED_CLINICIAN_ROLE=clinician|admin).",
            file=sys.stderr,
        )
        return 1
    if role not in ALLOWED_ROLES:
        print(f"ERROR: SEED_CLINICIAN_ROLE must be one of {sorted(ALLOWED_ROLES)}.", file=sys.stderr)
        return 1

    async with AsyncSessionLocal() as db:
        user = await create_or_update_user(
            db,
            username=username,
            password=password,
            role=role,  # type: ignore[arg-type]
            is_active=True,
        )
    print(f"OK: user id={user.id} username={user.username} role={user.role}")
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(_run()))


if __name__ == "__main__":
    main()
