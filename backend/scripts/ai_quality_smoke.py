#!/usr/bin/env python3
"""
AI quality smoke checks for plan generation.

Purpose:
- Deterministic contract checks over generated plans.
- Fast signal before pilot/demo and before enabling stricter CI gates.

Run inside backend container:
  docker compose exec backend env PYTHONPATH=/app python scripts/ai_quality_smoke.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import httpx
from jose import jwt

from app.core.config import get_settings

REF_ID_RE = re.compile(r"^REF-[A-Za-z0-9._-]+$")


def _clinician_token() -> str:
    s = get_settings()
    return jwt.encode(
        {"sub": "ai-quality-smoke", "role": "clinician"},
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

    validated: list[dict] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"Case #{i} is not an object")
        case_id = item.get("case_id")
        req = item.get("request")
        if not case_id or not isinstance(case_id, str):
            raise ValueError(f"Case #{i} requires string 'case_id'")
        if not isinstance(req, dict):
            raise ValueError(f"Case {case_id} requires object 'request'")
        validated.append(item)
    return validated


def _validate_plan_contract(
    case_id: str,
    data: dict,
    require_case_citations: bool,
    min_weeks: int,
    min_citations: int,
    allow_insufficient_evidence: bool,
) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []

    plan_id = data.get("plan_id")
    if not isinstance(plan_id, str) or len(plan_id.strip()) == 0:
        errors.append("missing/invalid plan_id")

    status = data.get("status")
    if status != "pending_review":
        errors.append(f"unexpected status={status!r} (expected 'pending_review')")

    weeks = data.get("weeks")
    if not isinstance(weeks, list):
        errors.append("weeks missing or invalid type")
        weeks = []
    elif len(weeks) < min_weeks and not insufficient_true:
        errors.append(f"weeks count {len(weeks)} below minimum {min_weeks}")

    insufficient = data.get("insufficient_evidence")
    insufficient_true = insufficient not in (False, 0)
    if insufficient_true:
        if allow_insufficient_evidence:
            warnings.append("insufficient_evidence is true (allowed by flag)")
        else:
            errors.append("insufficient_evidence is true")

    citations = data.get("citations_used")
    if not isinstance(citations, list):
        errors.append("citations_used must be a list")
    else:
        if require_case_citations and len(citations) == 0 and not insufficient_true:
            errors.append("citations_used empty (case requires citations)")
        if len(citations) < min_citations and not insufficient_true:
            errors.append(f"citations_used count {len(citations)} below minimum {min_citations}")
        if len(citations) == 0:
            warnings.append("citations_used empty")
        for ref in citations:
            if not isinstance(ref, str):
                errors.append("citations_used contains non-string entry")
            elif not REF_ID_RE.match(ref):
                warnings.append(f"citation does not match REF-* pattern: {ref}")

    retrieval = data.get("retrieval_metadata")
    if retrieval is not None and not isinstance(retrieval, dict):
        errors.append("retrieval_metadata must be an object when present")

    result: list[str] = []
    for err in errors:
        result.append(f"ERROR [{case_id}] {err}")
    for warn in warnings:
        result.append(f"WARN  [{case_id}] {warn}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="AI quality smoke checks")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--cases", default="/app/data/pilot/cases.json")
    parser.add_argument("--timeout-seconds", type=float, default=300.0)
    parser.add_argument(
        "--connect-retries",
        type=int,
        default=12,
        help="Number of retries for transient connection errors before failing",
    )
    parser.add_argument(
        "--retry-delay-seconds",
        type=float,
        default=5.0,
        help="Delay between connection retry attempts",
    )
    parser.add_argument(
        "--require-case-citations",
        action="store_true",
        help="Fail each case if citations_used is empty",
    )
    parser.add_argument(
        "--require-any-citations",
        action="store_true",
        help="Fail if all evaluated cases have zero citations_used",
    )
    parser.add_argument(
        "--allow-insufficient-evidence",
        action="store_true",
        help="Do not fail when insufficient_evidence=true (useful for constrained CI corpora)",
    )
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    try:
        cases = _load_cases(Path(args.cases))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    headers = {
        "Authorization": f"Bearer {_clinician_token()}",
        "Content-Type": "application/json",
    }

    print(f"Loaded {len(cases)} AI-quality cases from {args.cases}")
    print(f"Target API: {base}")

    error_count = 0
    total_citations = 0
    with httpx.Client(timeout=args.timeout_seconds) as client:
        for case in cases:
            case_id = case["case_id"]
            payload = case["request"]
            exp = case.get("ai_expectations") or {}
            min_weeks = int(exp.get("min_weeks", 1))
            min_citations = int(exp.get("min_citations", 0))
            resp = None
            last_exc: Exception | None = None
            for attempt in range(1, args.connect_retries + 1):
                try:
                    resp = client.post(f"{base}/rag/plan/generate", headers=headers, json=payload)
                    last_exc = None
                    break
                except httpx.ConnectError as exc:
                    last_exc = exc
                    print(
                        f"WARN  [{case_id}] connect attempt {attempt}/{args.connect_retries} failed: {exc}",
                        file=sys.stderr,
                    )
                    if attempt < args.connect_retries:
                        time.sleep(args.retry_delay_seconds)

            if resp is None:
                error_count += 1
                print(
                    f"ERROR [{case_id}] connection failed after {args.connect_retries} attempts: {last_exc}",
                    file=sys.stderr,
                )
                continue

            print(f"\n[{case_id}] POST /rag/plan/generate -> {resp.status_code}")
            if resp.status_code != 200:
                error_count += 1
                print(f"ERROR [{case_id}] non-200 response: {resp.status_code}", file=sys.stderr)
                print(resp.text[:1000], file=sys.stderr)
                continue

            data = resp.json()
            citations = data.get("citations_used") or []
            if isinstance(citations, list):
                total_citations += len(citations)
            messages = _validate_plan_contract(
                case_id=case_id,
                data=data,
                require_case_citations=args.require_case_citations,
                min_weeks=min_weeks,
                min_citations=min_citations,
                allow_insufficient_evidence=args.allow_insufficient_evidence,
            )
            for msg in messages:
                print(msg)
                if msg.startswith("ERROR"):
                    error_count += 1

    if args.require_any_citations and total_citations == 0 and not args.allow_insufficient_evidence:
        error_count += 1
        print(
            "ERROR [global] citations_used is empty across all evaluated cases",
            file=sys.stderr,
        )
    elif args.require_any_citations and total_citations == 0 and args.allow_insufficient_evidence:
        print(
            "WARN  [global] citations_used is empty across all evaluated cases (allowed by flag)",
            file=sys.stderr,
        )

    if error_count:
        print(f"\nAI quality smoke failed with {error_count} error(s).", file=sys.stderr)
        return 1

    print("\nAI quality smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
