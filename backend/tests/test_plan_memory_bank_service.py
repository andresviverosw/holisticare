"""Unit tests for US-PLAN-004 plan memory bank helpers (no DB)."""

import uuid
from datetime import datetime

from app.services.plan_memory_bank_service import (
    build_draft_from_template,
    extract_therapy_types,
    sanitize_plan_for_memory_bank,
)


def test_extract_therapy_types_collects_week_therapies():
    plan = {
        "weeks": [
            {
                "week": 1,
                "therapies": [
                    {"type": "Fisioterapia", "rationale": "x"},
                    {"type": "fisioterapia", "rationale": "dup"},
                ],
            },
            {"week": 2, "therapies": [{"type": "Acupuntura", "rationale": "y"}]},
        ]
    }
    assert extract_therapy_types(plan) == ["acupuntura", "fisioterapia"]


def test_sanitize_strips_identifiers_and_flags():
    src = {
        "plan_id": "old",
        "patient_id": str(uuid.uuid4()),
        "retrieval_metadata": {"q": 1},
        "practitioner_notes": "secret",
        "nutrition_safety_flags": [{"x": 1}],
        "weeks": [],
    }
    out = sanitize_plan_for_memory_bank(src)
    assert "patient_id" not in out
    assert "retrieval_metadata" not in out
    assert "practitioner_notes" not in out
    assert "nutrition_safety_flags" not in out
    assert out.get("memory_bank_snapshot") is True


def test_sanitize_scrubs_free_text_identifiers_us_priv_002():
    """US-PRIV-002 — narrative fields must not keep email/phone/UUID in bank snapshots."""
    patient_uuid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    src = {
        "plan_id": "plan-1",
        "patient_id": patient_uuid,
        "confidence_note": (
            "Contactar a ana@clinic.mx o +52 55 1234 5678; "
            f"expediente {patient_uuid}."
        ),
        "weeks": [
            {
                "week": 1,
                "goals": [f"Seguimiento con ID {patient_uuid}"],
                "therapies": [
                    {
                        "type": "Fisioterapia",
                        "rationale": "Avisar a physio@example.com antes de la sesión.",
                    }
                ],
            }
        ],
        "diet_recommendations": {
            "include": [
                {
                    "item": "Agua",
                    "rationale": "No compartir datos; email viejo: old@paciente.org",
                }
            ]
        },
    }
    out = sanitize_plan_for_memory_bank(src)
    blob = str(out)
    assert "patient_id" not in out
    assert "ana@clinic.mx" not in blob
    assert "physio@example.com" not in blob
    assert "old@paciente.org" not in blob
    assert patient_uuid not in blob
    assert "5512345678" not in blob.replace(" ", "").replace("-", "")
    assert out.get("memory_bank_snapshot") is True
    assert "[REDACTED]" in blob or "[ID]" in blob
    # Clinical therapy type preserved
    assert out["weeks"][0]["therapies"][0]["type"] == "Fisioterapia"


def test_build_draft_resets_status_and_clears_safety_flags():
    tid = uuid.uuid4()
    pid = uuid.uuid4()
    nid = uuid.uuid4()
    snap = {
        "plan_id": "old",
        "patient_id": "old-p",
        "status": "approved",
        "weeks": [],
        "confidence_note": "Nota",
    }
    draft = build_draft_from_template(
        snap,
        new_plan_id=nid,
        new_patient_id=pid,
        memory_bank_entry_id=tid,
    )
    assert draft["plan_id"] == str(nid)
    assert draft["patient_id"] == str(pid)
    assert draft["status"] == "pending_review"
    assert draft["requires_practitioner_review"] is True
    assert draft["insufficient_evidence"] is False
    assert draft["nutrition_safety_flags"] == []
    assert draft["derived_from_memory_bank"]["template_id"] == str(tid)
    datetime.fromisoformat(draft["generated_at"].replace("Z", "+00:00"))
    assert "biblioteca" in draft["confidence_note"].lower()
