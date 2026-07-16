"""Authentication — dev-only JWT endpoint (router included only when ALLOW_DEV_AUTH is true)."""

from __future__ import annotations

import re
from typing import Literal

from fastapi import APIRouter
import jwt
from pydantic import BaseModel, Field, model_validator

from app.core.config import get_settings

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
