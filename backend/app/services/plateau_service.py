"""
Deterministic plateau / worsening flags from diary outcome series (US-ANLY-002).
"""

from __future__ import annotations

from typing import Any

MIN_DIARY_DAYS = 7
MIN_VALUES_PER_HALF = 3
PAIN_WORSEN_DELTA = 2.0
FUNCTION_WORSEN_DELTA = 2.0
HIGH_PAIN_THRESHOLD = 6.0
PLATEAU_MAX_DELTA = 1.0


def _mean(vals: list[float]) -> float:
    return sum(vals) / len(vals)


def _time_halves(series: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    mid = len(series) // 2
    return series[:mid], series[mid:]


def _values_by_half(
    first_part: list[dict[str, Any]],
    second_part: list[dict[str, Any]],
    key: str,
) -> tuple[list[float], list[float]]:
    v1 = [float(p[key]) for p in first_part if p.get(key) is not None]
    v2 = [float(p[key]) for p in second_part if p.get(key) is not None]
    return v1, v2


def analyze_diary_plateau(
    series: list[dict[str, Any]],
    *,
    data_point_count: int,
) -> tuple[str, list[dict[str, Any]]]:
    """
    Compare first vs second chronological half of the diary window.

    Returns (analysis_status, flags) where analysis_status is ``insufficient_data`` or ``ok``.
    """
    if data_point_count < MIN_DIARY_DAYS or len(series) < MIN_DIARY_DAYS:
        return "insufficient_data", []

    first_part, second_part = _time_halves(series)
    flags: list[dict[str, Any]] = []

    pain1, pain2 = _values_by_half(first_part, second_part, "pain_nrs_0_10")
    if len(pain1) >= MIN_VALUES_PER_HALF and len(pain2) >= MIN_VALUES_PER_HALF:
        m1p, m2p = _mean(pain1), _mean(pain2)
        if m2p - m1p >= PAIN_WORSEN_DELTA:
            flags.append(
                {
                    "code": "PAIN_WORSENING",
                    "severity": "medium",
                    "metric": "pain_nrs_0_10",
                    "message": "El dolor reportado empeora al comparar la primera y la segunda mitad del periodo.",
                    "detail": (
                        f"Promedio primera mitad {m1p:.1f} vs segunda mitad {m2p:.1f} (escala 0–10)."
                    ),
                }
            )
        elif m2p >= HIGH_PAIN_THRESHOLD and abs(m2p - m1p) < PLATEAU_MAX_DELTA:
            flags.append(
                {
                    "code": "HIGH_PAIN_PLATEAU",
                    "severity": "medium",
                    "metric": "pain_nrs_0_10",
                    "message": "El dolor permanece elevado con poca variación entre mitades del periodo.",
                    "detail": (
                        f"Promedio primera mitad {m1p:.1f} vs segunda mitad {m2p:.1f} (escala 0–10)."
                    ),
                }
            )

    f1, f2 = _values_by_half(first_part, second_part, "function_0_10")
    if len(f1) >= MIN_VALUES_PER_HALF and len(f2) >= MIN_VALUES_PER_HALF:
        m1f, m2f = _mean(f1), _mean(f2)
        if m2f - m1f <= -FUNCTION_WORSEN_DELTA:
            flags.append(
                {
                    "code": "FUNCTION_WORSENING",
                    "severity": "medium",
                    "metric": "function_0_10",
                    "message": "La función reportada disminuye al comparar la primera y la segunda mitad del periodo.",
                    "detail": (
                        f"Promedio primera mitad {m1f:.1f} vs segunda mitad {m2f:.1f} (escala 0–10)."
                    ),
                }
            )

    return "ok", flags
