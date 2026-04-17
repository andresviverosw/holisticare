#!/usr/bin/env python3
"""
Run a repeatable pilot rehearsal against /rag/plan/generate using synthetic cases.

Run inside backend container:
  docker compose exec backend env PYTHONPATH=/app python scripts/pilot_rehearsal.py
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import httpx
from jose import jwt

from app.core.config import get_settings


def _clinician_token() -> str:
    s = get_settings()
    return jwt.encode(
        {"sub": "pilot-rehearsal", "role": "clinician"},
        s.secret_key,
        algorithm="HS256",
    )


def _load_cases(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"Cases file not found: {path}") from None
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in cases file {path}: {exc}") from exc

    if not isinstance(data, list) or not data:
        raise ValueError("Cases file must be a non-empty JSON array")

    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"Case {idx} is not an object")
        if "case_id" not in item or "request" not in item:
            raise ValueError(f"Case {idx} requires 'case_id' and 'request'")
        if not isinstance(item["request"], dict):
            raise ValueError(f"Case {item.get('case_id', idx)} request must be an object")

    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Pilot rehearsal runner")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--cases", default="/app/data/pilot/cases.json")
    parser.add_argument("--timeout-seconds", type=float, default=300.0)
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    cases_path = Path(args.cases)

    try:
        cases = _load_cases(cases_path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    token = _clinician_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    print(f"Loaded {len(cases)} pilot cases from {cases_path}")
    print(f"Target API: {base}")

    failures = 0
    with httpx.Client(timeout=args.timeout_seconds) as client:
        for case in cases:
            case_id = case["case_id"]
            description = case.get("description", "")
            payload = case["request"]

            print(f"\n=== {case_id} ===")
            if description:
                print(description)

            start = time.perf_counter()
            resp = client.post(f"{base}/rag/plan/generate", headers=headers, json=payload)
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            print(f"POST /rag/plan/generate -> {resp.status_code} ({elapsed_ms} ms)")

            if resp.status_code != 200:
                failures += 1
                print(resp.text[:1200], file=sys.stderr)
                continue

            data = resp.json()
            status = data.get("status")
            plan_id = data.get("plan_id")
            weeks = data.get("weeks") or []
            citations = data.get("citations_used") or []
            insufficient = bool(data.get("insufficient_evidence"))

            print(f"plan_id: {plan_id}")
            print(f"status: {status}")
            print(f"weeks: {len(weeks)}")
            print(f"citations_used: {len(citations)}")
            print(f"insufficient_evidence: {insufficient}")

            if status != "pending_review":
                failures += 1
                print("Unexpected plan status (expected pending_review)", file=sys.stderr)
            if not weeks:
                failures += 1
                print("Plan has no weeks", file=sys.stderr)
            if insufficient:
                failures += 1
                print("Insufficient evidence flag set", file=sys.stderr)

    if failures:
        print(f"\nPilot rehearsal finished with {failures} failure(s).", file=sys.stderr)
        return 1

    print("\nPilot rehearsal passed for all cases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
