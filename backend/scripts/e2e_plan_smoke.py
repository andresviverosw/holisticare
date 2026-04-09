#!/usr/bin/env python3
"""
End-to-end smoke: same HTTP contract as the Dashboard (POST /rag/plan/generate).

Run inside the backend container (API must be up on port 8000):

  docker compose exec backend env PYTHONPATH=/app python scripts/e2e_plan_smoke.py

Uses a clinician JWT (local secret) — no dev-login route required.
"""
from __future__ import annotations

import sys

import httpx
from jose import jwt

from app.core.config import get_settings

# Matches frontend Dashboard default (valid UUID v4)
DEFAULT_PATIENT_ID = "a1111111-1111-4111-8111-111111111111"


def _clinician_token() -> str:
    s = get_settings()
    return jwt.encode(
        {"sub": "e2e-plan-smoke", "role": "clinician"},
        s.secret_key,
        algorithm="HS256",
    )


def _payload() -> dict:
    return {
        "patient_id": DEFAULT_PATIENT_ID,
        "intake_json": {
            "profile_version": "generic_holistic_v0",
            "demographics": {"age_range": "40-50", "sex_at_birth": "F"},
            "chief_complaint": "Dolor lumbar crónico con irradiación a pierna izquierda.",
            "conditions": ["lumbalgia crónica"],
            "goals": ["Reducir dolor", "Mejorar movilidad"],
            "contraindications": [],
            "current_medications": ["ibuprofeno 400 mg"],
            "allergies": [],
            "baseline_outcomes": {"pain_nrs_0_10": 7, "notes": "FUNC afectada para cargas"},
            "psychosocial_summary": None,
            "prior_interventions_tried": ["fisioterapia convencional"],
        },
        "available_therapies": ["fisioterapia", "acupuntura", "hidroterapia"],
        "preferred_language": "es",
    }


def main() -> int:
    base = "http://127.0.0.1:8000"
    token = _clinician_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    with httpx.Client(timeout=300.0) as client:
        r_chunks = client.get(f"{base}/rag/chunks", params={"limit": 3})
        print("GET /rag/chunks", r_chunks.status_code, "items:", len(r_chunks.json().get("items", [])))

        r = client.post(f"{base}/rag/plan/generate", headers=headers, json=_payload())

    print("POST /rag/plan/generate", r.status_code)
    if r.status_code != 200:
        print(r.text[:2000], file=sys.stderr)
        return 1

    data = r.json()
    meta = data.get("retrieval_metadata") or {}
    print("plan_id:", data.get("plan_id"))
    print("status:", data.get("status"))
    print("insufficient_evidence:", data.get("insufficient_evidence"))
    print("citations_used:", len(data.get("citations_used") or []), data.get("citations_used"))
    print(
        "retrieval: candidates_retrieved=%s chunks_passed_to_llm=%s"
        % (meta.get("candidates_retrieved"), meta.get("chunks_passed_to_llm"))
    )
    weeks = data.get("weeks") or []
    print("weeks in plan:", len(weeks))

    if data.get("insufficient_evidence"):
        print(
            "\nWARNING: RAG returned insufficient_evidence; corpus may be empty or retrieval mismatch.",
            file=sys.stderr,
        )
        return 2

    if not weeks:
        print("\nWARNING: plan has no weeks.", file=sys.stderr)
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
