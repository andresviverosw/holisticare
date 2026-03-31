"""Unit tests for generic holistic intake v0 (Sprint 1)."""

import pytest
from pydantic import ValidationError

from app.schemas.intake_v0 import GenericHolisticIntakeV0


def _valid_payload():
    return {
        "profile_version": "generic_holistic_v0",
        "demographics": {"age_range": "40-49", "sex_at_birth": "femenino"},
        "chief_complaint": "Dolor lumbar.",
        "conditions": ["lumbalgia"],
        "goals": ["Reducir dolor"],
        "contraindications": [],
        "baseline_outcomes": {"pain_nrs_0_10": 6, "notes": "Mañanas peor"},
    }


def test_valid_intake_parses():
    m = GenericHolisticIntakeV0.model_validate(_valid_payload())
    assert m.profile_version == "generic_holistic_v0"
    assert m.chief_complaint == "Dolor lumbar."


def test_missing_conditions_rejected():
    p = _valid_payload()
    del p["conditions"]
    with pytest.raises(ValidationError):
        GenericHolisticIntakeV0.model_validate(p)


def test_empty_conditions_rejected():
    p = _valid_payload()
    p["conditions"] = []
    with pytest.raises(ValidationError):
        GenericHolisticIntakeV0.model_validate(p)


def test_empty_goals_rejected():
    p = _valid_payload()
    p["goals"] = []
    with pytest.raises(ValidationError):
        GenericHolisticIntakeV0.model_validate(p)


def test_wrong_profile_version_rejected():
    p = _valid_payload()
    p["profile_version"] = "nmg_v1"
    with pytest.raises(ValidationError):
        GenericHolisticIntakeV0.model_validate(p)


def test_pain_nrs_bounds():
    p = _valid_payload()
    p["baseline_outcomes"] = {"pain_nrs_0_10": 11}
    with pytest.raises(ValidationError):
        GenericHolisticIntakeV0.model_validate(p)
