"""Authentication — dev-only JWT endpoint (router included only when ALLOW_DEV_AUTH is true)."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter
from jose import jwt
from pydantic import BaseModel, Field

from app.core.config import get_settings

# Included by `create_app()` only when `Settings.allow_dev_auth` is true.
dev_auth_router = APIRouter()


class DevLoginRequest(BaseModel):
    role: Literal["clinician", "admin"] = "clinician"
    sub: str = Field(default="dev-clinician", min_length=1, max_length=128)


@dev_auth_router.post("/auth/dev-login")
async def dev_login(request: DevLoginRequest) -> dict[str, str]:
    settings = get_settings()
    token = jwt.encode(
        {"sub": request.sub, "role": request.role},
        settings.secret_key,
        algorithm="HS256",
    )
    return {
        "access_token": token,
        # Literal OAuth 2.0 token_type (RFC 6749); Bandit flags the string as B105 otherwise.
        "token_type": "bearer",  # nosec B105
        "role": request.role,
        "sub": request.sub,
    }
