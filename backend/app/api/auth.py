"""Authentication — always-on redeem + optional dev-login (ALLOW_DEV_AUTH)."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
import jwt
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.services.diary_invite_service import InviteError, redeem_diary_invite
from app.services.user_service import AuthError, authenticate_user

# Always mounted by `create_app()`.
auth_router = APIRouter()

# Included by `create_app()` only when `Settings.allow_dev_auth` is true.
dev_auth_router = APIRouter()

# RFC-4122 UUID version 4 (matches frontend `isValidUuidV4` / US-DIARY-UI-PATIENT).
_UUID_V4 = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


class DevLoginRequest(BaseModel):
    role: Literal["clinician", "admin", "patient"] = "clinician"
    sub: str = Field(default="dev-clinician", min_length=1, max_length=128)

    @model_validator(mode="after")
    def patient_sub_must_be_uuid_v4(self) -> DevLoginRequest:
        if self.role == "patient" and not _UUID_V4.match(self.sub.strip()):
            raise ValueError("patient role requires sub to be a UUID version 4")
        return self


class RedeemInviteRequest(BaseModel):
    token: str = Field(min_length=1, max_length=512)


class PasswordLoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


def encode_access_token(*, sub: str, role: str, exp: datetime | None = None) -> str:
    settings = get_settings()
    payload: dict = {"sub": sub, "role": role}
    if exp is not None:
        payload["exp"] = exp
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


@auth_router.post("/auth/login")
async def password_login(
    request: PasswordLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """US-AUTH-CLINICIAN-PROD — username/password → clinician/admin JWT with exp."""
    settings = get_settings()
    try:
        user = await authenticate_user(db, username=request.username, password=request.password)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=exc.message) from exc

    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=settings.clinician_jwt_ttl_hours)
    token = encode_access_token(sub=str(user.id), role=user.role, exp=exp)
    return {
        "access_token": token,
        "token_type": "bearer",  # nosec B105
        "role": user.role,
        "sub": str(user.id),
        "expires_at": exp.isoformat().replace("+00:00", "Z"),
    }


@dev_auth_router.post("/auth/dev-login")
async def dev_login(request: DevLoginRequest) -> dict[str, str]:
    token = encode_access_token(sub=request.sub, role=request.role)
    return {
        "access_token": token,
        # Literal OAuth 2.0 token_type (RFC 6749); Bandit flags the string as B105 otherwise.
        "token_type": "bearer",  # nosec B105
        "role": request.role,
        "sub": request.sub,
    }


@auth_router.post("/auth/redeem-invite")
async def redeem_invite(
    request: RedeemInviteRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """US-DIARY-AUTH-PROD — public single-use invite → patient JWT with exp."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    try:
        invite = await redeem_diary_invite(db, token=request.token, now=now)
    except InviteError as exc:
        raise HTTPException(status_code=410, detail=exc.message) from exc

    exp = now + timedelta(hours=settings.patient_jwt_ttl_hours)
    token = encode_access_token(sub=str(invite.patient_id), role="patient", exp=exp)
    return {
        "access_token": token,
        "token_type": "bearer",  # nosec B105
        "role": "patient",
        "sub": str(invite.patient_id),
        "expires_at": exp.isoformat().replace("+00:00", "Z"),
    }
