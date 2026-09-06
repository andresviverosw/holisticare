#!/usr/bin/env python3
"""
DEMO-01 — public Render walkthrough (API).

Path A: intake → POST /rag/plan/generate → approve
Path B (fallback on free-tier 100s timeout): intake → memory-bank instantiate → approve

Usage:
  PYTHONPATH=. python scripts/demo_public_walkthrough.py
  PYTHONPATH=. python scripts/demo_public_walkthrough.py --api-base https://holisticare-api.onrender.com
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from typing import Any

import httpx

DEFAULT_API = "https://holisticare-api.onrender.com"


def _intake() -> dict[str, Any]:
    return {
        "profile_version": "generic_holistic_v0",
        "demographics": {"age_range": "40-49", "sex_at_birth": "femenino"},
        "chief_complaint": "Dolor lumbar mecánico de 6 semanas de evolución.",
        "conditions": ["lumbalgia subaguda"],
        "goals": ["Reducir dolor", "Retomar caminatas diarias"],
        "contraindications": [],
        "current_medications": [],
        "allergies": [],
        "baseline_outcomes": {"pain_nrs_0_10": 6, "notes": "Peor por las mañanas."},
        "psychosocial_summary": "Estrés laboral moderado.",
        "prior_interventions_tried": ["reposo relativo", "calor local"],
    }


def _run(api_base: str, generate_timeout: float, prefer_generate: bool) -> int:
    patient_id = str(uuid.uuid4())
    report: dict[str, Any] = {
        "story": "DEMO-01",
        "api_base": api_base,
        "patient_id": patient_id,
        "steps": [],
        "path": None,
        "plan_id": None,
        "pass": False,
        "notes": [],
    }

    def step(name: str, r: httpx.Response) -> Any:
        try:
            body = r.json()
        except Exception:
            body = (r.text or "")[:2000]
        report["steps"].append(
            {
                "step": name,
                "http": r.status_code,
                "elapsed_s": round(r.elapsed.total_seconds(), 2),
            }
        )
        print(f"{name}: HTTP {r.status_code} ({r.elapsed.total_seconds():.1f}s)")
        return body

    timeout = httpx.Timeout(max(generate_timeout, 60.0), connect=60.0)
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        step("health", client.get(f"{api_base}/health"))
        step("ready", client.get(f"{api_base}/ready"))
        login = client.post(
            f"{api_base}/auth/dev-login",
            json={"role": "clinician", "sub": "demo-01-walkthrough"},
        )
        login_body = step("dev-login", login)
        if login.status_code != 200 or not isinstance(login_body, dict):
            print("FAIL: dev-login", file=sys.stderr)
            return 1
        token = login_body.get("access_token")
        if not isinstance(token, str) or not token.strip():
            print("FAIL: missing access_token", file=sys.stderr)
            return 1
        headers = {"Authorization": f"Bearer {token}"}

        intake = _intake()
        saved = client.post(
            f"{api_base}/rag/intake",
            headers=headers,
            json={"patient_id": patient_id, "intake_json": intake},
        )
        step("save-intake", saved)
        if saved.status_code != 200:
            print("FAIL: intake", saved.text[:500], file=sys.stderr)
            return 1

        plan_id: str | None = None
        if prefer_generate:
            t0 = time.time()
            gen = client.post(
                f"{api_base}/rag/plan/generate",
                headers=headers,
                json={
                    "patient_id": patient_id,
                    "intake_json": intake,
                    "available_therapies": ["fisioterapia", "acupuntura", "hidroterapia"],
                    "preferred_language": "es",
                },
            )
            print(f"generate wall={time.time() - t0:.1f}s")
            gen_body = step("generate-plan", gen)
            if gen.status_code == 200 and isinstance(gen_body, dict) and gen_body.get("plan_id"):
                plan_id = str(gen_body["plan_id"])
                report["path"] = "generate"
            else:
                report["notes"].append(
                    "generate failed or timed out (common on Render free tier ~100s limit); "
                    "falling back to memory-bank instantiate"
                )

        if not plan_id:
            mb = client.get(
                f"{api_base}/rag/plan/memory-bank",
                headers=headers,
                params={"limit": 5},
            )
            mb_body = step("list-memory-bank", mb)
            items = mb_body.get("items") if isinstance(mb_body, dict) else None
            if mb.status_code != 200 or not items:
                print("FAIL: no memory-bank templates for fallback", file=sys.stderr)
                print(json.dumps(report, indent=2))
                return 1
            template_id = items[0].get("id") or items[0].get("template_id")
            inst = client.post(
                f"{api_base}/rag/plan/memory-bank/{template_id}/instantiate",
                headers=headers,
                json={"patient_id": patient_id},
            )
            inst_body = step("instantiate-memory-bank", inst)
            if inst.status_code != 200 or not isinstance(inst_body, dict) or not inst_body.get("plan_id"):
                print("FAIL: instantiate", inst.text[:500], file=sys.stderr)
                return 1
            plan_id = str(inst_body["plan_id"])
            report["path"] = "memory-bank"

        report["plan_id"] = plan_id
        got = client.get(f"{api_base}/rag/plan/{plan_id}", headers=headers)
        got_body = step("get-plan", got)
        if got.status_code != 200:
            return 1
        status = str(got_body.get("status") if isinstance(got_body, dict) else "")
        # Live API uses pending_review (NOM-024 gate before activation).
        if status != "pending_review":
            print(f"FAIL: expected pending_review status, got {status!r}", file=sys.stderr)
            return 1

        src = client.get(f"{api_base}/rag/plan/{plan_id}/sources", headers=headers)
        step("get-sources", src)  # may be empty for memory-bank drafts

        appr = client.patch(
            f"{api_base}/rag/plan/{plan_id}/approve",
            headers=headers,
            json={
                "action": "approve",
                "practitioner_notes": "DEMO-01 public walkthrough — aprobado (NOM-024 gate).",
            },
        )
        appr_body = step("approve", appr)
        if appr.status_code != 200:
            print("FAIL: approve", appr.text[:500], file=sys.stderr)
            return 1
        if isinstance(appr_body, dict) and appr_body.get("status") != "approved":
            print(f"FAIL: approve status={appr_body.get('status')!r}", file=sys.stderr)
            return 1

    report["pass"] = True
    print(json.dumps({k: report[k] for k in ("story", "path", "plan_id", "pass", "notes", "steps")}, indent=2))
    print("DEMO-01 PASS")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="DEMO-01 public API walkthrough")
    p.add_argument("--api-base", default=DEFAULT_API)
    p.add_argument(
        "--generate-timeout",
        type=float,
        default=110.0,
        help="Seconds to wait for /rag/plan/generate before fallback",
    )
    p.add_argument(
        "--skip-generate",
        action="store_true",
        help="Skip LLM generate and use memory-bank instantiate only",
    )
    args = p.parse_args(argv)
    return _run(args.api_base.rstrip("/"), args.generate_timeout, prefer_generate=not args.skip_generate)


if __name__ == "__main__":
    sys.exit(main())
