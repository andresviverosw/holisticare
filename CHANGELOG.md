# Changelog

All notable changes to this project are documented here. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- **Sprint 11 planning (R1-UI):** Ready-for-dev UI stories for MVP continuity blockers — `US-INT-002-UI`, `US-DIARY-UI`, `US-ANLY-UI`, `US-SESS-UI`. See `docs/sprint-11.md`.

### Security

- **TODO-SEC-011:** Patch CI `pip-audit` findings — bump FastAPI/Starlette, pydantic-settings, pypdf, pillow, transformers; replace `python-jose` with `PyJWT` (removes unfixed transitive `ecdsa`). See `docs/09-security-audit-and-todos.md`.

## [2026-04-07]

### Added

- **US-RAG-001:** RAG corpus ingestion accepts `.html` and `.htm` in addition to `.pdf` (visible text extraction via BeautifulSoup; one indexed document per file). See `docs/setup.md` (section 4.3) and `docs/04-feature-specs-and-user-stories.md`.

### Security

- Bump **Pillow** to `12.1.1` to address **CVE-2026-25990** (CI `pip-audit`).
