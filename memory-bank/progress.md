# Project Progress

## Completed Milestones

- Sprints 1–10: RAG plan loop, intake UX, nutrition safety, memory bank, prediction panels (see `docs/sprint-01.md` … `docs/sprint-10.md`).
- Security remediation TODO-SEC-001 … TODO-SEC-010 (`docs/09-security-audit-and-todos.md`).

## Pending Milestones

- Optional polish: US-MOB-003, PILOT-GO; paid Render for live LLM generate.
- Pilot GO/NO-GO / clinician alignment remains optional (FEEDBACK-01 waiver filed).

## Update History

- [2026-09-06] US-PRIV-002 **Done** — memory-bank free-text scrub via shared PRIV-001 helper.
- [2026-09-06] Track D **Done**: PR #26 merged; tag/release `capstone-final` on `main` (`a1229ca`). Historical `v1.0-final-AVW` kept.
- [2026-09-06] DEMO-01 PASS on public Render (memory-bank → approve); DEPLOY-01 / US-OPS-DEMO-REPAIR-001 Done earlier same day; US-OPS-OOM-001 passthrough fix merged.
- [2026-07-26 2:13:36 PM] [Unknown User] - Sprint 16 code + docs progress: US-PRIV-001 (patient_anonymizer + pipeline choke point + tests) and US-OPS-SPA-HOST (resolveApiBaseUrl + Vitest) Done. DOC-CLOSE-01/02/03 partial: Phase 1 FR/NFR filled, Phase 3 privacy complete, ADR-003/004, EVAL-01 report, FEEDBACK-01 synthetic waiver. Remaining: DEPLOY-01 Render public URLs, DEMO-01 walkthrough against live host, Track D tag/README URLs.
- [2026-07-25] Development/QA: **SYNTH-01** end-to-end synthetic dataset v1 (32 patients default, optional 80) + generate/seed CLIs + appendix docs; unit tests PASS.
- [2026-07-25] Planning Agent: Corrected D2 topology — Entrega 2 was **Render** (`deploy-entrega2-demo.md` / `render.yaml`), not Hetzner/Pages; added `deploy-final-demo.md` and restored blueprint on planning branch.
- [2026-07-25] Planning Agent: Locked D1–D4 — D2 = public deploy (initially mis-specified as Hetzner/Pages); promoted US-OPS-SPA-HOST + DEPLOY-01 to Must; plan status Approved / Sprint 16 ready for dev.
- [2026-07-25] Planning Agent: Final delivery plan + Sprint 16 initial draft; added US-PRIV-001/002 to backlog; cut mobile/IdP from final window.
- [2026-07-16] QA Agent: Sprint 11 **PASS** (`docs/qa-sprint-11-report.md`); e2e continuity suite added (7 Playwright total); Vitest 38; a11y label fix.
- [2026-07-16] Development: Sprint 11 UI execution — risk flags, clinician-proxy diary, analytics, sessions on Dashboard.
- [2026-07-16] Planning session: MVP UI blockers scoped as Sprint 11 ready-for-dev stories (`US-INT-002-UI`, `US-DIARY-UI`, `US-ANLY-UI`, `US-SESS-UI`). Diary v1 = clinician proxy.
- [2026-04-07] Removed duplicate `memory-bank/memory-bank/` tree; single canonical folder at repo root (`memory-bank/`). See `memory-bank/README.md`.
- [2026-04-07 12:18:31 PM] [Unknown User] - Decision Made: Standardize Memory Bank MCP usage
- [2026-04-07 12:18:31 PM] [Unknown User] - Security remediation milestone logged: Recorded completion of TODO-SEC-001, TODO-SEC-004, and TODO-SEC-006 with verification status; memory bank now configured and active.
