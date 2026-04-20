from __future__ import annotations

import uuid
from datetime import date, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient_diary_entry import PatientDiaryEntry
from app.services.diary_service import list_diary_entries_in_date_range
from app.services.plateau_service import analyze_diary_plateau

MAX_RANGE_DAYS = 731
DEFAULT_DAYS = 90
MIN_RECOVERY_POINTS = 5


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


def estimate_recovery_trajectory_from_series(series: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Estimate short-term recovery trajectory from diary pain trend.

    Rules:
    - Requires >= MIN_RECOVERY_POINTS entries with valid pain scores.
    - Uses first/last pain and elapsed days to estimate slope_per_day.
    - Projects pain level 4 weeks (28 days) ahead.
    """
    pain_points = [
        (row.get("date"), row.get("pain_nrs_0_10"))
        for row in series
        if isinstance(row.get("pain_nrs_0_10"), (int, float))
    ]

    if len(pain_points) < MIN_RECOVERY_POINTS:
        return {
            "analysis_status": "insufficient_data",
            "reason": f"Se requieren al menos {MIN_RECOVERY_POINTS} registros con dolor para estimar trayectoria.",
            "trajectory": None,
        }

    first_date = date.fromisoformat(str(pain_points[0][0]))
    last_date = date.fromisoformat(str(pain_points[-1][0]))
    elapsed_days = (last_date - first_date).days
    if elapsed_days <= 0:
        return {
            "analysis_status": "insufficient_data",
            "reason": "Se requieren registros en fechas diferentes para estimar tendencia.",
            "trajectory": None,
        }

    first_pain = float(pain_points[0][1])
    last_pain = float(pain_points[-1][1])
    slope_per_day = (last_pain - first_pain) / elapsed_days
    projected_4w = max(0.0, min(10.0, last_pain + (slope_per_day * 28.0)))

    if slope_per_day <= -0.05:
        label = "improving"
    elif slope_per_day >= 0.05:
        label = "worsening"
    else:
        label = "stable"

    return {
        "analysis_status": "ok",
        "reason": None,
        "trajectory": {
            "label": label,
            "baseline_pain_nrs": round(first_pain, 2),
            "latest_pain_nrs": round(last_pain, 2),
            "slope_per_day": round(slope_per_day, 4),
            "projected_pain_nrs_in_4_weeks": round(projected_4w, 2),
        },
    }


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


async def get_patient_plateau_flags_payload(
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
    series = diary_entries_to_outcome_series(rows)
    status, flags = analyze_diary_plateau(series, data_point_count=len(rows))
    return {
        "patient_id": str(patient_id),
        "source": "patient_diary_v0",
        "date_from": d0.isoformat(),
        "date_to": d1.isoformat(),
        "analysis_status": status,
        "data_points_used": len(rows),
        "flags": flags,
    }


async def get_patient_recovery_trajectory_payload(
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
    series = diary_entries_to_outcome_series(rows)
    prediction = estimate_recovery_trajectory_from_series(series)
    return {
        "patient_id": str(patient_id),
        "source": "patient_diary_v0",
        "date_from": d0.isoformat(),
        "date_to": d1.isoformat(),
        "data_points_used": len(rows),
        **prediction,
    }
