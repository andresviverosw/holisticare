"""FastAPI dependencies — override in tests via app.dependency_overrides for CI-safe runs."""

from __future__ import annotations

import uuid

from pydantic import BaseModel
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import get_settings
from app.rag.pipeline import RAGPipeline
from app.services.ingestion_service import IngestionService

security = HTTPBearer(auto_error=False)


class AuthUser(BaseModel):
    sub: str
    role: str


def get_rag_pipeline() -> RAGPipeline:
    """Default: real pipeline (requires DB + APIs unless subsystems are mocked)."""
    return RAGPipeline()


def get_ingestion_service() -> IngestionService:
    """Default: real ingestion service (can be overridden in tests)."""
    return IngestionService()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AuthUser:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    settings = get_settings()
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=["HS256"])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication token") from exc
    role = payload.get("role")
    if not role:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return AuthUser(sub=str(payload.get("sub", "unknown")), role=str(role))


def require_roles(*allowed_roles: str):
    def _checker(user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return _checker


def ensure_diary_subject_access(user: AuthUser, patient_id: uuid.UUID) -> None:
    """Patients may only read/write diary data for their own patient_id (sub must be that UUID)."""
    if user.role != "patient":
        return
    try:
        sub_id = uuid.UUID(user.sub)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail="Forbidden") from exc
    if sub_id != patient_id:
        raise HTTPException(status_code=403, detail="Forbidden")
