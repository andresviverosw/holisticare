"""US-DIARY-AUTH-PROD — create/redeem single-use patient diary invites."""

from __future__ import annotations

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.patient_diary_invite import PatientDiaryInvite

INVITE_UNUSABLE = "Invite invalid, expired, or already used"


class InviteError(Exception):
    """Domain failure for invite create/redeem (map to HTTP in API layer)."""

    def __init__(self, message: str = INVITE_UNUSABLE):
        self.message = message
        super().__init__(message)


def hash_invite_token(token: str) -> str:
    return hashlib.sha256(token.strip().encode("utf-8")).hexdigest()


def generate_invite_token() -> str:
    return secrets.token_urlsafe(32)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class CreatedInvite:
    invite: PatientDiaryInvite
    plaintext_token: str


async def create_diary_invite(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID,
    created_by_sub: str,
    ttl_hours: int | None = None,
    now: datetime | None = None,
) -> CreatedInvite:
    settings = get_settings()
    hours = ttl_hours if ttl_hours is not None else settings.diary_invite_ttl_hours
    if hours < 1:
        raise InviteError("Invite TTL must be at least 1 hour")
    when = now or _utcnow()
    token = generate_invite_token()
    row = PatientDiaryInvite(
        id=uuid.uuid4(),
        patient_id=patient_id,
        token_hash=hash_invite_token(token),
        expires_at=when + timedelta(hours=hours),
        redeemed_at=None,
        created_by_sub=created_by_sub,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return CreatedInvite(invite=row, plaintext_token=token)


def assert_invite_redeemable(invite: PatientDiaryInvite | None, *, now: datetime | None = None) -> PatientDiaryInvite:
    when = now or _utcnow()
    if invite is None:
        raise InviteError()
    expires = invite.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if invite.redeemed_at is not None:
        raise InviteError()
    if expires <= when:
        raise InviteError()
    return invite


async def redeem_diary_invite(
    db: AsyncSession,
    *,
    token: str,
    now: datetime | None = None,
) -> PatientDiaryInvite:
    raw = (token or "").strip()
    if not raw:
        raise InviteError()
    when = now or _utcnow()
    stmt = select(PatientDiaryInvite).where(PatientDiaryInvite.token_hash == hash_invite_token(raw))
    result = await db.execute(stmt)
    invite = assert_invite_redeemable(result.scalar_one_or_none(), now=when)
    invite.redeemed_at = when
    await db.commit()
    await db.refresh(invite)
    return invite
