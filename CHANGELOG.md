# Changelog

All notable changes to this project are documented here. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- **DEMO-01:** public Render walkthrough script + evidence (`scripts/demo_public_walkthrough.py`, `docs/demo-01-public-walkthrough.md`) — login → intake → memory-bank instantiate → approve (NOM-024 gate). LLM generate on free tier may 502 near ~100s.

### Security
- **US-SEC-RBAC-001:** clinician/admin required on clinical GETs (intake, risk-flags, plan, sources, chunks) + auth-matrix tests.
- **CI security-audit:** bump `pypdf` `6.14.2` → `6.17.0`, `transformers` `5.5.0` → `5.16.1`; temporary ignore for transitive `nltk` **PYSEC-2026-3740** (no newer release; TODO-SEC-015).
- **CI npm audit:** overrides `brace-expansion@5.0.9`, `js-yaml@4.3.2`, `nanoid@3.3.18` (high advisories).

### Added
- **US-OPS-HEALTH-001 / MONITOR-001:** `GET /ready` DB probe; public smoke + 6h GitHub monitor check readiness.
- **US-OPS-SCHEMA-001:** `scripts/migrate.sh` applies `infra/init.sql` + patches in order.
- **DOC-QUICKSTART / OPS / PROMPTS:** README ingest path, filled ops runbook, prompt excerpts, demo repair checklist.

### Added

- **Sprint 17 planning (AI4devs review remediation):** `docs/ai4devs-review-remediation-plan.md` + `docs/sprint-17.md` — backlog for RBAC hotfix on unguarded clinical GETs, DB readiness, public demo repair, monitoring, schema migrations, and docs polish (tutor *Aprobado con notas*, 19 Aug 2026).
- **CD Render (CI-gated):** `.github/workflows/cd-render.yml` deploys API+SPA after CI succeeds on `main`, then runs `scripts/smoke_public_demo.py`. Render `autoDeploy` disabled.
- **Sprint 16 / US-PRIV-001:** LLM egress anonymization (`patient_anonymizer.py`) — clinical projection + email/phone/UUID redaction; `PATIENT_TOKEN` in generator prompts; fail-closed API 422; unit + pipeline tests.
- **Sprint 16 / US-OPS-SPA-HOST:** `resolveApiBaseUrl` + `VITE_API_BASE_URL` for Render Static Site (fallback `/api`).
- **DOC-CLOSE / EVAL / FEEDBACK:** Phase 1 §7 FR/NFR, Phase 3 privacy framework, ADR-003/004, `docs/rag-evaluation-report.md`, `docs/feedback-01-synthetic-demo-waiver.md`.

### Fixed

- **CI backend-tests:** `test_redeem_invite_200_returns_patient_jwt_with_exp` used a fixed July-16 `expires_at`, which became expired vs wall-clock `datetime.now(UTC)` after that date (410 instead of 200).
- **CI security-audit:** bump `pypdf` `6.13.3` → `6.14.2` (CVE-2026-59935..59938); frontend `npm audit` via React 19 + `react-router@8.3.0`, `brace-expansion@5.0.8` / `minimatch@10` overrides; CI Node `22.22`.

### Added (prior)

- **SYNTH-01:** End-to-end synthetic dataset v1 — deterministic generator (`app/synthetic/`), committed package (`backend/data/synthetic/v1/dataset.json`, 32 patients), generate/seed CLIs, analytics/plateau/recovery cohort coverage, docs appendix (`docs/synthetic-dataset-v1.md`).
- **Final delivery planning (Approved):** `docs/final-delivery-plan.md` + `docs/sprint-16.md` — D1–D4 locked; Must tracks **US-PRIV-001**, **US-OPS-SPA-HOST** + **DEPLOY-01** on **Render** (Entrega 2 parity: `render.yaml`, `docs/deploy-final-demo.md`); mobile/JWT-harden/IdP cut.
- **Sprint 15 execution (US-OPS-PROD-COMPOSE):** `docker-compose.prod.yml`, `Caddyfile`, `.env.prod.example`, GHCR build workflow, `POSTGRES_SSL_REQUIRE` DSN flag.
- **Sprint 15 QA:** compose contract tests + report (`docs/qa-sprint-15-report.md`).
- **Sprint 15 planning:** `US-OPS-PROD-COMPOSE` ready-for-dev (`docs/sprint-15.md`) — `docker-compose.prod.yml` + Caddyfile + prod env contract.
- **Sprint 14 execution (US-AUTH-CLINICIAN-PROD):** `app_users` + bcrypt, `POST /auth/login`, `seed_clinician.py`, Login username/password SPA.
- **Sprint 14 QA:** Playwright clinician login smoke + report (`docs/qa-sprint-14-report.md`).
- **Sprint 14 planning:** `US-AUTH-CLINICIAN-PROD` ready-for-dev (`docs/sprint-14.md`) — username/password login + seed clinician JWT with `exp`.
- **Sprint 13 execution (US-DIARY-AUTH-PROD):** single-use diary invites (`POST /rag/diary/invites`, `POST /auth/redeem-invite`), patient JWT `exp`, Dashboard/Login SPA.
- **Sprint 13 QA:** Playwright invite smoke + report (`docs/qa-sprint-13-report.md`).
- **Sprint 13 planning:** `US-DIARY-AUTH-PROD` ready-for-dev (`docs/sprint-13.md`) — single-use patient invite link → JWT with `exp` (no OTP/IdP this slice).
- **Sprint 12 execution (US-DIARY-UI-PATIENT):** patient `/diario`, `RequirePatient` / clinician role redirects, extended `POST /auth/dev-login` for `role=patient` + UUID v4 `sub`.
- **Sprint 12 QA:** Playwright patient diary smoke + report (`docs/qa-sprint-12-report.md`).
- **Sprint 12 planning:** `US-DIARY-UI-PATIENT` ready-for-dev (`docs/sprint-12.md`) — patient `/diario`, patient JWT via extended dev-login.
- **Sprint 11 planning (R1-UI):** Ready-for-dev UI stories for MVP continuity blockers — `US-INT-002-UI`, `US-DIARY-UI`, `US-ANLY-UI`, `US-SESS-UI`. See `docs/sprint-11.md`.
- **Sprint 11 execution:** Dashboard continuity UI — intake risk flags, clinician-proxy diary, outcome trends/plateaus, session log + note suggest (Vitest builders + `api.js` wiring).
- **Sprint 11 QA:** Continuity Playwright suite + report (`docs/qa-sprint-11-report.md`); label a11y fix on session/patient fields.

### Security

- **TODO-SEC-011:** Patch CI `security-audit` findings — bump FastAPI/Starlette, pydantic-settings, pypdf, pillow, transformers; replace `python-jose` with `PyJWT`; frontend `npm audit fix` (axios/vite/vitest/react-router/postcss). See `docs/09-security-audit-and-todos.md`.

## [2026-04-07]

### Added

- **US-RAG-001:** RAG corpus ingestion accepts `.html` and `.htm` in addition to `.pdf` (visible text extraction via BeautifulSoup; one indexed document per file). See `docs/setup.md` (section 4.3) and `docs/04-feature-specs-and-user-stories.md`.

### Security

- Bump **Pillow** to `12.1.1` to address **CVE-2026-25990** (CI `pip-audit`).
