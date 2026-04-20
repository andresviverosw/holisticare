"""Unit tests for analytics date window (no HTTP)."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.services.analytics_service import (
    MAX_RANGE_DAYS,
    estimate_recovery_trajectory_from_series,
    resolve_analytics_date_window,
)


def test_resolve_window_defaults_to_last_90_days():
    d1 = date(2026, 6, 15)
    d0, d2 = resolve_analytics_date_window(None, d1)
    assert d2 == d1
    assert (d2 - d0).days == 90


def test_resolve_window_rejects_inverted_range():
    with pytest.raises(ValueError, match="fecha inicial"):
        resolve_analytics_date_window(date(2026, 4, 10), date(2026, 4, 1))


def test_resolve_window_rejects_too_long():
    start = date(2020, 1, 1)
    end = start + timedelta(days=MAX_RANGE_DAYS + 1)
    with pytest.raises(ValueError, match="731"):
        resolve_analytics_date_window(start, end)


def test_recovery_trajectory_improving_when_pain_decreases():
    series = [
        {"date": "2026-04-01", "pain_nrs_0_10": 8},
        {"date": "2026-04-03", "pain_nrs_0_10": 7},
        {"date": "2026-04-05", "pain_nrs_0_10": 6},
        {"date": "2026-04-07", "pain_nrs_0_10": 6},
        {"date": "2026-04-10", "pain_nrs_0_10": 5},
    ]
    out = estimate_recovery_trajectory_from_series(series)
    assert out["analysis_status"] == "ok"
    assert out["trajectory"]["label"] == "improving"
    assert out["trajectory"]["projected_pain_nrs_in_4_weeks"] <= out["trajectory"]["latest_pain_nrs"]


def test_recovery_trajectory_insufficient_data_with_few_points():
    series = [
        {"date": "2026-04-01", "pain_nrs_0_10": 6},
        {"date": "2026-04-02", "pain_nrs_0_10": 6},
        {"date": "2026-04-03", "pain_nrs_0_10": 5},
    ]
    out = estimate_recovery_trajectory_from_series(series)
    assert out["analysis_status"] == "insufficient_data"
    assert out["trajectory"] is None
