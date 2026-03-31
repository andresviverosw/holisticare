"""
Generic holistic rehab intake — profile_version generic_holistic_v0.

Normative shape: docs/sprint-01.md
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class DemographicsV0(BaseModel):
    age_range: str | None = None
    sex_at_birth: str | None = None


class BaselineOutcomesV0(BaseModel):
    pain_nrs_0_10: int | None = Field(default=None, ge=0, le=10)
    notes: str | None = None


class GenericHolisticIntakeV0(BaseModel):
    profile_version: Literal["generic_holistic_v0"]
    demographics: DemographicsV0 = Field(default_factory=DemographicsV0)
    chief_complaint: str = Field(..., min_length=1, description="Motivo principal de consulta")
    conditions: list[str] = Field(..., min_length=1)
    goals: list[str] = Field(..., min_length=1)
    contraindications: list[str] = Field(default_factory=list)
    current_medications: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    baseline_outcomes: BaselineOutcomesV0 | None = None
    psychosocial_summary: str | None = None
    prior_interventions_tried: list[str] = Field(default_factory=list)

    @field_validator("chief_complaint", mode="before")
    @classmethod
    def strip_chief(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("conditions", "goals", mode="after")
    @classmethod
    def nonempty_trimmed_strings(cls, v: list[str]) -> list[str]:
        out = [s.strip() for s in v if isinstance(s, str) and s.strip()]
        if not out:
            raise ValueError("Debe incluir al menos un elemento no vacío.")
        return out
