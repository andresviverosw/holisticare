"""US-OPS-PROD-COMPOSE — contract tests for production Compose overlay (no Docker required)."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(rel: str) -> str:
    path = REPO_ROOT / rel
    assert path.is_file(), f"Missing required file: {rel}"
    return path.read_text(encoding="utf-8")


def test_prod_compose_exists_and_lists_backend_and_caddy_only():
    text = _read("docker-compose.prod.yml")
    assert "services:" in text
    assert "backend:" in text
    assert "caddy:" in text
    # Dev stack services must not appear as top-level services
    assert "\n  db:" not in text
    assert "\n  frontend:" not in text


def test_prod_compose_forces_allow_dev_auth_false():
    text = _read("docker-compose.prod.yml")
    assert 'ALLOW_DEV_AUTH: "false"' in text or "ALLOW_DEV_AUTH: 'false'" in text


def test_prod_compose_backend_has_no_reload_or_source_bind():
    text = _read("docker-compose.prod.yml")
    # Ignore comments when checking for the reload flag
    code_lines = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
    assert "--reload" not in code_lines
    assert "./backend:/app" not in code_lines
    assert "uvicorn app.main:app" in code_lines
    assert "--workers" in code_lines
    # Image-based deploy (not build: on the server)
    assert "image:" in code_lines
    assert "ghcr.io/" in code_lines
    assert "holisticare-backend" in code_lines
    # API only exposed on the docker network
    assert "expose:" in code_lines
    assert "8000" in code_lines


def test_prod_compose_caddy_publishes_80_and_443():
    text = _read("docker-compose.prod.yml")
    assert '"80:80"' in text or "80:80" in text
    assert '"443:443"' in text or "443:443" in text
    assert "./Caddyfile" in text


def test_caddyfile_reverse_proxies_backend():
    text = _read("Caddyfile")
    assert "reverse_proxy backend:8000" in text
    assert "api.example.com" in text or "{" in text


def test_env_prod_example_safe_defaults():
    text = _read(".env.prod.example")
    assert "DEBUG=false" in text
    assert "ALLOW_DEV_AUTH=false" in text
    assert "CORS_ORIGINS=" in text
    assert "SECRET_KEY=" in text
    # Must not look like a committed real secret
    assert "sk-ant-" not in text
    assert "changeme" in text.lower() or "replace" in text.lower() or "generate" in text.lower()
