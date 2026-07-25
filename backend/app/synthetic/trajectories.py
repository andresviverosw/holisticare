"""Diary outcome series generators for analytics/plateau/KPI coverage (SYNTH-01)."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

TrajectoryId = Literal["improving", "high_pain_plateau", "worsening", "short_series"]

TRAJECTORIES: tuple[TrajectoryId, ...] = (
    "improving",
    "high_pain_plateau",
    "worsening",
    "short_series",
)

ADVERSE_NOTES = (
    "Posible evento adverso: aumento de dolor tras la sesión.",
    "Hoy empeoró la molestia después de caminar más de lo habitual.",
    "Nota: leve un evento adverso digestivo post-comida.",
)

ROUTINE_NOTES = (
    "Dolor moderado, mejor en la mañana.",
    "Sueño irregular pero estable.",
    "Ánimo aceptable; cumplí ejercicios en casa.",
    "Funcionalidad suficiente para actividades básicas.",
    "Sin cambios relevantes hoy.",
    None,
    None,
    None,
)


@dataclass(frozen=True)
class DiaryPoint:
    entry_date: date
    pain: int
    sleep: int
    mood: int
    function: int
    notes_es: str | None


def _clamp(v: float) -> int:
    return max(0, min(10, int(round(v))))


def _pick_note(rng: random.Random, *, force_adverse: bool) -> str | None:
    if force_adverse:
        return rng.choice(ADVERSE_NOTES)
    return rng.choice(ROUTINE_NOTES)


def build_diary_series(
    *,
    trajectory: TrajectoryId,
    start_date: date,
    baseline_pain: int,
    rng: random.Random,
    adverse_rate: float = 0.05,
) -> list[DiaryPoint]:
    """
    Build a deterministic-ish diary series for a trajectory cohort.

    Thresholds aligned with plateau_service / analytics_service:
    - improving: clear downward pain slope
    - worsening: second-half pain mean >= first-half + 2
    - high_pain_plateau: second-half mean >= 6 and |delta| < 1
    - short_series: < 7 points (insufficient_data)
    """
    if trajectory == "short_series":
        n_days = 4
        points: list[DiaryPoint] = []
        for i in range(n_days):
            d = start_date + timedelta(days=i * 2)
            pain = _clamp(baseline_pain + rng.uniform(-0.5, 0.5))
            points.append(
                DiaryPoint(
                    entry_date=d,
                    pain=pain,
                    sleep=_clamp(5 + rng.uniform(-1, 1)),
                    mood=_clamp(5 + rng.uniform(-1, 1)),
                    function=_clamp(5 + rng.uniform(-1, 1)),
                    notes_es=_pick_note(rng, force_adverse=False),
                )
            )
        return points

    n_days = 56  # 8 weeks of near-daily check-ins
    points = []
    for i in range(n_days):
        # Skip ~15% of days for realism (still keep enough points)
        if i > 0 and rng.random() < 0.15:
            continue
        d = start_date + timedelta(days=i)
        t = i / max(n_days - 1, 1)

        if trajectory == "improving":
            pain = _clamp(baseline_pain - 3.5 * t + rng.uniform(-0.3, 0.3))
            function = _clamp(4 + 3.5 * t + rng.uniform(-0.3, 0.3))
            sleep = _clamp(4 + 2.5 * t + rng.uniform(-0.4, 0.4))
            mood = _clamp(4 + 2.0 * t + rng.uniform(-0.4, 0.4))
        elif trajectory == "worsening":
            # First half milder, second half clearly worse (+>=2 mean pain)
            pain = _clamp(baseline_pain - 1.0 + 4.0 * t + rng.uniform(-0.2, 0.2))
            function = _clamp(6 - 3.5 * t + rng.uniform(-0.2, 0.2))
            sleep = _clamp(6 - 2.0 * t + rng.uniform(-0.3, 0.3))
            mood = _clamp(6 - 2.0 * t + rng.uniform(-0.3, 0.3))
        else:  # high_pain_plateau
            base = max(baseline_pain, 7)
            pain = _clamp(base + rng.uniform(-0.35, 0.35))
            function = _clamp(4 + rng.uniform(-0.4, 0.4))
            sleep = _clamp(4 + rng.uniform(-0.4, 0.4))
            mood = _clamp(4 + rng.uniform(-0.4, 0.4))

        force_adverse = rng.random() < adverse_rate
        points.append(
            DiaryPoint(
                entry_date=d,
                pain=pain,
                sleep=sleep,
                mood=mood,
                function=function,
                notes_es=_pick_note(rng, force_adverse=force_adverse),
            )
        )

    # Guarantee minimum density for analytics (≥7 and both halves ≥3)
    if len(points) < 14:
        extra_start = start_date
        while len(points) < 14:
            d = extra_start + timedelta(days=len(points))
            points.append(
                DiaryPoint(
                    entry_date=d,
                    pain=_clamp(baseline_pain),
                    sleep=5,
                    mood=5,
                    function=5,
                    notes_es=None,
                )
            )
        points.sort(key=lambda p: p.entry_date)

    return points
