"""
Daily patient diary check-in — profile_version patient_diary_v0.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PatientDiaryCheckinV0(BaseModel):
    profile_version: Literal["patient_diary_v0"]
    checkin_date: date
    pain_nrs_0_10: int = Field(..., ge=0, le=10, description="Dolor 0–10")
    sleep_quality_0_10: int = Field(..., ge=0, le=10, description="Calidad de sueño 0–10")
    mood_0_10: int = Field(..., ge=0, le=10, description="Ánimo 0–10")
    function_0_10: int = Field(..., ge=0, le=10, description="Funcionalidad 0–10")
    notes_es: str | None = Field(
        default=None,
        max_length=1500,
        description="Notas opcionales del paciente en español.",
    )

    @field_validator("notes_es", mode="before")
    @classmethod
    def strip_notes(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if isinstance(v, str):
            s = v.strip()
            return s if s else None
        return v
