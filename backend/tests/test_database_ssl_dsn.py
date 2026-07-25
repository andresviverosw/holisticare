"""US-OPS-PROD-COMPOSE — Postgres SSL DSN flag."""

from __future__ import annotations

from app.core.config import get_settings


def test_database_url_appends_ssl_when_required(monkeypatch):
    monkeypatch.setenv("POSTGRES_SSL_REQUIRE", "true")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.postgres_ssl_require is True
    assert settings.database_url.endswith("?ssl=require")
    assert "sslmode=require" in settings.database_url_sync
    get_settings.cache_clear()


def test_database_url_omits_ssl_by_default(monkeypatch):
    monkeypatch.delenv("POSTGRES_SSL_REQUIRE", raising=False)
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.postgres_ssl_require is False
    assert "?ssl=" not in settings.database_url
    get_settings.cache_clear()
