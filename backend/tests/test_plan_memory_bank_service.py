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
