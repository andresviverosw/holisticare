from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PatientDiaryEntry(Base):
    __tablename__ = "patient_diary_entries"
    __table_args__ = (UniqueConstraint("patient_id", "entry_date", name="uq_patient_diary_entry_day"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    diary_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
