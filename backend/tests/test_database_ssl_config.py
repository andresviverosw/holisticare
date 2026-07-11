from app.core.config import Settings


def _settings(**overrides) -> Settings:
    base = {
        "postgres_user": "u",
        "postgres_password": "p@ss",
        "postgres_db": "holisticare_db",
        "postgres_host": "db",
        "postgres_port": 5432,
        "anthropic_api_key": "anthropic-test",
        "openai_api_key": "openai-test",
        "secret_key": "secret-test",
    }
    base.update(overrides)
    return Settings(**base)


def test_database_url_sync_uses_sslmode_for_remote_host():
    s = _settings(postgres_host="dpg-xxx.oregon-postgres.render.com")
    assert "sslmode=require" in s.database_url_sync
    assert "sslmode=require" in s.database_url_sync_psycopg2
    assert s.database_url_sync_psycopg2.startswith("postgresql+psycopg2://")


def test_database_url_sync_omits_sslmode_for_docker_compose():
    s = _settings(postgres_host="db")
    assert "sslmode" not in s.database_url_sync


def test_database_url_sync_urlencodes_password():
    s = _settings(postgres_password="p@ss:word")
    assert "p%40ss%3Aword" in s.database_url_sync


def test_database_url_sync_uses_database_url_override():
    s = _settings(
        database_url_override="postgresql://user:pass@dpg-xxx.oregon-postgres.render.com/holisticare_db",
    )
    assert s.database_url_sync.startswith("postgresql://user:pass@dpg-xxx")
    assert "sslmode=require" in s.database_url_sync


def test_postgres_port_none_string_defaults_to_5432():
    s = _settings(postgres_port="None")
    assert s.postgres_port == 5432
    assert ":5432/" in s.database_url_sync
