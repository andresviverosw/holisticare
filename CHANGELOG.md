# Changelog

All notable changes to this project are documented here. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

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
