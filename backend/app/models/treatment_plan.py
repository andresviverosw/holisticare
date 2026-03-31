from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TreatmentPlan(Base):
    __tablename__ = "treatment_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    practitioner_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default="pending_review",
    )
    plan_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    citations_used: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
