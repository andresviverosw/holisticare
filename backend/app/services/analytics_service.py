from __future__ import annotations

import uuid
from datetime import date, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient_diary_entry import PatientDiaryEntry
from app.services.diary_service import list_diary_entries_in_date_range

MAX_RANGE_DAYS = 731
DEFAULT_DAYS = 90


def resolve_analytics_date_window(
    date_from: date | None,
    date_to: date | None,
) -> tuple[date, date]:
    if date_to is None:
        date_to = date.today()
    if date_from is None:
        date_from = date_to - timedelta(days=DEFAULT_DAYS)
    if date_from > date_to:
        raise ValueError("La fecha inicial debe ser anterior o igual a la fecha final.")
    if (date_to - date_from).days > MAX_RANGE_DAYS:
        raise ValueError(f"El rango no puede superar {MAX_RANGE_DAYS} días.")
    return date_from, date_to


def diary_entries_to_outcome_series(rows: list[PatientDiaryEntry]) -> list[dict[str, Any]]:
    series: list[dict[str, Any]] = []
    for r in rows:
        j = r.diary_json or {}
        series.append(
            {
                "date": r.entry_date.isoformat(),
                "pain_nrs_0_10": j.get("pain_nrs_0_10"),
                "sleep_quality_0_10": j.get("sleep_quality_0_10"),
                "mood_0_10": j.get("mood_0_10"),
                "function_0_10": j.get("function_0_10"),
            }
        )
    return series


async def get_patient_outcomes_trend_payload(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID,
    date_from: date | None,
    date_to: date | None,
) -> dict[str, Any]:
    d0, d1 = resolve_analytics_date_window(date_from, date_to)
    rows = await list_diary_entries_in_date_range(
        db,
        patient_id=patient_id,
        date_from=d0,
        date_to=d1,
    )
    return {
        "patient_id": str(patient_id),
        "source": "patient_diary_v0",
        "date_from": d0.isoformat(),
        "date_to": d1.isoformat(),
        "series": diary_entries_to_outcome_series(rows),
    }
