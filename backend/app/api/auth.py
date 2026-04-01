"""Authentication helpers — development token endpoint only when explicitly enabled."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException
from jose import jwt
from pydantic import BaseModel, Field

from app.core.config import get_settings

router = APIRouter()


class DevLoginRequest(BaseModel):
    role: Literal["clinician", "admin"] = "clinician"
    sub: str = Field(default="dev-clinician", min_length=1, max_length=128)


@router.post("/auth/dev-login")
async def dev_login(request: DevLoginRequest) -> dict[str, str]:
    settings = get_settings()
    if not settings.allow_dev_auth:
        raise HTTPException(
            status_code=403,
            detail="El inicio de sesión de desarrollo no está habilitado en este entorno.",
        )
    token = jwt.encode(
        {"sub": request.sub, "role": request.role},
        settings.secret_key,
        algorithm="HS256",
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": request.role,
        "sub": request.sub,
    }
