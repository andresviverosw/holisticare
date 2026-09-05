#!/usr/bin/env python3
"""
Public Render demo smoke (DEPLOY-01 / CD).

Usage:
  python scripts/smoke_public_demo.py
  python scripts/smoke_public_demo.py --api-base https://holisticare-api.onrender.com \\
      --spa-base https://holisticare-frontend.onrender.com
"""
from __future__ import annotations

import argparse
import sys
import time

import httpx

from app.ops.public_demo_smoke import (
    check_cors,
    check_dev_login,
    check_health,
    check_ready,
    check_spa,
    parse_json_body,
)


def _run(api_base: str, spa_base: str, origin: str, timeout: float) -> int:
    errors: list[str] = []
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        # Cold start: retry health a few times
        health_body = None
        health_code = 0
        for attempt in range(1, 6):
            r = client.get(f"{api_base.rstrip('/')}/health")
            health_code = r.status_code
            health_body = parse_json_body(r.text)
            if health_code == 200:
                break
            time.sleep(min(15 * attempt, 60))
        errors.extend(check_health(health_code, health_body))

        ready = client.get(f"{api_base.rstrip('/')}/ready")
        errors.extend(check_ready(ready.status_code, parse_json_body(ready.text)))

        spa = client.get(spa_base)
        errors.extend(check_spa(spa.status_code, spa.text))

        opt = client.options(
            f"{api_base.rstrip('/')}/auth/dev-login",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
            },
        )
        errors.extend(check_cors(opt.headers, origin))

        login = client.post(
            f"{api_base.rstrip('/')}/auth/dev-login",
            json={"role": "clinician", "sub": "cd-smoke"},
            headers={"Origin": origin},
        )
        errors.extend(check_dev_login(login.status_code, parse_json_body(login.text)))

    if errors:
        print("SMOKE FAIL:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("SMOKE PASS: health + ready + spa + cors + dev-login")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Smoke public HolistiCare Render demo")
    p.add_argument(
        "--api-base",
        default="https://holisticare-api.onrender.com",
    )
    p.add_argument(
        "--spa-base",
        default="https://holisticare-frontend.onrender.com",
    )
    p.add_argument(
        "--origin",
        default="https://holisticare-frontend.onrender.com",
        help="Browser Origin for CORS checks",
    )
    p.add_argument("--timeout", type=float, default=120.0)
    args = p.parse_args(argv)
    return _run(args.api_base, args.spa_base, args.origin, args.timeout)


if __name__ == "__main__":
    sys.exit(main())
