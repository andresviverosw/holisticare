"""US-PRIV-001 — project + redact intake before external LLM egress."""

from __future__ import annotations

import copy
import re
from typing import Any

PATIENT_TOKEN = "PATIENT_TOKEN"  # nosec B105 — LLM prompt placeholder, not a credential

# Clinical fields allowed in LLM prompts (generic_holistic_v0 projection).
_ALLOWED_TOP_LEVEL = frozenset(
    {
        "profile_version",
        "demographics",
        "chief_complaint",
        "conditions",
        "goals",
        "contraindications",
        "current_medications",
        "allergies",
        "baseline_outcomes",
        "psychosocial_summary",
        "prior_interventions_tried",
    }
)

_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
# MX/US-ish phones with optional +country and separators
_PHONE_RE = re.compile(
    r"(?<!\w)(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,3}\)?[\s-]?)?\d{3}[\s-]?\d{2,4}[\s-]?\d{2,4}(?!\w)"
)
_UUID_RE = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)


def redact_free_text(value: str) -> str:
    text = value
    text = _EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = _UUID_RE.sub("[REDACTED_UUID]", text)
    text = _PHONE_RE.sub("[REDACTED_PHONE]", text)
    return text


def _scrub_value(value: Any) -> Any:
    if isinstance(value, str):
        return redact_free_text(value)
    if isinstance(value, list):
        return [_scrub_value(v) for v in value]
    if isinstance(value, dict):
        return {k: _scrub_value(v) for k, v in value.items()}
    return value


def anonymize_intake_for_llm(intake_json: dict[str, Any] | None) -> dict[str, Any]:
    """
    Return a clinical-only, PII-scrubbed copy of intake for LLM prompts.

    Local DB / API layers keep the real patient_id; this projection must never
    include it or contact-like free-text matches.
    """
    if not isinstance(intake_json, dict):
        return {}
    projected: dict[str, Any] = {}
    for key in _ALLOWED_TOP_LEVEL:
        if key in intake_json:
            projected[key] = copy.deepcopy(intake_json[key])
    return _scrub_value(projected)
