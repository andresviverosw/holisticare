"""Unit tests for mapping generated plan dicts to treatment_plans rows (no DB)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.treatment_plan import TreatmentPlan
from app.services.plan_persistence import (
    build_treatment_plan_row,
    persist_generated_plan,
)


PATIENT_ID = uuid.uuid4()
PRACTITIONER_ID = uuid.uuid4()
PLAN_ID = uuid.uuid4()


def _sample_plan(extra: dict | None = None) -> dict:
    base = {
        "plan_id": str(PLAN_ID),
        "patient_id": str(PATIENT_ID),
        "generated_at": "2026-01-01T00:00:00+00:00",
        "status": "pending_review",
        "citations_used": ["REF-A", "REF-B"],
        "weeks": [],
        "confidence_note": "ok",
    }
    if extra:
        base.update(extra)
    return base


def test_build_treatment_plan_row_uses_plan_id_as_primary_key():
    row = build_treatment_plan_row(
        _sample_plan(),
        patient_id=PATIENT_ID,
        practitioner_id=PRACTITIONER_ID,
    )
    assert isinstance(row, TreatmentPlan)
    assert row.id == PLAN_ID
    assert row.patient_id == PATIENT_ID
    assert row.practitioner_id == PRACTITIONER_ID
    assert row.status == "pending_review"
    assert row.citations_used == ["REF-A", "REF-B"]
    assert row.plan_json["plan_id"] == str(PLAN_ID)


def test_build_treatment_plan_row_practitioner_optional():
    row = build_treatment_plan_row(
        _sample_plan(),
        patient_id=PATIENT_ID,
        practitioner_id=None,
    )
    assert row.practitioner_id is None


def test_build_treatment_plan_row_insufficient_evidence_flag_in_json():
    row = build_treatment_plan_row(
        _sample_plan({"insufficient_evidence": True, "citations_used": []}),
        patient_id=PATIENT_ID,
        practitioner_id=None,
    )
    assert row.plan_json["insufficient_evidence"] is True
    assert row.citations_used == []


@pytest.mark.asyncio
async def test_persist_generated_plan_adds_and_commits():
    session = AsyncMock()
    session.add = MagicMock()
    plan = _sample_plan()
    plan_id = await persist_generated_plan(
        session,
        patient_id=PATIENT_ID,
        practitioner_id=PRACTITIONER_ID,
        plan=plan,
    )
    assert plan_id == PLAN_ID
    session.add.assert_called_once()
    added = session.add.call_args[0][0]
    assert isinstance(added, TreatmentPlan)
    assert added.id == PLAN_ID
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once()
