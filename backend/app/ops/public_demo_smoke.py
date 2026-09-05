"""US-OPS CD — pure checks for public Render demo smoke (no network)."""

from __future__ import annotations

import json
from typing import Any, Mapping


def check_health(status_code: int, body: Any) -> list[str]:
    errors: list[str] = []
    if status_code != 200:
        errors.append(f"health status_code={status_code} expected 200")
        return errors
    if not isinstance(body, dict):
        errors.append("health body must be JSON object")
        return errors
    if body.get("status") != "ok":
        errors.append(f"health status={body.get('status')!r} expected 'ok'")
    return errors


def check_spa(status_code: int, html: str) -> list[str]:
    errors: list[str] = []
    if status_code != 200:
        errors.append(f"spa status_code={status_code} expected 200")
        return errors
    if 'id="root"' not in html and "id='root'" not in html:
        errors.append("spa HTML missing #root")
    if "HolistiCare" not in html:
        errors.append("spa HTML missing HolistiCare title/brand")
    return errors


def check_cors(headers: Mapping[str, str], origin: str) -> list[str]:
    errors: list[str] = []
    # httpx / curl headers are case-insensitive; normalize
    normalized = {str(k).lower(): str(v) for k, v in headers.items()}
    allow = normalized.get("access-control-allow-origin", "")
    if allow != origin and allow != "*":
        errors.append(
            f"CORS allow-origin={allow!r} expected {origin!r}"
        )
    return errors


def check_dev_login(status_code: int, body: Any) -> list[str]:
    errors: list[str] = []
    if status_code != 200:
        errors.append(f"dev-login status_code={status_code} expected 200")
        return errors
    if not isinstance(body, dict):
        errors.append("dev-login body must be JSON object")
        return errors
    token = body.get("access_token")
    if not isinstance(token, str) or not token.strip():
        errors.append("dev-login missing access_token")
    if body.get("role") != "clinician":
        errors.append(f"dev-login role={body.get('role')!r} expected clinician")
    return errors


def check_ready(status_code: int, body: Any) -> list[str]:
    """Delegate to readiness helper (US-OPS-MONITOR-001)."""
    from app.ops.readiness import check_ready as _check_ready

    return _check_ready(status_code, body)


def parse_json_body(raw: str | bytes | None) -> Any:
    if raw is None or raw == "":
        return None
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw
