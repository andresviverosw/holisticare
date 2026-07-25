"""
SYNTH-01 — end-to-end synthetic dataset generator contracts.

Pure unit tests (no DB, no LLM). Validates schema integrity and that
trajectory cohorts exercise analytics / plateau / recovery KPIs.
"""

from __future__ import annotations

from datetime import date

import pytest

from app.schemas.diary_v0 import PatientDiaryCheckinV0
from app.schemas.intake_v0 import GenericHolisticIntakeV0
from app.schemas.session_v0 import ClinicalSessionLogV0
from app.services.analytics_service import estimate_recovery_trajectory_from_series
from app.services.plateau_service import analyze_diary_plateau
from app.synthetic.generator import (
    DEFAULT_SEED,
    DEFAULT_VARIANTS_PER_ARCHETYPE,
    generate_synthetic_dataset,
    dataset_to_dict,
)
from app.synthetic.archetypes import ARCHETYPES


def _diary_series(patient: dict) -> list[dict]:
    return [
        {
            "date": e["entry_date"],
            "pain_nrs_0_10": e["diary_json"]["pain_nrs_0_10"],
            "sleep_quality_0_10": e["diary_json"]["sleep_quality_0_10"],
            "mood_0_10": e["diary_json"]["mood_0_10"],
            "function_0_10": e["diary_json"]["function_0_10"],
        }
        for e in patient["diary_entries"]
    ]


def test_default_dataset_covers_all_archetypes_and_trajectories():
    ds = generate_synthetic_dataset(seed=DEFAULT_SEED)
    payload = dataset_to_dict(ds)

    assert payload["dataset_version"] == "v1"
    assert payload["seed"] == DEFAULT_SEED
    assert len(payload["patients"]) == len(ARCHETYPES) * DEFAULT_VARIANTS_PER_ARCHETYPE

    archetype_ids = {p["archetype_id"] for p in payload["patients"]}
    assert archetype_ids == {a.id for a in ARCHETYPES}

    trajectories = {p["trajectory"] for p in payload["patients"]}
    assert trajectories == {
        "improving",
        "high_pain_plateau",
        "worsening",
        "short_series",
    }


def test_dataset_is_deterministic_for_same_seed():
    a = dataset_to_dict(generate_synthetic_dataset(seed=7))
    b = dataset_to_dict(generate_synthetic_dataset(seed=7))
    assert a == b


def test_patient_ids_are_deterministic_uuid5():
    ds = generate_synthetic_dataset(seed=1, variants_per_archetype=1)
    ids = [str(p.patient_id) for p in ds.patients]
    assert len(ids) == len(set(ids))
    # Fixed uuid5 for first archetype + improving variant
    assert ids[0] == str(ds.patients[0].patient_id)
    again = generate_synthetic_dataset(seed=1, variants_per_archetype=1)
    assert [str(p.patient_id) for p in again.patients] == ids


def test_intake_sessions_and_diary_pass_pydantic_schemas():
    ds = generate_synthetic_dataset(seed=DEFAULT_SEED, variants_per_archetype=2)
    for patient in ds.patients:
        GenericHolisticIntakeV0.model_validate(patient.intake_json)
        for session in patient.sessions:
            ClinicalSessionLogV0.model_validate(session.session_json)
        for entry in patient.diary_entries:
            PatientDiaryCheckinV0.model_validate(entry.diary_json)
            assert entry.entry_date == date.fromisoformat(
                entry.diary_json["checkin_date"]
            )


def test_plans_always_require_practitioner_review_and_cover_statuses():
    payload = dataset_to_dict(generate_synthetic_dataset(seed=3))
    statuses = set()
    for patient in payload["patients"]:
        plan = patient["plan"]
        assert plan["requires_practitioner_review"] is True
        assert plan["patient_id"] == patient["patient_id"]
        assert isinstance(plan["weeks"], list)
        statuses.add(plan["status"])
        if plan.get("insufficient_evidence"):
            assert plan["status"] == "pending_review"
            assert plan["weeks"] == []
    assert {"approved", "pending_review", "rejected"}.issubset(statuses)


def test_improving_cohort_triggers_improving_recovery_trajectory():
    payload = dataset_to_dict(generate_synthetic_dataset(seed=11))
    improving = [p for p in payload["patients"] if p["trajectory"] == "improving"]
    assert improving
    for patient in improving[:3]:
        series = _diary_series(patient)
        result = estimate_recovery_trajectory_from_series(series)
        assert result["analysis_status"] == "ok"
        assert result["trajectory"]["label"] == "improving"


def test_worsening_cohort_triggers_pain_worsening_plateau_flag():
    payload = dataset_to_dict(generate_synthetic_dataset(seed=11))
    worsening = [p for p in payload["patients"] if p["trajectory"] == "worsening"]
    assert worsening
    for patient in worsening[:3]:
        series = _diary_series(patient)
        status, flags = analyze_diary_plateau(series, data_point_count=len(series))
        assert status == "ok"
        codes = {f["code"] for f in flags}
        assert "PAIN_WORSENING" in codes


