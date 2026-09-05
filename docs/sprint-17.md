# Sprint 17 — AI4devs tutor review remediation

## Sprint parameters

| Field | Value |
|-------|--------|
| Length | Post-capstone remediation (no new product features) |
| Primary stories | **US-SEC-RBAC-001**, **US-OPS-HEALTH-001**, **US-OPS-DEMO-REPAIR-001** |
| Companion tracks | US-OPS-MONITOR-001, US-OPS-SCHEMA-001, DOC-QUICKSTART-001, DOC-OPS-FILL-001, DOC-PROMPTS-001 |
| Deferred | **US-SEC-JWT-COOKIE-001** (httpOnly cookies — tutor “next iteration”) |
| Priority | Must (security + demo integrity) |
| Scope | Close authorization gaps, restore/observe public demo health, document ops truthfully |
| Owner | Planning → Development (TDD) → Ops → QA |
| Status | **Ready for prioritization** — planning only; code not started |
| Source | AI4devs LIDR final review (19 Aug 2026) — *Aprobado con notas* |
| Plan of record | [`ai4devs-review-remediation-plan.md`](ai4devs-review-remediation-plan.md) |

## Problem statement

The capstone was **approved with notes**. Functional product code is strong locally (tutor confirmed eight main flows end-to-end after seeding). Two gaps dominate:

1. **Authorization hole:** `GET /rag/intake/{id}`, `GET /rag/intake/{id}/risk-flags`, `GET /rag/plan/{id}`, and `GET /rag/chunks` return clinical data **without** `Depends(require_roles(...))`. Planning also found `GET /rag/plan/{id}/sources` unguarded — include it in the same fix.
2. **Public demo fragility:** Render demo returns **500** on every DB-backed endpoint; `/health` stays 200 because it never checks Postgres. Smoke passes process health + login and does not detect a broken schema/volume.

Tutor verdict: the highest-value next step is **not** a new feature — close the RBAC circle already used elsewhere, and add **database-aware health** so a silent demo outage cannot recur unnoticed.

## Why this slice

| Candidate | Decision |
|-----------|----------|
| RBAC on unguarded clinical GETs + regression tests | **Selected (P0)** — security finding; blocks trust in privacy story |
| DB readiness probe + demo repair | **Selected (P0)** — restores tutor-facing public demo |
| Continuous / scheduled smoke with a DB-backed check | **Selected (P1)** — prevents silent outage |
| Versioned schema migrations (Alembic or equivalent) | **Selected (P1)** — likely root cause of public 500 after volume recreate |
| README/docs quickstart + runbook + prompts excerpt | **Selected (P1 docs)** — academic + ops hygiene |
| JWT → httpOnly cookie | **Deferred (P2)** — tutor called “siguiente iteración” |
| New clinical features / mobile / IdP | **Out of scope** |

## Planning decisions (recommended defaults)

| # | Decision | Recommended choice | Alternatives |
|---|----------|--------------------|--------------|
| D1 | Role matrix for previously open GETs | `clinician` + `admin` for intake, risk-flags, plan, plan sources, chunks | Patient role **not** granted intake/plan/chunks (patients already have diary-scoped routes) |
| D2 | Health vs ready | Keep `GET /health` process-only; add `GET /ready` (or extend health with `db: ok\|fail`) that pings Postgres | Single endpoint is OK if SPA/CD can tolerate non-200 when DB is down |
| D3 | Schema strategy | Introduce **Alembic** (or documented `infra/migrate.sh` applying `init.sql` + patches in order) and wire Render deploy/bootstrap to it | Manual patch docs alone — weaker; does not prevent recurrence |
| D4 | Monitoring | Extend `smoke_public_demo.py` to hit one authenticated DB-backed path + schedule via GitHub Actions cron (or Render cron) | External uptime only on `/health` — insufficient |
| D5 | JWT storage | **Defer** httpOnly migration; document residual XSS risk in security audit | Full cookie+CSRF slice — larger frontend/backend change |

## Implementation order (waves)

### Wave 0 — Confirm (Ops, before code merge to production)

1. Reproduce local unauthenticated 200 on the four (five) GETs.
2. Hit public API `/health` vs a DB path; capture whether schema/seed is missing.
3. Do **not** leave production open while documenting; Wave 1 code should ship ASAP.

### Wave 1 — P0 security (Development → QA)

| ID | Work | Exit criteria |
|----|------|---------------|
| **US-SEC-RBAC-001** | Add `require_roles("clinician", "admin")` to unguarded GETs in `backend/app/api/rag.py` | Unauthenticated → **401**; wrong role → **403**; clinician/admin still **200** |
| *(tests in same story)* | TDD: failing tests first for no-auth and cross-role denial | pytest covers intake, risk-flags, plan, plan sources, chunks |

### Wave 2 — P0 demo integrity (Ops + Development)

| ID | Work | Exit criteria |
|----|------|---------------|
| **US-OPS-HEALTH-001** | DB readiness endpoint + unit/integration tests | Ready fails when DB unreachable; health process check remains for cold-start |
| **US-OPS-DEMO-REPAIR-001** | Re-apply schema (`init.sql` + patches), seed clinician + synthetic dataset on Render; verify data endpoints | Public intake/risk-flags/diary return 200 with auth; CORS no longer masks 500 |

### Wave 3 — P1 prevention (Development → Ops)

| ID | Work | Exit criteria |
|----|------|---------------|
| **US-OPS-MONITOR-001** | Smoke asserts ready/DB path; scheduled job after deploy | Broken DB fails smoke/cron; alert path documented |
| **US-OPS-SCHEMA-001** | Versioned migrations replace ad-hoc patch memory | Fresh DB bootstrap is one command; Render uses same path |

### Wave 4 — P1 documentation (Planning)

| ID | Work | Exit criteria |
|----|------|---------------|
| **DOC-QUICKSTART-001** | Fix README/`docs/setup.md` ingest paths (`data/mock` → existing dirs) | Documented command succeeds or is clearly marked optional |
| **DOC-OPS-FILL-001** | Fill `docs/06-deployment-and-ops-runbook.md` from real Render/Compose practice | Env table + checklists no longer empty stubs |
| **DOC-PROMPTS-001** | Excerpt product `SYSTEM_PROMPT` (and query_builder prompts) into `prompts.md` | Tutor can read prompts without opening generator source |

### Wave 5 — P2 deferred

| ID | Work | Notes |
|----|------|-------|
| **US-SEC-JWT-COOKIE-001** | Migrate JWT from `localStorage` to httpOnly cookie (+ CSRF strategy) | Health-domain hardening; out of Sprint 17 Must |

## Ready-for-dev checklist

- [x] Feedback mapped to story IDs with AC and test intent
- [x] Priority waves and dependencies documented
- [x] Unguarded endpoints confirmed in current `rag.py` (incl. `get_plan_sources`)
- [ ] User confirms D1–D5 (or overrides) before Development starts Wave 1
- [ ] Development starts **Red** tests for RBAC before editing handlers
- [ ] Ops access to Render Postgres confirmed for Wave 2

## Handoff

- Backlog item ID: **US-SEC-RBAC-001** (first)
- Scope: Sprint 17 Wave 1 only until RBAC green
- Acceptance criteria: see story ACs in [`04-feature-specs-and-user-stories.md`](04-feature-specs-and-user-stories.md)
- Test evidence: pending Development/QA
- Risks/issues: locking endpoints may break any undocumented unauthenticated clients/scripts; public demo repair needs Render credentials; Alembic introduces migration history risk if `init.sql` and Alembic diverge
- Next owner: **Development Agent** (after D1–D5 confirmation)
