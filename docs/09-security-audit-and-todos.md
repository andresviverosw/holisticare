# Security Audit and TODOs

## Scope

Security checks were run on:
- Backend dependencies (`pip-audit`)
- Backend static code (`bandit`)
- Frontend dependencies (`npm audit`)

Date: 2026-04-07

## Commands used

- `pip-audit -r backend/requirements.txt -f json`
- `bandit -r backend/app -f txt`
- `npm audit --json` (in `frontend/`)

## Findings summary

### 1) Python dependency vulnerabilities (high priority)

`pip-audit` reported vulnerabilities in key packages.

Latest rerun after remediation slices (`python-jose`, FastAPI/Starlette, and `llama-index` modernization) reports:
- no known backend dependency vulnerabilities (`pip-audit -r backend/requirements.txt`)

- `python-jose==3.3.0`
  - JWT/JWE related vulnerabilities
  - fix version: `>=3.4.0`
- transitive `starlette==0.38.6`
  - multipart DoS advisories fixed in newer Starlette (`>=0.40.0`, `>=0.47.2`)

### 2) Frontend dependency vulnerabilities (medium priority)

Initial scan reported:
- `vite` advisory (path traversal related)
- transitive `esbuild` advisory
- suggested fix path to `vite@8.x`

Latest rerun after remediation (`npm audit --json`) reports no known frontend dependency vulnerabilities.

### 3) Bandit code scan (low/medium confidence issues)

Bandit reported:
- `B105` in `backend/app/api/auth.py` on `"token_type": "bearer"` (likely false positive)
- `B608` in `backend/app/services/chunk_query.py` due SQL text construction with f-string
  - currently low confidence because values are parameterized and filters are controlled
  - still worth hardening by removing dynamic query string assembly

## Prioritized TODOs

- [x] TODO-SEC-001 Upgrade `python-jose` to patched version
- Target: `python-jose>=3.4.0`
- Verify:
  - auth tests pass (`backend/tests/test_auth_dev_login.py` and auth-protected endpoints)
  - JWT decode compatibility unchanged
 - Implemented:
   - `backend/requirements.txt` now pins `python-jose[cryptography]==3.5.0`
   - targeted tests passing

- [x] TODO-SEC-002 Upgrade/replace vulnerable `pypdf`
- Preferred: update to latest stable major and validate ingestion.
- Verify:
  - ingestion works on current corpus
  - no major API break in `app/rag/ingestion/loader.py`
 - Implemented:
   - `backend/requirements.txt` now pins `pypdf==6.9.2`.
   - verified installation compatibility after `llama-index-*` modernization.
   - regression suite remains green (`pytest -q`: 99 passed).

- [x] TODO-SEC-003 Plan and execute `llama-index-*` security upgrade
- Implemented with compatible modern set:
  - `llama-index-core==0.14.20`
  - `llama-index-readers-file==0.6.0`
  - `llama-index-vector-stores-postgres==0.8.1`
  - `llama-index-embeddings-openai==0.6.0`
  - `llama-index-llms-anthropic==0.11.2`
  - supporting alignments: `pydantic==2.12.5`, `pydantic-settings==2.13.1`, `anthropic==0.90.0`
- Verification evidence:
  - backend tests: `pytest -q` -> `99 passed`
  - security scan: `pip-audit -r backend/requirements.txt` -> `No known vulnerabilities found`

- [x] TODO-SEC-004 Patch transitive Starlette/FastAPI chain
- Bump FastAPI to a release with patched Starlette.
- Verify:
  - all API tests pass
  - multipart/form behavior unaffected
 - Implemented:
   - `backend/requirements.txt` now pins `fastapi==0.121.3`
   - resolved transitive `starlette` to `0.50.0`
   - verified with tests:
     - `tests/test_plan_generate_api.py` (39 passed)
     - `tests/test_auth_dev_login.py`, `tests/test_chunk_query_security.py`, `tests/test_rag.py` (14 passed)

- [x] TODO-SEC-005 Frontend: upgrade Vite/esbuild safely
- Move to patched major (`vite@8.x`) in dedicated PR.
- Verify:
  - `npm run lint`, `npm run test`, `npm run build`
  - local dev server still proxies correctly
 - Implemented:
   - upgraded `vite` to `8.0.7` and `@vitejs/plugin-react` to `6.0.1` in `frontend/package.json`
   - refreshed lockfile via `npm install`
   - verification:
     - `npm run lint` passed
     - `npm run test` passed (`8` tests)
     - `npm run build` passed
     - `npm audit --json` reports zero vulnerabilities

- [x] TODO-SEC-006 Harden SQL query assembly in chunk listing
- Refactor `app/services/chunk_query.py` to avoid interpolated `where_clause` string.
- Use SQLAlchemy expression builder or fixed query branches.
- Add regression test ensuring filters still work.
 - Implemented:
   - replaced dynamic SQL assembly with static parameterized predicates
   - added `backend/tests/test_chunk_query_security.py`
   - list-chunks API regression tests passing

- [x] TODO-SEC-007 Reduce production risk from dev auth endpoint
- Keep `ALLOW_DEV_AUTH=false` in production.
- Add explicit deployment checklist check for this variable.
- Optional: disable route registration entirely outside debug/dev profiles.
 - Implemented:
   - `POST /auth/dev-login` is only registered when `ALLOW_DEV_AUTH=true` (`create_app()` in `backend/app/main.py`).
   - `docker-compose.yml` defaults `ALLOW_DEV_AUTH` to `false`; set `ALLOW_DEV_AUTH=true` in `.env` for local dev with the SPA dev login button.
   - `.env.example` documents the variable and production requirement.
 - **Deployment checklist (before production):**
   - Set `ALLOW_DEV_AUTH=false` (or omit; default in `Settings` is false).
   - Confirm `POST /auth/dev-login` returns **404** (route absent), not a token.
   - Never set `ALLOW_DEV_AUTH=true` on staging/production hosts.

- [x] TODO-SEC-008 Add security checks to CI (non-blocking first)
- Add optional/nightly job for:
  - `pip-audit`
  - `npm audit --audit-level=moderate`
  - `bandit -r backend/app`
- Start as advisory; promote to blocking after dependency remediation.
 - Implemented:
   - added `security-audit` job to `.github/workflows/ci.yml`
   - job runs `pip-audit`, `bandit`, and frontend `npm audit --audit-level=moderate`
   - configured as advisory with `continue-on-error: true`

## Notes and assumptions

- Findings are based on automated scanners; some are environment-specific or low-confidence.
- Dependency upgrades should be handled in small, test-backed slices because this codebase has LLM SDK integration points that can break on minor/major updates.

