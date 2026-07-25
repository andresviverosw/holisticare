# QA Report — Sprint 15 (US-OPS-PROD-COMPOSE)

**Date:** 2026-07-16  
**Owner:** QA Agent  
**Branch / PR:** `cursor/sprint-15-ops-prod-compose-exec-2591`  
**Scope:** US-OPS-PROD-COMPOSE  

## Verdict

**PASS — ready for Planning Agent backlog closeout / merge**

No blocking defects. Prod Compose overlay + Caddy + env contract shipped with CI structural tests (no live TLS).

## Acceptance criteria (pass/fail)

| AC | Result | Evidence |
|----|--------|----------|
| Prod compose has backend + caddy only | **PASS** | `test_prod_compose_exists_and_lists_backend_and_caddy_only` |
| Force `ALLOW_DEV_AUTH=false` | **PASS** | `test_prod_compose_forces_allow_dev_auth_false` |
| No reload / source bind; image + workers | **PASS** | `test_prod_compose_backend_has_no_reload_or_source_bind` |
| Caddyfile reverse_proxy backend:8000 | **PASS** | `test_caddyfile_reverse_proxies_backend` |
| `.env.prod.example` safe defaults | **PASS** | `test_env_prod_example_safe_defaults` |
| Docs checklist health + dev-login 404 | **PASS** | `docs/06-deployment-and-ops-runbook.md` |
| NOM-024 unchanged | **PASS** | No plan-approval code changes |
| Optional SSL DSN flag | **PASS** | `test_database_ssl_dsn.py` |
| Optional GHCR workflow | **PASS** | `.github/workflows/build-backend.yml` present |

## Commands run

```bash
pytest tests/test_prod_compose_contract.py tests/test_database_ssl_dsn.py \
  tests/test_auth_dev_login.py tests/test_auth_password_login.py -q   # 17 passed
```

## Risks / residual

| Risk | Severity | Note |
|------|----------|------|
| GHCR image must exist before `pull` | Medium | Workflow on main; or manual build |
| `api.example.com` must be replaced | Medium | Documented in Caddyfile / runbook |
| SPA still needs static host + API base URL | Medium | `US-OPS-SPA-HOST` follow-on |
| Live TLS not exercised in CI | Low | Manual smoke on real host |

## Handoff

- Backlog item ID: US-OPS-PROD-COMPOSE
- Scope: prod compose + Caddy + env template + contract tests + GHCR workflow + SSL flag
- Acceptance criteria: **PASS**
- Test evidence: commands above
- Risks/issues: SPA host still follow-on
- Next owner: **Planning Agent**
