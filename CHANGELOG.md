# Changelog

All notable changes to this project are documented here. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [2026-04-07]

### Added

- **US-RAG-001:** RAG corpus ingestion accepts `.html` and `.htm` in addition to `.pdf` (visible text extraction via BeautifulSoup; one indexed document per file). See `docs/setup.md` (section 4.3) and `docs/04-feature-specs-and-user-stories.md`.

### Security

- Bump **Pillow** to `12.1.1` to address **CVE-2026-25990** (CI `pip-audit`).
