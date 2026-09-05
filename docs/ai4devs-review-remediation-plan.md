# AI4devs final review — remediation backlog plan

| Field | Value |
|-------|--------|
| Owner | Planning Agent |
| Audience | Solo developer / product owner (Andrés) |
| Source | AI4devs · LIDR · Revisión de entrega final (19 Aug 2026) — *Aprobado con notas* |
| Repo | github.com/andresviverosw/holisticare |
| Public demo | holisticare-frontend.onrender.com / holisticare-api.onrender.com |
| Status | **Planning complete** — ready for D1–D5 confirmation, then Development |
| Execution plan | [`sprint-17.md`](sprint-17.md) |

## 1. Tutor verdict (compressed)

HolistiCare is among the best-documented and most disciplined projects in the cohort (234 backend tests, blocking security CI, Playwright, changelog↔user-story traceability, real RAG governance). The urgent work is **not** new product features:

1. Authorization gap on clinical GETs (code).
2. Public demo down due to DB/schema + lack of active monitoring (ops).

Local code works; public infrastructure and one RBAC inconsistency are the blockers to close the loop on what the project already promised.

## 2. Feedback → backlog map

| # | Tutor finding | Severity | Backlog ID | Wave | Type |
|---|---------------|----------|------------|------|------|
| F1 | Four clinical GETs respond 200 without `Authorization` | **P0 / BUG** | **US-SEC-RBAC-001** | 1 | Code + tests |
| F2 | No test that a patient (or anonymous caller) cannot read another patient’s intake | **P0** | *(folded into US-SEC-RBAC-001)* | 1 | Tests |
| F3 | Public demo: all DB-backed endpoints 500; CORS symptom masks DB cause | **P0** | **US-OPS-DEMO-REPAIR-001** | 2 | Ops |
| F4 | `/health` does not detect DB failure; smoke insufficient for continuous detection | **P0/P1** | **US-OPS-HEALTH-001**, **US-OPS-MONITOR-001** | 2–3 | Code + Ops |
| F5 | No Alembic; `init.sql` + manual patches → likely root cause after volume recreate | **P1** | **US-OPS-SCHEMA-001** | 3 | Infra |
| F6 | README quickstart `data/mock` missing (only `ci_smoke` / `pilot` / `synthetic`) | **P1** | **DOC-QUICKSTART-001** | 4 | Docs |
| F7 | `docs/06-deployment-and-ops-runbook.md` mostly empty template | **P1** | **DOC-OPS-FILL-001** | 4 | Docs |
| F8 | Product `SYSTEM_PROMPT` not excerpted in `prompts.md` | **P2** (nice) | **DOC-PROMPTS-001** | 4 | Docs |
| F9 | JWT in `localStorage` XSS residual risk | **P2** (next iter) | **US-SEC-JWT-COOKIE-001** | 5 | Deferred |
| F10 | RAG E2E not verified by tutor (policy — no reviewer API keys) | Info | No story | — | Optional self-demo with own keys |
| — | **Planning discovery:** `GET /rag/plan/{id}/sources` also lacks `require_roles` | **P0** | Include in **US-SEC-RBAC-001** | 1 | Code + tests |

### Strengths to preserve (do not regress)

- NOM-024: every AI plan stays `pending_review` / `requires_practitioner_review: true`.
- LLM egress anonymization (US-PRIV-001) fail-closed path.
- Blocking `pip-audit` / `npm audit` / bandit CI gate.
- Changelog ↔ user-story traceability.
- Parameterized chunk SQL and privacy controls.

## 3. Current code evidence (planning time)

Confirmed in `backend/app/api/rag.py` — handlers **without** `Depends(require_roles(...))`:

- `get_intake` — `GET /rag/intake/{patient_id}`
- `get_intake_risk_flags` — `GET /rag/intake/{patient_id}/risk-flags`
- `list_chunks` — `GET /rag/chunks`
- `get_plan` — `GET /rag/plan/{plan_id}`
- `get_plan_sources` — `GET /rag/plan/{plan_id}/sources` *(extra vs tutor list)*

`GET /health` in `backend/app/main.py` returns process OK only.

`backend/scripts/smoke_public_demo.py` checks health + SPA + CORS + dev-login — **no DB-backed clinical read**.

On-disk data dirs under `backend/data/`: `ci_smoke`, `pilot`, `synthetic` — **no `mock`**.

## 4. Story definitions (ready-for-dev)

### US-SEC-RBAC-001 — Close clinical GET authorization gaps

- **Epic:** Security / Auth
- **As a** clinic operator
- **I want** every clinical data GET to require clinician/admin JWT
- **So that** intake, plans, and corpus chunks are not anonymously readable on the public API
- **Priority:** Must | **Estimate:** S

**Acceptance criteria**

