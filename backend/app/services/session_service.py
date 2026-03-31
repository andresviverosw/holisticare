from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.care_session import CareSession
from app.schemas.session_v0 import ClinicalSessionLogV0


async def create_care_session(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID,
    practitioner_id: uuid.UUID | None,
    session_log: ClinicalSessionLogV0,
) -> CareSession:
    payload = session_log.model_dump(mode="json")
    row = CareSession(
        id=uuid.uuid4(),
        patient_id=patient_id,
        practitioner_id=practitioner_id,
        occurred_at=session_log.session_at,
        session_json=payload,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def list_care_sessions_for_patient(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID,
    limit: int,
    offset: int,
) -> list[CareSession]:
    stmt = (
        select(CareSession)
        .where(CareSession.patient_id == patient_id)
        .order_by(CareSession.occurred_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
