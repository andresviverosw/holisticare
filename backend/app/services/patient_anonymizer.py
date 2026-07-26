"""
US-PRIV-001 — Pseudonymize patient data at the LLM egress boundary.

Local DB rows remain identified by UUID. Only outbound Claude/OpenAI payloads
are scrubbed (LFPDPPP-aligned minimization for international model APIs).
"""

from __future__ import annotations

import copy
import json
import re
from typing import Any

PATIENT_TOKEN = "PATIENT_TOKEN"

# Clinical-only keys from GenericHolisticIntakeV0 (+ nested). Drop everything else.
_CLINICAL_TOP_LEVEL_KEYS = frozenset(
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

_EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
    re.IGNORECASE,
)
_UUID_RE = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)
# MX/US-ish phone: optional +, groups of digits with separators; ≥10 digits total.
_PHONE_RE = re.compile(
    r"(?<!\w)(?:\+?\d{1,3}[\s.\-]?)?(?:\(?\d{2,4}\)?[\s.\-]?)?\d{3,4}[\s.\-]?\d{3,4}(?!\w)"
)


class AnonymizationError(ValueError):
    """Raised when egress payload still contains forbidden identifier patterns."""

    def __init__(self, message: str = "Patient anonymization failed for LLM egress"):
        super().__init__(message)


def _digit_count(s: str) -> int:
    return sum(1 for c in s if c.isdigit())


def redact_free_text(value: str) -> str:
    """Redact email, UUID, and phone-like tokens from a free-text string."""
    text = _EMAIL_RE.sub("[REDACTED]", value)
    text = _UUID_RE.sub("[ID]", text)

    def _phone_sub(match: re.Match[str]) -> str:
        raw = match.group(0)
        if _digit_count(raw) < 10:
            return raw
        return "[REDACTED]"

    return _PHONE_RE.sub(_phone_sub, text)


def _scrub_value(value: Any) -> Any:
    if isinstance(value, str):
        return redact_free_text(value)
    if isinstance(value, list):
        return [_scrub_value(v) for v in value]
    if isinstance(value, dict):
        return {k: _scrub_value(v) for k, v in value.items()}
    return value


def anonymize_intake_for_llm(intake_json: dict[str, Any]) -> dict[str, Any]:
    """
    Project intake to clinical-only fields and redact contact-like free text.

    Never includes patient_id or unknown keys (emails, names, etc.).
    """
    if not isinstance(intake_json, dict):
        raise AnonymizationError("Intake must be an object for anonymization")

    projected: dict[str, Any] = {}
    for key in _CLINICAL_TOP_LEVEL_KEYS:
        if key in intake_json:
            projected[key] = copy.deepcopy(intake_json[key])

    return _scrub_value(projected)


def assert_egress_safe(payload: str | dict[str, Any]) -> None:
    """Fail closed if residual email/phone/UUID patterns remain in egress text."""
    text = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    if _EMAIL_RE.search(text):
        raise AnonymizationError("Residual email pattern in LLM egress payload")
    if _UUID_RE.search(text):
        raise AnonymizationError("Residual UUID pattern in LLM egress payload")
    for match in _PHONE_RE.finditer(text):
        if _digit_count(match.group(0)) >= 10:
            raise AnonymizationError("Residual phone pattern in LLM egress payload")


def prepare_intake_for_llm(intake_json: dict[str, Any]) -> dict[str, Any]:
    """Anonymize then validate — single entry point for RAGPipeline."""
    safe = anonymize_intake_for_llm(intake_json)
    assert_egress_safe(safe)
    return safe
