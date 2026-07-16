"""Unit tests for diary invite create/redeem (US-DIARY-AUTH-PROD)."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.patient_diary_invite import PatientDiaryInvite
from app.services.diary_invite_service import (
    InviteError,
    assert_invite_redeemable,
    create_diary_invite,
    hash_invite_token,
    redeem_diary_invite,
)

PATIENT_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
NOW = datetime(2026, 7, 16, 12, 0, 0, tzinfo=timezone.utc)


def test_hash_invite_token_is_sha256_hex():
    digest = hash_invite_token("abc")
    assert len(digest) == 64
    assert digest == hash_invite_token("abc")
    assert digest != hash_invite_token("abd")


def test_assert_invite_redeemable_rejects_missing_used_expired():
    with pytest.raises(InviteError):
        assert_invite_redeemable(None, now=NOW)

    used = PatientDiaryInvite(
        id=uuid.uuid4(),
        patient_id=PATIENT_ID,
        token_hash="x" * 64,
        expires_at=NOW + timedelta(days=1),
        redeemed_at=NOW,
        created_by_sub="clin",
    )
    with pytest.raises(InviteError):
        assert_invite_redeemable(used, now=NOW)

    expired = PatientDiaryInvite(
        id=uuid.uuid4(),
        patient_id=PATIENT_ID,
        token_hash="y" * 64,
        expires_at=NOW - timedelta(seconds=1),
        redeemed_at=None,
        created_by_sub="clin",
    )
    with pytest.raises(InviteError):
        assert_invite_redeemable(expired, now=NOW)


@pytest.mark.asyncio
async def test_create_diary_invite_stores_hash_not_plaintext(monkeypatch):
    monkeypatch.setenv("DIARY_INVITE_TTL_HOURS", "24")
    from app.core.config import get_settings

    get_settings.cache_clear()

    db = AsyncMock()
    db.add = MagicMock()
    created = await create_diary_invite(
        db,
        patient_id=PATIENT_ID,
        created_by_sub="clin-1",
        now=NOW,
    )
    db.add.assert_called_once()
    row = db.add.call_args[0][0]
    assert row.token_hash == hash_invite_token(created.plaintext_token)
    assert created.plaintext_token not in row.token_hash
    assert row.expires_at == NOW + timedelta(hours=24)
    assert row.patient_id == PATIENT_ID
    db.commit.assert_awaited_once()
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_redeem_diary_invite_marks_redeemed():
    token = "one-time-secret-token"
    invite = PatientDiaryInvite(
        id=uuid.uuid4(),
        patient_id=PATIENT_ID,
        token_hash=hash_invite_token(token),
        expires_at=NOW + timedelta(days=1),
        redeemed_at=None,
        created_by_sub="clin-1",
    )
    db = AsyncMock()
    exec_result = MagicMock()
    exec_result.scalar_one_or_none.return_value = invite
    db.execute = AsyncMock(return_value=exec_result)

    row = await redeem_diary_invite(db, token=token, now=NOW)
    assert row.redeemed_at == NOW
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_redeem_diary_invite_rejects_unknown_token():
    db = AsyncMock()
    exec_result = MagicMock()
    exec_result.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=exec_result)

    with pytest.raises(InviteError):
        await redeem_diary_invite(db, token="missing", now=NOW)
