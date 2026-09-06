"""
Shared plan snapshot helpers (US-PLAN-004 / SYNTH-01).

Pure functions — safe to import without initializing the DB engine.
"""

from __future__ import annotations

import copy
from typing import Any

from app.services.patient_anonymizer import scrub_nested_free_text


def extract_therapy_types(plan: dict[str, Any]) -> list[str]:
    out: set[str] = set()
    for week in plan.get("weeks") or []:
        if not isinstance(week, dict):
            continue
        for t in week.get("therapies") or []:
            if isinstance(t, dict):
                typ = t.get("type")
                if isinstance(typ, str) and typ.strip():
                    out.add(typ.strip().lower())
    return sorted(out)


def sanitize_plan_for_memory_bank(plan: dict[str, Any]) -> dict[str, Any]:
    """De-identify plan JSON for storage as a reusable template snapshot.

    US-PLAN-004: drop patient_id and operational metadata.
    US-PRIV-002: scrub email/phone/UUID patterns from remaining free text.
    """
    snap = copy.deepcopy(plan)
    snap.pop("patient_id", None)
    snap.pop("retrieval_metadata", None)
    snap.pop("practitioner_notes", None)
    snap.pop("nutrition_safety_flags", None)
    snap = scrub_nested_free_text(snap)
    snap["memory_bank_snapshot"] = True
    return snap
