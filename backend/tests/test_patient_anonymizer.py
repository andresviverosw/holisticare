"""US-PRIV-001 — patient anonymization before external LLM egress."""

import json
import re
import uuid

import pytest

from app.services.patient_anonymizer import (
    PATIENT_TOKEN,
    AnonymizationError,
    anonymize_intake_for_llm,
    assert_egress_safe,
    prepare_intake_for_llm,
)


PATIENT_UUID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"


def _dirty_intake() -> dict:
    return {
        "patient_id": PATIENT_UUID,
        "email": "paciente@ejemplo.com",
        "profile_version": "generic_holistic_v0",
        "chief_complaint": (
            f"Dolor lumbar. Contacto: paciente@ejemplo.com / +52 55 1234 5678. "
            f"ID interno {PATIENT_UUID}."
        ),
        "conditions": ["lumbalgia"],
        "goals": ["Reducir dolor"],
        "contraindications": ["anticoagulantes"],
        "allergies": ["mariscos"],
        "psychosocial_summary": "Vive con Ana. Tel 555-987-6543. Correo ana.garcia@mail.mx",
        "extra_pii_field": "should-be-dropped",
    }


def test_anonymize_drops_patient_id_and_unknown_keys():
    safe = anonymize_intake_for_llm(_dirty_intake())
    assert "patient_id" not in safe
    assert "email" not in safe
    assert "extra_pii_field" not in safe
    assert safe["profile_version"] == "generic_holistic_v0"
    assert safe["conditions"] == ["lumbalgia"]
    assert "anticoagulantes" in safe["contraindications"]


def test_anonymize_redacts_email_phone_and_uuid_in_free_text():
    safe = anonymize_intake_for_llm(_dirty_intake())
    blob = json.dumps(safe, ensure_ascii=False)
    assert PATIENT_UUID not in blob
    assert "paciente@ejemplo.com" not in blob
    assert "ana.garcia@mail.mx" not in blob
    assert "+52 55 1234 5678" not in blob
    assert "555-987-6543" not in blob
    assert "[REDACTED]" in blob or "[ID]" in blob


def test_assert_egress_safe_rejects_residual_pii():
    with pytest.raises(AnonymizationError):
        assert_egress_safe(f"Contact {PATIENT_UUID} at paciente@ejemplo.com")


def test_prepare_intake_for_llm_is_egress_safe():
    safe = prepare_intake_for_llm(_dirty_intake())
    assert_egress_safe(json.dumps(safe, ensure_ascii=False))
    assert PATIENT_TOKEN  # constant exported for generator prompts


def test_patient_token_is_stable_placeholder():
    assert PATIENT_TOKEN == "PATIENT_TOKEN"
    assert not re.fullmatch(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
        PATIENT_TOKEN,
    )


def test_prepare_raises_when_post_scrub_validation_fails(monkeypatch):
    from app.services import patient_anonymizer as mod

    monkeypatch.setattr(mod, "anonymize_intake_for_llm", lambda _intake: {"chief_complaint": "x@y.com"})
    with pytest.raises(AnonymizationError):
        prepare_intake_for_llm({"chief_complaint": "irrelevant"})