- [ ] AC-01: Unauthenticated requests to intake, risk-flags, plan, plan sources, and chunks return **401**.
- [ ] AC-02: Authenticated `patient` role cannot read those endpoints (**403**), except any future patient-scoped route explicitly designed otherwise (none today for these five).
- [ ] AC-03: Authenticated `clinician` or `admin` retains successful access (**200** / **404** as today).
- [ ] AC-04: Implementation uses the existing `require_roles(...)` dependency (DRY with the rest of `rag.py`).
- [ ] AC-05: Security audit TODO notes the closed gap; changelog entry under Security.

**Test intent (TDD — Red first)**

- Unit/API: parametrized tests — no header → 401; patient JWT → 403; clinician JWT → 200 (or 404 with stubbed empty DB).
- Regression: existing plan-generate / diary auth tests remain green.
- Optional e2e: one Playwright assertion that Dashboard still loads intake after login (auth regression).

**Implementation notes**

- File: `backend/app/api/rag.py` only for guards; no service-layer change expected.
- Watch for scripts/docs that curl these endpoints without a token — update them in the same PR.

---

### US-OPS-HEALTH-001 — Database readiness probe

- **Epic:** Ops
- **As an** operator
- **I want** a probe that fails when Postgres is unreachable or schema-critical
- **So that** CD smoke and monitors detect the failure mode the tutor saw (process up, data down)
- **Priority:** Must | **Estimate:** S–M

**Acceptance criteria**

- [ ] AC-01: Readiness check executes a cheap DB round-trip (e.g. `SELECT 1`).
- [ ] AC-02: When DB is down, readiness returns non-200 (or `status: fail` with explicit contract documented for CD).
- [ ] AC-03: Process liveness remains usable for Render cold-start retries (do not break existing CD health retries without updating smoke).
- [ ] AC-04: Tests cover success and failure paths (mock engine/session).

**Test intent:** unit/integration with mocked DB failure; smoke helper updated to call readiness.

---

### US-OPS-DEMO-REPAIR-001 — Restore public Render demo data plane

- **Epic:** Ops / Deploy
- **As a** tutor or reviewer
- **I want** the public demo’s DB-backed flows to work again
- **So that** evaluation against the live URL matches local behavior
- **Priority:** Must | **Estimate:** M (ops, not product code)

**Acceptance criteria**

- [ ] AC-01: Schema applied on Render Postgres (`init.sql` + ordered patches, or migration runner from US-OPS-SCHEMA-001 if already landed).
- [ ] AC-02: Clinician seed + synthetic dataset seed applied (or documented restore script run).
- [ ] AC-03: Authenticated curl to intake / risk-flags / diary succeeds against public API.
- [ ] AC-04: README or deploy runbook records the restore procedure and last verification date.
- [ ] AC-05: CORS “errors” in browser disappear once underlying 500s are gone (verify from SPA origin).

**Test intent:** manual ops checklist + enhanced smoke (US-OPS-MONITOR-001) as automated gate.

**Risk:** Requires Render dashboard/DB credentials; cannot be fully automated from CI without those secrets.

---

### US-OPS-MONITOR-001 — Continuous demo smoke with DB signal

- **Epic:** Ops
- **As an** operator
- **I want** post-deploy and periodic smoke that exercises a DB-backed authenticated path
- **So that** a free-tier Postgres reset cannot leave the demo silently broken for weeks
- **Priority:** Should (strongly recommended) | **Estimate:** S–M

**Acceptance criteria**

- [ ] AC-01: `smoke_public_demo.py` fails if readiness/DB check fails (even when `/health` is 200).
- [ ] AC-02: Smoke performs at least one authenticated clinical GET (or dedicated ready endpoint that implies schema).
- [ ] AC-03: Scheduled check (GitHub Actions `schedule` and/or Render cron) documented; failure visible in Actions.
- [ ] AC-04: CD workflow uses the strengthened smoke.

**Test intent:** extend `test_public_demo_smoke.py` for new check helpers; cron workflow dry-run on PR optional.

---

### US-OPS-SCHEMA-001 — Versioned database migrations

- **Epic:** Ops / Database
- **As an** operator
- **I want** a single, ordered, repeatable schema apply path
- **So that** recreating Render Postgres does not leave the API in “500 on every data route”
- **Priority:** Should | **Estimate:** M–L

**Acceptance criteria**

- [ ] AC-01: Fresh empty Postgres reaches current schema via one documented command (Alembic upgrade or `scripts/migrate.sh`).
- [ ] AC-02: `infra/init.sql` + patch files are either generated from migrations or explicitly superseded (one source of truth).
- [ ] AC-03: Docker Compose and Render bootstrap docs point at the same path.
- [ ] AC-04: At least one CI job validates migrations against Postgres service (or documents why Compose init remains the CI path).