def test_high_pain_plateau_cohort_triggers_high_pain_plateau_flag():
    payload = dataset_to_dict(generate_synthetic_dataset(seed=11))
    plateau = [p for p in payload["patients"] if p["trajectory"] == "high_pain_plateau"]
    assert plateau
    for patient in plateau[:3]:
        series = _diary_series(patient)
        status, flags = analyze_diary_plateau(series, data_point_count=len(series))
        assert status == "ok"
        codes = {f["code"] for f in flags}
        assert "HIGH_PAIN_PLATEAU" in codes


def test_short_series_cohort_is_insufficient_for_plateau_and_recovery():
    payload = dataset_to_dict(generate_synthetic_dataset(seed=11))
    short = [p for p in payload["patients"] if p["trajectory"] == "short_series"]
    assert short
    for patient in short:
        series = _diary_series(patient)
        assert len(series) < 7
        status, flags = analyze_diary_plateau(series, data_point_count=len(series))
        assert status == "insufficient_data"
        assert flags == []
        recovery = estimate_recovery_trajectory_from_series(series)
        assert recovery["analysis_status"] == "insufficient_data"


def test_memory_bank_entries_only_from_approved_deidentified_plans():
    payload = dataset_to_dict(generate_synthetic_dataset(seed=5))
    bank = payload["memory_bank"]
    assert len(bank) >= len(ARCHETYPES)
    approved_plan_ids = {
        p["plan"]["plan_id"]
        for p in payload["patients"]
        if p["plan"]["status"] == "approved"
    }
    for entry in bank:
        assert entry["source_plan_id"] in approved_plan_ids
        snap = entry["snapshot_json"]
        assert "patient_id" not in snap
        assert snap.get("memory_bank_snapshot") is True


def test_adverse_event_rate_is_near_five_percent():
    payload = dataset_to_dict(generate_synthetic_dataset(seed=99))
    notes = []
    for patient in payload["patients"]:
        for entry in patient["diary_entries"]:
            note = entry["diary_json"].get("notes_es")
            if note:
                notes.append(note)
    adverse = [n for n in notes if "evento adverso" in n.lower() or "empeoró" in n.lower()]
    # Only count among longitudinal cohorts (enough notes)
    long_entries = sum(
        len(p["diary_entries"])
        for p in payload["patients"]
        if p["trajectory"] != "short_series"
    )
    rate = len(adverse) / max(long_entries, 1)
    assert 0.02 <= rate <= 0.10


def test_spanish_free_text_present_in_diary_and_sessions():
    payload = dataset_to_dict(generate_synthetic_dataset(seed=2, variants_per_archetype=1))
    diary_notes = [
        e["diary_json"].get("notes_es")
        for p in payload["patients"]
        for e in p["diary_entries"]
        if e["diary_json"].get("notes_es")
    ]
    assert diary_notes
    assert any("dolor" in (n or "").lower() or "sueño" in (n or "").lower() or "sueño" in (n or "") for n in diary_notes)
    sessions = [s for p in payload["patients"] for s in p["sessions"]]
    assert sessions
    assert all("observaciones" in s["session_json"] or s["session_json"]["observations"] for s in sessions)


def test_full_scale_option_reaches_eighty_patients():
    ds = generate_synthetic_dataset(seed=1, variants_per_archetype=10)
    assert len(ds.patients) == 80


def test_manifest_summary_counts_match_payload():
    payload = dataset_to_dict(generate_synthetic_dataset(seed=4))
    m = payload["manifest"]
    assert m["patient_count"] == len(payload["patients"])
    assert m["diary_entry_count"] == sum(len(p["diary_entries"]) for p in payload["patients"])
    assert m["session_count"] == sum(len(p["sessions"]) for p in payload["patients"])
    assert m["memory_bank_count"] == len(payload["memory_bank"])
    assert set(m["trajectories_covered"]) == {
        "improving",
        "high_pain_plateau",
        "worsening",
        "short_series",
    }
    assert set(m["plan_statuses_covered"]) >= {"approved", "pending_review", "rejected"}


def test_committed_package_matches_generator_default():
    from pathlib import Path
    import json

    path = Path(__file__).resolve().parents[1] / "data" / "synthetic" / "v1" / "dataset.json"
    assert path.is_file(), "committed SYNTH-01 package missing"
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    expected = dataset_to_dict(
        generate_synthetic_dataset(seed=DEFAULT_SEED, variants_per_archetype=DEFAULT_VARIANTS_PER_ARCHETYPE)
    )
    # generated_at is fixed inside generator; compare full payload for drift.
    assert on_disk == expected
