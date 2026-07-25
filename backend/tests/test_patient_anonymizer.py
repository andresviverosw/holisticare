"""US-PRIV-001 — anonymize/pseudonymize intake before external LLM calls."""

from __future__ import annotations

import uuid

from app.services.patient_anonymizer import (
    PATIENT_TOKEN,
    anonymize_intake_for_llm,
    redact_free_text,
)


def test_anonymize_strips_patient_id_and_unknown_keys():
    pid = str(uuid.uuid4())
    out = anonymize_intake_for_llm(
        {
            "patient_id": pid,
            "profile_version": "generic_holistic_v0",
            "chief_complaint": "dolor lumbar",
            "conditions": ["lumbalgia"],
            "goals": ["caminar"],
            "email": "secret@example.com",
            "full_name": "Juan Pérez",
        }
    )
    assert "patient_id" not in out
    assert "email" not in out
    assert "full_name" not in out
    assert out["chief_complaint"] == "dolor lumbar"
    assert out["conditions"] == ["lumbalgia"]
    assert pid not in str(out)


def test_redact_free_text_masks_email_phone_and_uuid():
    pid = "550e8400-e29b-41d4-a716-446655440000"
    text = f"Contactar a ana@clinic.mx o +52 55 1234 5678; id={pid}"
    redacted = redact_free_text(text)
    assert "ana@clinic.mx" not in redacted
    assert "+52 55 1234 5678" not in redacted
    assert pid not in redacted
    assert "[REDACTED_EMAIL]" in redacted
    assert "[REDACTED_PHONE]" in redacted
    assert "[REDACTED_UUID]" in redacted


def test_anonymize_redacts_pii_inside_clinical_free_text():
    out = anonymize_intake_for_llm(
        {
            "profile_version": "generic_holistic_v0",
            "chief_complaint": "Dolor; email paciente@test.com",
            "conditions": ["asma"],
            "goals": ["mejorar sueño"],
            "psychosocial_summary": "Llama al 555-123-4567",
            "baseline_outcomes": {"pain_nrs_0_10": 6, "notes": "UUID 550e8400-e29b-41d4-a716-446655440000"},
        }
    )
    blob = str(out)
    assert "paciente@test.com" not in blob
    assert "555-123-4567" not in blob
    assert "550e8400-e29b-41d4-a716-446655440000" not in blob
    assert out["baseline_outcomes"]["pain_nrs_0_10"] == 6


def test_patient_token_constant_for_llm_prompts():
    assert PATIENT_TOKEN == "PATIENT_TOKEN"
