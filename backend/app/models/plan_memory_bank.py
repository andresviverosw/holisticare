from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PlanMemoryBankEntry(Base):
    """
    Immutable snapshot of an approved plan for reuse as a draft template (US-PLAN-004).
    Does not store patient identifiers in snapshot_json.
    """

    __tablename__ = "plan_memory_bank"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    therapy_types: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    language: Mapped[str | None] = mapped_column(String(8), nullable=True)
    snapshot_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    created_by_sub: Mapped[str] = mapped_column(String(255), nullable=False)
