# Sprint 16 — Final delivery: US-PRIV-001 + US-OPS-SPA-HOST + capstone closeout

## Sprint parameters

| Field | Value |
|-------|--------|
| Length | Capstone closeout slice (privacy + public deploy + academic packaging) |
| Primary stories | **US-PRIV-001**, **US-OPS-SPA-HOST** |
| Companion tracks | DEPLOY-01, DOC-CLOSE-01..03, EVAL-01, DEMO-01, FEEDBACK-01 |
| Priority | Must (final master’s delivery) |
| Scope | LLM egress anonymization; SPA `VITE_API_BASE_URL` + **Render** public deploy (Entrega 2 parity); privacy docs; submission package |
| Owner | Planning → Development (TDD) → Ops deploy → QA |
| Status | **Code + docs complete; DEPLOY-01 awaiting operator Render deploy** |
| Plan of record | [`final-delivery-plan.md`](final-delivery-plan.md) |

## Problem statement

HolistiCare’s MVP product loop is implemented through Sprint 15, but Phase 1 risk **R-02** (LFPDPPP × international LLM APIs) is still open, and on `main` the SPA still hardcodes `/api` (Vite proxy only). Entrega 2 used a **public Render Blueprint** (`render.yaml` + `docs/deploy-entrega2-demo.md`). Final delivery must match that Render approach while closing privacy + academic documentation gaps.

## Why this slice

| Candidate | Decision |
|-----------|----------|
| **US-PRIV-001** | **Selected** — closes R-02 control gap |
| **US-OPS-SPA-HOST** + **DEPLOY-01** | **Selected** — D2 locked: **Render** public deploy like Entrega 2 |
| Phase 3 privacy + FR/NFR fill | **Selected** — academic DoD blocker |
| R4 mobile / JWT harden / IdP | **Cut** — see final-delivery-plan Track C |
| Full ARCO automation | **Out of scope** — document manual process only |

## Planning decisions (locked)

1. **D1:** Anonymize at **egress** (before `complete_claude_or_openai`); keep DB UUIDs locally.
2. **D2:** Public **Render Blueprint** per `docs/deploy-final-demo.md` / Entrega 2 (not local-demo-only; not Hetzner/Pages for this delivery).
3. **D3:** Mobile out of scope for this window.
4. **D4:** One clinician feedback form or documented pending clinical alignment.
5. Single anonymization choke point in `RAGPipeline.generate_plan` preferred.
6. TDD mandatory for US-PRIV-001 and US-OPS-SPA-HOST.
7. Docs land in the same PR series as code (Phase 3 + backlog status).

## Ready-for-dev checklist

- [x] Story IDs, AC, test intent in [`04-feature-specs-and-user-stories.md`](04-feature-specs-and-user-stories.md)
- [x] Sequence and cut list in [`final-delivery-plan.md`](final-delivery-plan.md)
- [x] User confirmed D1–D4 (D2 = public deploy)
- [x] Development starts Red tests for scrubber + API base URL helper
- [x] Owner confirmed `ALLOW_DEV_AUTH=true` for Render demo

## Handoff

- Backlog item ID: **US-PRIV-001**, **US-OPS-SPA-HOST** (+ DEPLOY-01 / DOC / EVAL / DEMO companions)
- Scope: Final delivery plan §3 Track A
- Acceptance criteria: story ACs + final DoD checklist §8 in plan
- Test evidence: pending Development/QA
- Risks/issues: deploy DNS/TLS/CORS; over-scrubbing clinical text; residual legal Q1
- Next owner: **Development Agent**
