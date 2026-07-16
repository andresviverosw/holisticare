"""Unit tests for clinician password helpers (US-AUTH-CLINICIAN-PROD)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.app_user import AppUser
from app.services.user_service import (
    AuthError,
    authenticate_user,
    create_or_update_user,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password_roundtrip():
    digest = hash_password("correct-horse")
    assert digest != "correct-horse"
    assert verify_password("correct-horse", digest)
    assert not verify_password("wrong", digest)


def test_hash_password_rejects_empty():
    with pytest.raises(AuthError):
        hash_password("")


@pytest.mark.asyncio
async def test_create_or_update_user_creates_hashed_row():
    db = AsyncMock()
    db.add = MagicMock()
    exec_result = MagicMock()
    exec_result.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=exec_result)

    user = await create_or_update_user(
        db,
        username="  Clinician1 ",
        password="s3cret-pass",
        role="clinician",
    )
    db.add.assert_called_once()
    row = db.add.call_args[0][0]
    assert row.username == "clinician1"
    assert row.role == "clinician"
    assert row.password_hash != "s3cret-pass"
    assert verify_password("s3cret-pass", row.password_hash)
    assert user is row


@pytest.mark.asyncio
async def test_create_or_update_user_updates_existing():
    existing = AppUser(
        id=uuid.uuid4(),
        username="clinician1",
        password_hash=hash_password("old"),
        role="clinician",
        is_active=True,
    )
    db = AsyncMock()
    db.add = MagicMock()
    exec_result = MagicMock()
    exec_result.scalar_one_or_none.return_value = existing
    db.execute = AsyncMock(return_value=exec_result)

    await create_or_update_user(
        db,
        username="clinician1",
        password="new-pass",
        role="admin",
    )
    db.add.assert_not_called()
    assert existing.role == "admin"
    assert verify_password("new-pass", existing.password_hash)


@pytest.mark.asyncio
async def test_authenticate_user_success():
    user = AppUser(
        id=uuid.uuid4(),
        username="clinician1",
        password_hash=hash_password("ok"),
        role="clinician",
        is_active=True,
    )
    db = AsyncMock()
    exec_result = MagicMock()
    exec_result.scalar_one_or_none.return_value = user
    db.execute = AsyncMock(return_value=exec_result)

    got = await authenticate_user(db, username="Clinician1", password="ok")
    assert got.id == user.id


@pytest.mark.asyncio
async def test_authenticate_user_rejects_wrong_password_and_inactive():
    user = AppUser(
        id=uuid.uuid4(),
        username="clinician1",
        password_hash=hash_password("ok"),
        role="clinician",
        is_active=True,
    )
    db = AsyncMock()
    exec_result = MagicMock()
    exec_result.scalar_one_or_none.return_value = user
    db.execute = AsyncMock(return_value=exec_result)

    with pytest.raises(AuthError):
        await authenticate_user(db, username="clinician1", password="nope")

    user.is_active = False
    with pytest.raises(AuthError):
        await authenticate_user(db, username="clinician1", password="ok")

    exec_result.scalar_one_or_none.return_value = None
    with pytest.raises(AuthError):
        await authenticate_user(db, username="missing", password="ok")
