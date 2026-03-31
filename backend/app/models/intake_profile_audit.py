from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class IntakeProfileAudit(Base):
    __tablename__ = "intake_profile_audit"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    actor_sub: Mapped[str] = mapped_column(String(128), nullable=False)
    before_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    after_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
