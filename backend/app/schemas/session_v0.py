"""
Structured clinical session log — profile_version clinical_session_v0.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SessionInterventionV0(BaseModel):
    therapy_type: str = Field(..., min_length=1, description="Modalidad o tipo de intervención")
    description: str = Field(..., min_length=1, description="Qué se realizó en la sesión")
    duration_minutes: int | None = Field(default=None, ge=1, le=600)

    @field_validator("therapy_type", "description", mode="before")
    @classmethod
    def strip_strings(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v


class ClinicalSessionLogV0(BaseModel):
    profile_version: Literal["clinical_session_v0"]
    session_at: datetime
    interventions: list[SessionInterventionV0] = Field(..., min_length=1)
    observations: str = Field(..., min_length=1)
    patient_reported_response: str | None = None

    @field_validator("observations", mode="before")
    @classmethod
    def strip_observations(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("observations", mode="after")
    @classmethod
    def observations_non_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("Las observaciones no pueden quedar vacías.")
        return v

    @field_validator("patient_reported_response", mode="before")
    @classmethod
    def strip_patient_response(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if isinstance(v, str):
            s = v.strip()
            return s if s else None
        return v


class SessionNoteAssistV0(BaseModel):
    profile_version: Literal["clinical_session_note_assist_v0"]
    interventions: list[SessionInterventionV0] = Field(..., min_length=1)
    observations_draft: str | None = None
    patient_reported_response: str | None = None

    @field_validator("observations_draft", "patient_reported_response", mode="before")
    @classmethod
    def strip_optional_strings(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if isinstance(v, str):
            s = v.strip()
            return s if s else None
        return v
