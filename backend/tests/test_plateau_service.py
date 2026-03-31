"""Unit tests for plateau / worsening detection (US-ANLY-002)."""

from __future__ import annotations

from app.services.plateau_service import analyze_diary_plateau


def _series_pain_only(vals: list[int | None]) -> list[dict]:
    out = []
    for i, v in enumerate(vals):
        row: dict = {"date": f"2026-04-{i+1:02d}"}
        if v is not None:
            row["pain_nrs_0_10"] = v
            row["sleep_quality_0_10"] = 5
            row["mood_0_10"] = 5
            row["function_0_10"] = 5
        out.append(row)
    return out


def test_insufficient_when_fewer_than_seven_days():
    status, flags = analyze_diary_plateau(_series_pain_only([3, 4, 5, 6, 6]), data_point_count=5)
    assert status == "insufficient_data"
    assert flags == []


def test_pain_worsening_split_halves():
    # 8 days: first half pain ~3, second half ~7 -> +4
    pains = [3, 3, 3, 3, 7, 7, 7, 7]
    s = []
    for i, p in enumerate(pains):
        s.append(
            {
                "date": f"2026-04-{i+1:02d}",
                "pain_nrs_0_10": p,
                "function_0_10": 6,
            }
        )
    status, flags = analyze_diary_plateau(s, data_point_count=8)
    assert status == "ok"
    codes = {f["code"] for f in flags}
    assert "PAIN_WORSENING" in codes


def test_function_worsening():
    # 8 days: function drops from ~8 to ~4
    s = []
    for i in range(8):
        fn = 8 if i < 4 else 4
        s.append(
            {
                "date": f"2026-04-{i+1:02d}",
                "pain_nrs_0_10": 4,
                "function_0_10": fn,
            }
        )
    status, flags = analyze_diary_plateau(s, data_point_count=8)
    assert status == "ok"
    assert any(f["code"] == "FUNCTION_WORSENING" for f in flags)


def test_high_pain_plateau():
    # Segunda mitad media 6.5 (≥6), diferencia con primera 7 es 0.5 (<1)
    pains = [7, 7, 7, 7, 6, 7, 6, 7]
    s = []
    for i, p in enumerate(pains):
        s.append(
            {
                "date": f"2026-04-{i+1:02d}",
                "pain_nrs_0_10": p,
                "function_0_10": 6,
            }
        )
    status, flags = analyze_diary_plateau(s, data_point_count=8)
    assert status == "ok"
    assert any(f["code"] == "HIGH_PAIN_PLATEAU" for f in flags)


def test_stable_no_flags():
    s = []
    for i in range(8):
        s.append(
            {
                "date": f"2026-04-{i+1:02d}",
                "pain_nrs_0_10": 3,
                "function_0_10": 7,
            }
        )
    status, flags = analyze_diary_plateau(s, data_point_count=8)
    assert status == "ok"
    assert flags == []
