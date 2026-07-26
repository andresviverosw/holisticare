#!/usr/bin/env python3
"""
Trigger Render deploys for CD (used by .github/workflows/cd-render.yml).

Env:
  RENDER_API_KEY (required)
  API_SERVICE_ID, FE_SERVICE_ID (required)
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


API_ROOT = "https://api.render.com/v1"


def _request(method: str, path: str, body: dict | None = None) -> tuple[int, Any]:
    key = os.environ.get("RENDER_API_KEY") or ""
    if not key:
        raise SystemExit("RENDER_API_KEY is required")
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{API_ROOT}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            payload: Any = json.loads(raw) if raw.strip() else {}
            return resp.status, payload
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw) if raw.strip() else {"message": raw}
        except json.JSONDecodeError:
            payload = {"message": raw}
        return exc.code, payload


def _write_deploy(path: Path, deploy: dict) -> None:
    path.write_text(json.dumps(deploy), encoding="utf-8")


def _latest_deploy(service_id: str) -> dict | None:
    code, payload = _request("GET", f"/services/{service_id}/deploys?limit=1")
    if code >= 400:
        print(f"latest deploy HTTP {code}: {payload}", flush=True)
        return None
    item = payload[0] if isinstance(payload, list) and payload else payload
    if isinstance(item, dict) and "deploy" in item:
        dep = item["deploy"]
    elif isinstance(item, dict):
        dep = item
    else:
        return None
    return dep if isinstance(dep, dict) and dep.get("id") else None


def trigger_one(service_id: str, out: Path) -> None:
    print(f"Deploying {service_id} ...", flush=True)
    for attempt in range(1, 4):
        code, payload = _request(
            "POST",
            f"/services/{service_id}/deploys",
            {"clearCache": "clear"},
        )
        print(f"attempt={attempt} HTTP={code} body={str(payload)[:400]}", flush=True)
        if isinstance(payload, dict) and payload.get("id"):
            _write_deploy(out, payload)
            print(f"created deploy id={payload['id']}", flush=True)
            return

        latest = _latest_deploy(service_id)
        if latest:
            _write_deploy(out, latest)
            print(
                f"adopted deploy id={latest['id']} status={latest.get('status')}",
                flush=True,
            )
            return
        time.sleep(8)
    raise SystemExit(f"Failed to trigger or adopt a deploy for {service_id}")


def wait_one(service_id: str, deploy_path: Path) -> None:
    dep = json.loads(deploy_path.read_text(encoding="utf-8"))
    dep_id = dep["id"]
    print(f"Waiting for {service_id} deploy {dep_id} ...", flush=True)
    for i in range(1, 61):
        code, payload = _request("GET", f"/services/{service_id}/deploys/{dep_id}")
        status = payload.get("status") if isinstance(payload, dict) else None
        print(f"[{i}] {service_id}={status} (HTTP {code})", flush=True)
        if status == "live":
            return
        if status in {"build_failed", "update_failed", "canceled", "deactivated"}:
            raise SystemExit(f"Deploy failed: {status}")
        time.sleep(15)
    raise SystemExit(f"Timed out waiting for {service_id}")


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] not in {"trigger", "wait"}:
        print("Usage: trigger_render_deploys.py trigger|wait", file=sys.stderr)
        return 2
    api_id = os.environ.get("API_SERVICE_ID") or ""
    fe_id = os.environ.get("FE_SERVICE_ID") or ""
    if not api_id or not fe_id:
        raise SystemExit("API_SERVICE_ID and FE_SERVICE_ID are required")

    api_out = Path(f"/tmp/deploy-{api_id}.json")
    fe_out = Path(f"/tmp/deploy-{fe_id}.json")

    if argv[1] == "trigger":
        trigger_one(api_id, api_out)
        trigger_one(fe_id, fe_out)
        return 0

    wait_one(api_id, api_out)
    wait_one(fe_id, fe_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