**Design note (D3):** Prefer Alembic with an initial revision matching current schema; keep `init.sql` only if generated or clearly “legacy bootstrap.” Avoid dual-writing forever.

---

### DOC-QUICKSTART-001 — Fix broken ingest quickstart paths

- **Priority:** Should | **Estimate:** S

**Acceptance criteria**

- [ ] AC-01: README ingest example uses an existing directory (`data/ci_smoke`, `data/pilot`, or `data/synthetic` guidance) or states that `data/mock` is local-only and gitignored.
- [ ] AC-02: `docs/setup.md` examples aligned.
- [ ] AC-03: Running the documented happy-path command no longer returns 400 for “missing source dir” on a clean clone (for the path chosen).

---

### DOC-OPS-FILL-001 — Complete deployment runbook

- **Priority:** Should | **Estimate:** M

**Acceptance criteria**

- [ ] AC-01: Environment table filled (local Compose, prod Compose, Render).
- [ ] AC-02: Checklists for deploy, schema/seed, CORS, `ALLOW_DEV_AUTH`, smoke, and rollback are concrete commands — not empty boxes.
- [ ] AC-03: Cross-links to `deploy-final-demo.md`, `render.yaml`, and Sprint 17 ops stories.

---

### DOC-PROMPTS-001 — Excerpt product prompts for tutor readability

- **Priority:** Could | **Estimate:** S

**Acceptance criteria**

- [ ] AC-01: `prompts.md` includes a dated excerpt (or verbatim block) of generator `SYSTEM_PROMPT` and query-builder product prompts with file:symbol pointers.
- [ ] AC-02: Note remains: code is source of truth; excerpt may lag — link to constants.

---

### US-SEC-JWT-COOKIE-001 — httpOnly cookie session (deferred)

- **Priority:** Could / next iteration | **Estimate:** L
- **Status:** Deferred (Wave 5)

Migrate SPA token storage from `localStorage` to httpOnly Secure cookies with an explicit CSRF strategy. Remains residual risk documented in `09-security-audit-and-todos.md` until scheduled.

## 5. Dependency graph

```text
US-SEC-RBAC-001 ──────────────► (unblock trust / security DoD)
        │
US-OPS-HEALTH-001 ──► US-OPS-MONITOR-001 ──► (cron + CD)
        │                      ▲
US-OPS-DEMO-REPAIR-001 ────────┘  (needs health/smoke to stay fixed)
        │
US-OPS-SCHEMA-001 ──► reduces recurrence of DEMO-REPAIR

DOC-* stories parallel after Wave 1 (no code dependency)
US-SEC-JWT-COOKIE-001 independent, deferred
```

## 6. Release slice proposal

| Slice | Ship when | Includes |
|-------|-----------|----------|
| **17a Security hotfix** | ASAP | US-SEC-RBAC-001 only |
| **17b Demo pulse** | Right after 17a | US-OPS-HEALTH-001 + US-OPS-DEMO-REPAIR-001 |
| **17c Hardening** | Next | US-OPS-MONITOR-001 + US-OPS-SCHEMA-001 |
| **17d Docs polish** | Parallel/anytime | DOC-QUICKSTART-001, DOC-OPS-FILL-001, DOC-PROMPTS-001 |
| **18+** | Later | US-SEC-JWT-COOKIE-001, US-PRIV-002, US-MOB-* |

## 7. QA focus for this program

- **Blocking:** RBAC matrix tests; readiness failure mode; public smoke with DB signal.
- **Non-blocking:** Prompt excerpt completeness; runbook prose quality.
- **Regression:** Full `pytest -q`; frontend unit; Playwright smoke that clinician login still loads dashboard data.
- **Out of scope for tutor gap:** New RAG quality metrics automation (already honestly disclosed in eval report).

## 8. Risks

| Risk | Mitigation |
|------|------------|
| Scripts/Postman collections assume open GETs | Grep repo for unauthenticated curls; update in RBAC PR |
| Render free Postgres suspend/reset again | Schema bootstrap + scheduled smoke |
| Alembic vs `init.sql` dual source of truth | Pick one canonical path in D3 before coding US-OPS-SCHEMA-001 |
| Tightening auth breaks demo if SPA forgot tokens on those calls | SPA already sends JWT via `api.js`; verify with e2e |
| DEMO-REPAIR blocked without Render access | Document exact steps for human operator; agent prepares scripts/docs |

## 9. Handoff

- Backlog item ID: **Sprint 17 / US-SEC-RBAC-001** first
- Scope: Remediation only — no new clinical features
- Acceptance criteria: §4 stories
- Test evidence: pending
- Risks/issues: §8; confirm D1–D5 in [`sprint-17.md`](sprint-17.md)
- Next owner: **User** (confirm decisions) → **Development Agent** (Wave 1 TDD)
