"""Unit tests for diary upsert (no HTTP)."""

from __future__ import annotations

import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.patient_diary_entry import PatientDiaryEntry
from app.schemas.diary_v0 import PatientDiaryCheckinV0
from app.services.diary_service import upsert_diary_entry

PATIENT_ID = uuid.uuid4()


def _checkin(pain: int = 3) -> PatientDiaryCheckinV0:
    return PatientDiaryCheckinV0(
        profile_version="patient_diary_v0",
        checkin_date=date(2026, 4, 2),
        pain_nrs_0_10=pain,
        sleep_quality_0_10=5,
        mood_0_10=6,
        function_0_10=4,
    )


@pytest.mark.asyncio
async def test_upsert_creates_when_missing():
    db = AsyncMock()
    db.add = MagicMock()
    exec_result = MagicMock()
    exec_result.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=exec_result)

    row = await upsert_diary_entry(db, patient_id=PATIENT_ID, checkin=_checkin())
    db.add.assert_called_once()
    assert row.patient_id == PATIENT_ID
    assert row.entry_date == date(2026, 4, 2)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_upsert_updates_when_same_day_exists():
    existing = PatientDiaryEntry(
        id=uuid.uuid4(),
        patient_id=PATIENT_ID,
        entry_date=date(2026, 4, 2),
        diary_json={"profile_version": "patient_diary_v0", "pain_nrs_0_10": 1},
    )
    db = AsyncMock()
    db.add = MagicMock()
    exec_result = MagicMock()
    exec_result.scalar_one_or_none.return_value = existing
    db.execute = AsyncMock(return_value=exec_result)

    await upsert_diary_entry(db, patient_id=PATIENT_ID, checkin=_checkin(pain=8))
    db.add.assert_not_called()
    assert existing.diary_json["pain_nrs_0_10"] == 8
    db.commit.assert_awaited_once()
