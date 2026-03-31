from __future__ import annotations

from typing import Any


def analyze_intake_risk_flags(intake_json: dict[str, Any]) -> list[dict[str, str]]:
    flags: list[dict[str, str]] = []

    contraindications = intake_json.get("contraindications") or []
    if isinstance(contraindications, list) and contraindications:
        flags.append(
            {
                "code": "CONTRAINDICATION_DECLARED",
                "severity": "high",
                "message": "Se detectaron contraindicaciones declaradas en la historia clínica.",
            }
        )

    chief = str(intake_json.get("chief_complaint") or "").lower()
    if any(token in chief for token in ["intenso", "severo", "agudo"]):
        flags.append(
            {
                "code": "HIGH_SYMPTOM_INTENSITY",
                "severity": "medium",
                "message": "El motivo de consulta sugiere intensidad alta de síntomas.",
            }
        )

    return flags
