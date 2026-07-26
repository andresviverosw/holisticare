"""US-ANLY / US-PRED — analytics date window anchors on latest diary when defaults used."""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.patient_diary_entry import PatientDiaryEntry
from app.services.analytics_service import (
    DEFAULT_DAYS,
    get_patient_recovery_trajectory_payload,
    resolve_analytics_date_window,
    resolve_analytics_date_window_for_anchor,
)


def test_resolve_window_defaults_to_today_minus_default_days():
    d0, d1 = resolve_analytics_date_window(None, None)
    assert d1 == date.today()
    assert d0 == d1 - timedelta(days=DEFAULT_DAYS)


def test_resolve_window_for_anchor_uses_latest_diary_not_wall_clock():
    """Synthetic corpus (Feb–Apr) must remain visible after calendar advances."""
    latest = date(2026, 4, 16)
    d0, d1 = resolve_analytics_date_window_for_anchor(None, None, latest_diary_date=latest)
    assert d1 == latest
    assert d0 == latest - timedelta(days=DEFAULT_DAYS)


def test_explicit_dates_ignore_anchor():
    d0, d1 = resolve_analytics_date_window_for_anchor(
        date(2026, 1, 1),
        date(2026, 1, 31),
        latest_diary_date=date(2026, 4, 16),
    )
    assert d0 == date(2026, 1, 1)
    assert d1 == date(2026, 1, 31)


def test_missing_diary_falls_back_to_calendar_default():
    d0, d1 = resolve_analytics_date_window_for_anchor(None, None, latest_diary_date=None)
    assert d1 == date.today()
    assert d0 == d1 - timedelta(days=DEFAULT_DAYS)


@pytest.mark.asyncio
async def test_recovery_payload_anchors_on_latest_diary_when_dates_omitted():
    """Wall-clock today must not hide synthetic diaries that ended months earlier."""
    pid = uuid.uuid4()
    latest = date(2026, 4, 16)
    rows = [
        PatientDiaryEntry(
            id=uuid.uuid4(),
            patient_id=pid,
            entry_date=latest - timedelta(days=offset),
            diary_json={"pain_nrs_0_10": pain},
        )
        for offset, pain in [(40, 8), (30, 7), (20, 6), (10, 5), (0, 4)]
    ]

    db = AsyncMock()
    call_n = {"n": 0}

    async def execute(_stmt):
        call_n["n"] += 1
        result = MagicMock()
        if call_n["n"] == 1:
            result.scalar_one_or_none.return_value = latest
            return result
        result.scalars.return_value.all.return_value = rows
        return result

    db.execute = AsyncMock(side_effect=execute)

    payload = await get_patient_recovery_trajectory_payload(
        db,
        patient_id=pid,
        date_from=None,
        date_to=None,
    )

    assert payload["date_to"] == latest.isoformat()
    assert payload["date_from"] == (latest - timedelta(days=DEFAULT_DAYS)).isoformat()
    assert payload["data_points_used"] == 5
    assert payload["analysis_status"] == "ok"
    assert payload["trajectory"]["label"] == "improving"
