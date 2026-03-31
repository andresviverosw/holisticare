from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient_diary_entry import PatientDiaryEntry
from app.schemas.diary_v0 import PatientDiaryCheckinV0


async def upsert_diary_entry(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID,
    checkin: PatientDiaryCheckinV0,
) -> PatientDiaryEntry:
    payload = checkin.model_dump(mode="json")
    stmt = select(PatientDiaryEntry).where(
        PatientDiaryEntry.patient_id == patient_id,
        PatientDiaryEntry.entry_date == checkin.checkin_date,
    )
    result = await db.execute(stmt)
    row = result.scalar_one_or_none()
    if row is None:
        row = PatientDiaryEntry(
            id=uuid.uuid4(),
            patient_id=patient_id,
            entry_date=checkin.checkin_date,
            diary_json=payload,
        )
        db.add(row)
    else:
        row.diary_json = payload
    await db.commit()
    await db.refresh(row)
    return row


async def list_diary_entries_for_patient(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID,
    date_from: date | None,
    date_to: date | None,
    limit: int,
    offset: int,
) -> list[PatientDiaryEntry]:
    stmt = select(PatientDiaryEntry).where(PatientDiaryEntry.patient_id == patient_id)
    if date_from is not None:
        stmt = stmt.where(PatientDiaryEntry.entry_date >= date_from)
    if date_to is not None:
        stmt = stmt.where(PatientDiaryEntry.entry_date <= date_to)
    stmt = (
        stmt.order_by(PatientDiaryEntry.entry_date.desc()).limit(limit).offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def list_diary_entries_in_date_range(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID,
    date_from: date,
    date_to: date,
) -> list[PatientDiaryEntry]:
    stmt = (
        select(PatientDiaryEntry)
        .where(
            PatientDiaryEntry.patient_id == patient_id,
            PatientDiaryEntry.entry_date >= date_from,
            PatientDiaryEntry.entry_date <= date_to,
        )
        .order_by(PatientDiaryEntry.entry_date.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
