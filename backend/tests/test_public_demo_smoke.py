"""Unit tests for public demo smoke checkers (US-OPS CD)."""

from app.ops.public_demo_smoke import (
    check_authenticated_chunks,
    check_cors,
    check_dev_login,
    check_health,
    check_ready,
    check_spa,
    parse_json_body,
)


def test_check_health_ok():
    assert check_health(200, {"status": "ok", "version": "0.1.0"}) == []


def test_check_health_rejects_bad_status():
    errs = check_health(503, {"status": "ok"})
    assert any("status_code" in e for e in errs)


def test_check_spa_ok():
    html = "<html><title>HolistiCare — x</title><div id=\"root\"></div></html>"
    assert check_spa(200, html) == []


def test_check_spa_missing_root():
    errs = check_spa(200, "<html><title>HolistiCare</title></html>")
    assert any("#root" in e for e in errs)


def test_check_cors_exact_origin():
    origin = "https://holisticare-frontend.onrender.com"
    assert check_cors({"Access-Control-Allow-Origin": origin}, origin) == []


def test_check_cors_mismatch():
    errs = check_cors(
        {"access-control-allow-origin": "https://evil.example"},
        "https://holisticare-frontend.onrender.com",
    )
    assert errs


def test_check_dev_login_ok():
    assert (
        check_dev_login(
            200,
            {"access_token": "abc", "token_type": "bearer", "role": "clinician"},
        )
        == []
    )


def test_check_dev_login_missing_token():
    errs = check_dev_login(200, {"role": "clinician"})
    assert any("access_token" in e for e in errs)


def test_check_ready_ok():
    assert check_ready(200, {"status": "ready", "db": "ok"}) == []


def test_check_authenticated_chunks_ok():
    assert check_authenticated_chunks(200, {"items": [], "limit": 3, "offset": 0}) == []
    assert check_authenticated_chunks(200, {"items": [{"ref_id": "a"}]}) == []


def test_check_authenticated_chunks_rejects_errors():
    assert any("status_code" in e for e in check_authenticated_chunks(500, {"items": []}))
    assert any("items" in e for e in check_authenticated_chunks(200, {}))
    assert any("items" in e for e in check_authenticated_chunks(200, {"items": "x"}))


def test_parse_json_body():
    assert parse_json_body('{"status":"ok"}') == {"status": "ok"}
    assert parse_json_body("not-json") == "not-json"
