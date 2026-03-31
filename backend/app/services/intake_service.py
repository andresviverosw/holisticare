from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.intake_profile import IntakeProfile
from app.models.intake_profile_audit import IntakeProfileAudit


async def save_intake_profile(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID,
    practitioner_id: uuid.UUID | None,
    intake_json: dict[str, Any],
) -> IntakeProfile:
    existing = await get_intake_profile(db, patient_id=patient_id)
    if existing is None:
        row = IntakeProfile(
            id=uuid.uuid4(),
            patient_id=patient_id,
            practitioner_id=practitioner_id,
            intake_json=dict(intake_json),
        )
        db.add(row)
    else:
        row = existing
        row.practitioner_id = practitioner_id
        row.intake_json = dict(intake_json)

    await db.commit()
    await db.refresh(row)
    return row


async def get_intake_profile(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID,
) -> IntakeProfile | None:
    stmt = select(IntakeProfile).where(IntakeProfile.patient_id == patient_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_intake_profile_with_audit(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID,
    actor_sub: str,
    intake_json: dict[str, Any],
    practitioner_id: uuid.UUID | None = None,
) -> IntakeProfile | None:
    row = await get_intake_profile(db, patient_id=patient_id)
    if row is None:
        return None

    before = dict(row.intake_json)
    row.intake_json = dict(intake_json)
    if practitioner_id is not None:
        row.practitioner_id = practitioner_id

    audit = IntakeProfileAudit(
        id=uuid.uuid4(),
        patient_id=patient_id,
        actor_sub=actor_sub,
        before_json=before,
        after_json=dict(intake_json),
    )
    db.add(audit)
    await db.commit()
    await db.refresh(row)
    return row
