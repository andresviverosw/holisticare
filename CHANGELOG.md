# Changelog

All notable changes to this project are documented here. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

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
