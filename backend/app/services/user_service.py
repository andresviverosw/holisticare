"""US-AUTH-CLINICIAN-PROD — clinician/admin credential helpers."""

from __future__ import annotations

import uuid
from typing import Literal

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser

ALLOWED_ROLES = frozenset({"clinician", "admin"})
AuthRole = Literal["clinician", "admin"]

LOGIN_FAILED = "Invalid username or password"


class AuthError(Exception):
    def __init__(self, message: str = LOGIN_FAILED):
        self.message = message
        super().__init__(message)


def hash_password(password: str) -> str:
    raw = (password or "").encode("utf-8")
    if not raw:
        raise AuthError("Password must not be empty")
    # bcrypt truncates at 72 bytes; reject longer to avoid silent truncation.
    if len(raw) > 72:
        raise AuthError("Password must be at most 72 bytes")
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            (password or "").encode("utf-8"),
            (password_hash or "").encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


async def get_user_by_username(db: AsyncSession, *, username: str) -> AppUser | None:
    normalized = (username or "").strip().lower()
    if not normalized:
        return None
    stmt = select(AppUser).where(AppUser.username == normalized)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_or_update_user(
    db: AsyncSession,
    *,
    username: str,
    password: str,
    role: AuthRole,
    is_active: bool = True,
) -> AppUser:
    normalized = (username or "").strip().lower()
    if not normalized or len(normalized) > 64:
        raise AuthError("Username must be 1–64 characters")
    if role not in ALLOWED_ROLES:
        raise AuthError("Role must be clinician or admin")
    password_hash = hash_password(password)
    existing = await get_user_by_username(db, username=normalized)
    if existing is None:
        row = AppUser(
            id=uuid.uuid4(),
            username=normalized,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return row
    existing.password_hash = password_hash
    existing.role = role
    existing.is_active = is_active
    await db.commit()
    await db.refresh(existing)
    return existing


async def authenticate_user(
    db: AsyncSession,
    *,
    username: str,
    password: str,
) -> AppUser:
    """Verify credentials; raise AuthError with generic message on any failure."""
    user = await get_user_by_username(db, username=username)
    if user is None or not user.is_active:
        raise AuthError()
    if not verify_password(password, user.password_hash):
        raise AuthError()
    if user.role not in ALLOWED_ROLES:
        raise AuthError()
    return user
