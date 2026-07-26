# Final Delivery Plan — AI4devs Capstone (HolistiCare)

| Field | Value |
|-------|--------|
| Owner | Planning Agent |
| Audience | Solo developer / product owner (Andrés) |
| Horizon | Short final-submission window (aggressive scope control) |
| Status | **Approved** — decisions D1–D4 locked 2026-07-25 |
| Related | MVP DoD in [`01-requirements-and-domain-research.md`](01-requirements-and-domain-research.md) §11; backlog in [`04-feature-specs-and-user-stories.md`](04-feature-specs-and-user-stories.md); deploy path in [`deploy-final-demo.md`](deploy-final-demo.md) (Render; same as Entrega 2) |

## 1. Verdict on current state

**Product MVP (code) is largely done.** R1 through R3 product stories and Sprints 1–15 are complete, including clinician/patient auth and production Compose. The remaining risk for the master’s submission is **academic closeout, privacy evidence (anonymization), public deployment (same approach as the second delivery), and tutor-facing documentation**.

| Area | Status | Gap vs DoD |
|------|--------|------------|
| 6 MVP features e2e (intake → plan → approve → sessions → diary → analytics) | **Done** (Sprint 11 UI + APIs) | Keep regression green for submission |
| NOM-024 practitioner gate | **Done** (`pending_review`, no auto-activation) | Keep as non-negotiable demo talking point |
| Prediction + memory bank (R3) | **Done** | Optional in live demo; cite as stretch |
| Prod auth + Compose (R2+) | **Done** (Sprints 13–15) | Need live host + SPA on Pages |
| Phase 1 FR/NFR tables | **Stub / empty** | Must fill for academic DoD item 5 |
| Phase 3 data dictionary & privacy | **Stub** | Must complete; anchors anonymization story |
| RAG golden-eval thresholds (hit≥0.80, faith≥0.85) | Partial (AI quality smoke exists) | Need a short eval report artifact |
| Practitioner collaborator feedback | Pilot GO/NO-GO still `IN_PROGRESS` | Need documented feedback or explicit synthetic-demo waiver |
| Patient anonymization before LLM egress | **Missing** (R-02 / Q1) | **Must** (US-PRIV-001) |
| Public Render deploy (API + SPA) | Entrega 2 path exists on `feature-entrega2-AVW`; not on `main` | **Must** (US-OPS-SPA-HOST + DEPLOY-01 on Render) |
| R4 mobile (`US-MOB-*`) | Planned | **Cut** from final window |
| JWT harden, IdP, password reset | Planned | **Cut** from final window |

## 2. Decisions (locked 2026-07-25)

| # | Decision | Locked choice | Notes |
|---|----------|---------------|-------|
| D1 | Anonymization scope for US-PRIV-001 | **LLM egress scrub + docs** (not full ARCO portal) | Closes R-02 for the thesis; ARCO UI remains deferred |
| D2 | Public deploy vs local-only demo | **Public Render Blueprint** (same approach as Entrega 2) | Render Postgres + Docker API + Static Site SPA; see [`deploy-final-demo.md`](deploy-final-demo.md). Hetzner/Pages quickstart stays post-pilot only. |
| D3 | R4 mobile in submission | **Out of scope / future work** | Should/R4 |
| D4 | Clinician sign-off evidence | **One structured feedback form** or documented “pending clinical alignment” | DoD item 6; do not block code on a late co-design |

### D2 topology (mandatory) — Render (Entrega 2 parity)

Follow [`deploy-final-demo.md`](deploy-final-demo.md) / [`deploy-entrega2-demo.md`](deploy-entrega2-demo.md):

- **Platform:** Render Blueprint from root [`render.yaml`](../render.yaml)
- **DB:** Render PostgreSQL 16 (Neon fallback only if `vector` unavailable)
- **API:** Docker web service `holisticare-api` (`backend/Dockerfile`)
- **SPA:** Render Static Site with `VITE_API_BASE_URL` → API origin
- **Auth (demo default):** `ALLOW_DEV_AUTH=true` for TA “Entrar desarrollo”, plus seeded clinician login documented
- **Evidence:** public `*.onrender.com` (or custom) frontend + API `/health` in submission notes

`docker-compose.prod.yml` / Hetzner+Cloudflare remain **alternate** ops paths, not the capstone demo host.

## 3. Final backlog slice (ordered)

Execute **only** tracks A → D in order. Everything else stays backlog.

### Track A — Capstone must-ship (blocking)

| ID | Work | Priority | Owner role | Exit criteria |
|----|------|----------|------------|---------------|
| **US-PRIV-001** | Patient anonymization / pseudonymization before external LLM calls | **Must** | Dev → QA | Failing tests first; no `patient_id` or contact-like PII in outbound LLM prompts; phase-3 privacy section updated |
| **US-OPS-SPA-HOST** | Configurable SPA API base URL + Pages build contract | **Must** | Dev → QA | `VITE_API_BASE_URL` used in production build; `/api` remains valid for Vite proxy in local/dev; unit/contract tests green |
| **DEPLOY-01** | Live public deploy on **Render** (Entrega 2 approach) | **Must** | Dev/Ops → QA | Public API `/health` 200; SPA loads against API; demo login works; CORS allows Static Site origin; schema + seed + corpus ingest done; URLs in README |
| **DOC-CLOSE-01** | Complete Phase 1 §7 FR/NFR from implemented system | **Must** | Planning | Tables filled; MoSCoW aligned with backlog |
| **DOC-CLOSE-02** | Complete Phase 3 data dictionary + privacy framework (LFPDPPP / NOM-024 mapping) | **Must** | Planning (+ Dev notes) | Entities/fields, sensitivity classes, anonymization control, ARCO *policy* (manual process OK) |
| **DOC-CLOSE-03** | Mark phases 1–6 / guides consistent; fill owners/dates/status | **Must** | Planning | Checklists honest; cross-links valid |
| **EVAL-01** | Short RAG evaluation / AI quality report for thesis | **Must** | QA | Document smoke metrics + known limits; link `ai_quality_smoke` + pilot cases |
| **DEMO-01** | Submission demo package **on public URLs** | **Must** | Dev/QA | Walkthrough against live app/API (+ optional recording); local `demo-smoke-checklist` still green as CI gate |
| **FEEDBACK-01** | Clinician feedback artifact | **Must** | Planning | Completed [`pilot-clinician-feedback-form.md`](pilot-clinician-feedback-form.md) **or** explicit “pending clinical alignment” appendix |

### Track B — Strongly recommended if capacity remains

| ID | Work | Priority | Notes |
|----|------|----------|-------|
| **US-PRIV-002** | Harden memory-bank de-identification (free-text scrub in snapshots) | Should | Extends Sprint 10 sanitize beyond stripping `patient_id` |
| **PILOT-GO** | Close pilot GO/NO-GO with evidence pointers | Should | Prefer closing after public deploy smoke |
| **SYNTH-01** | End-to-end synthetic dataset v1 (intakes, plans, sessions, diaries, KPI/plateau/recovery cohorts, memory bank) + seed CLI | Should → **Must for demo richness** | Default 32 patients (8×4); optional `--variants 10` → 80. See [`synthetic-dataset-v1.md`](synthetic-dataset-v1.md) |

### Track C — Explicitly deferred (do not start)

- `US-MOB-001` … `US-MOB-003` (R4)
- JWT harden / refresh tokens / password reset / IdP / MFA
- Admin audit UI (`US-INT-003` UI)
- OTP email/SMS diary invites
- Full automated ARCO cancellation workflow
- Production monitoring / Sentry / formal SLOs (optional nicety; not blocking if UptimeRobot free probe already noted)

### Track D — Submission packaging (last day)

1. Freeze branch / tag `capstone-final` (or equivalent).
2. Update `CHANGELOG.md` + `memory-bank/progress.md` + `active-context.md`.
3. README “how to demo” path includes **public URLs** + fallback local quickstart.
4. Thesis appendix index: phases 01–06, privacy, eval report, **deploy evidence**, feedback form.

## 4. Story: US-PRIV-001 — Patient anonymization before LLM egress

### Problem

Phase 1 risk **R-02** and open question **Q1** require anonymization/pseudonymization before Anthropic/OpenAI calls. Today:

- `QueryBuilder.build_clinical_summary` sends the **raw intake JSON** to the LLM.
- `PlanGenerator.generate` embeds **`patient_id`** in the user message.
- Memory-bank sanitize strips identifiers from templates but does **not** cover LLM egress.

Intake schema is already fairly minimized (no name/email fields), but free-text (`chief_complaint`, `psychosocial_summary`, notes) and UUIDs can still leak identifiers.

### User story

| Field | Value |
|-------|--------|
| Story ID | **US-PRIV-001** |
| Epic | Privacy / compliance |
| As a | Clinic operator / product owner |
| I want | patient-identifying data removed or tokenized before any external LLM call |
| So that | HolistiCare can argue LFPDPPP-aligned minimization for international model APIs and satisfy capstone privacy claims |
| Priority | **Must** (final delivery) |
| Estimate | M |
| Status | **Ready for dev** |

### Acceptance criteria

- Given intake JSON that contains `patient_id` and optional contact-like strings in free text, when a clinical summary is built, then the outbound LLM user payload contains **no** raw `patient_id` and **no** matched email/phone patterns.
- Given plan generation, when the generator calls the LLM, then the prompt uses a **local placeholder** (e.g. `PATIENT_TOKEN`) and the persisted plan still stores the real `patient_id` assigned by the service layer.
- Given anonymization fails validation, when generation is attempted, then the API returns a clear error and does **not** call the external LLM.
- Given unit tests with fixtures containing PII-like strings, when the scrubber runs, then tests assert redaction (Red → Green).
- Given docs, when Phase 3 privacy framework is read, then US-PRIV-001 is mapped as a control under LFPDPPP / international transfer mitigation (with explicit “legal advice still required for real PHI” caveat).

### Functional design (minimal)

1. New pure module e.g. `app/services/patient_anonymizer.py` (or `app/rag/privacy/anonymize_intake.py`):
   - Project intake → **clinical-only** dict (drop unknown keys; keep conditions/goals/contraindications/etc.).
   - Redact email/phone/UUID-looking tokens in free-text fields.
   - Never pass `patient_id` into LLM chat helpers.
2. Wire into `QueryBuilder` and `PlanGenerator` (single choke point preferred: sanitize once in `RAGPipeline.generate_plan` before phase 1).
3. Keep local DB rows fully identified (UUID primary keys) — this is **pseudonymization at the egress boundary**, not deletion of the clinical record.
4. Optional log flag `anonymization_applied: true` in retrieval/generation metadata (no raw PII in logs).

### Test intent

- Unit: scrubber fixtures (email, phone MX/US-ish, UUID, name-like lines).
- Integration: mock `complete_claude_or_openai` and assert call args omit identifiers.
- Regression: existing plan-generate tests still pass; persisted `patient_id` unchanged.

### Out of scope for US-PRIV-001

- Patient-facing privacy notice UI / consent capture screens.
- Automated ARCO deletion across all tables.
- Vendor DPA signatures (document checklist only).
- Changing embedding corpus (documents are not patient PHI).

### Follow-on (US-PRIV-002, if time)

- Apply the same free-text scrub when saving memory-bank snapshots.
- Document retention/deletion runbook steps for admin.

## 5. Story: US-OPS-SPA-HOST — SPA API base URL for Render Static Site

### Problem

On `main`, `frontend/src/services/api.js` hardcodes `baseURL: "/api"` (Vite proxy). That breaks on **Render Static Site** (same failure mode as Entrega 2 before the fix). Entrega 2 already solved this on `feature-entrega2-AVW` with `VITE_API_BASE_URL`; final delivery must reintroduce that on the delivery branch.

### User story

| Field | Value |
|-------|--------|
| Story ID | **US-OPS-SPA-HOST** |
| Epic | Ops |
| As a | Admin / deployer |
| I want | the SPA to call a configurable absolute API base URL in production builds |
| So that | the Render Static Site can call the Render API web service |
| Priority | **Must** (final delivery — locked D2) |
| Estimate | S–M |
| Status | **Ready for dev** |

### Acceptance criteria

- Given `VITE_API_BASE_URL` is set at build time (e.g. `https://holisticare-api.onrender.com`), when the SPA boots, then axios uses that origin (no reliance on Vite `/api` proxy).
- Given `VITE_API_BASE_URL` is unset, when running local Vite, then the client falls back to `/api` (current proxy behavior preserved).
- Given CORS on the API, when the Render Static Site origin calls the API, then browser requests succeed for login and a smoke RAG path.
- Given docs, when an operator follows [`deploy-final-demo.md`](deploy-final-demo.md), then `render.yaml`, env vars, and SPA rewrite/`_redirects` match this repo.
- Given unit/contract tests, when `api` base URL resolution is tested, then both configured and fallback modes pass.

### Companion ops story: DEPLOY-01 (Render)

Ops execution checklist (Entrega 2 parity):

1. Render Blueprint from `render.yaml` (DB + API + Static Site).
2. Apply `infra/init.sql` (+ needed patches) via External Database URL; enable `vector`.
3. Set API secrets + `CORS_ORIGINS` = Static Site URL; set SPA `VITE_API_BASE_URL` = API URL.
4. Seed clinician; ingest `data/mock`.
5. Public smoke: `/health`, SPA load, login → generate → approve/reject.
6. Record live URLs in README / submission notes (see Entrega 2 §8 pattern).

## 6. Documentation closeout checklist (Track A)

Map to Phase 1 DoD item 5 (“documentación académica … entregada”).

| Doc | Action |
|-----|--------|
| `01-requirements-and-domain-research.md` | Fill §7 FR/NFR from implemented features; update deliverable statuses; mark complete where honest |
| `02-system-architecture.md` | Add ADR for egress anonymization; close privacy checklist items |
| `03-data-dictionary-and-privacy-framework.md` | **Primary gap** — entities from ORM/schemas, sensitivity table, anonymization control, ARCO process (manual OK) |
| `04-feature-specs-and-user-stories.md` | US-PRIV-001, US-OPS-SPA-HOST; release slice R-final |
| `05-test-plan.md` | Add privacy/anonymization + SPA base URL test rows |
| `06-deployment-and-ops-runbook.md` | Point final public demo to Render (`deploy-final-demo.md`); keep Hetzner quickstart as post-pilot |
| `EVAL` short report | New `docs/rag-evaluation-report.md` (metrics + limits + commands) |
| Guides 07–10 | Spot-fix only; no redesign |

## 7. Suggested execution sequence (no calendar estimates)

Work is ordered by dependency and submission risk, not by day counts.

```
1) D1–D4 locked (done)
2) US-PRIV-001 — TDD anonymizer + pipeline wire-up + QA
3) US-OPS-SPA-HOST — VITE_API_BASE_URL + tests + Render deploy docs (`render.yaml`, `_redirects`)
4) DOC-CLOSE-02 (Phase 3) in parallel with code polish
5) DOC-CLOSE-01 + DOC-CLOSE-03 (FR/NFR + consistency)
6) DEPLOY-01 — Render Blueprint public deploy + internet smoke
7) EVAL-01 report from smoke/pilot artifacts
8) DEMO-01 on public URLs + FEEDBACK-01 artifact
9) Optional US-PRIV-002 / PILOT-GO if still green
10) Tag + packaging (Track D)
```

### Agent handoffs

| Step | Owner | Handoff must include |
|------|-------|----------------------|
| Plan lock | Planning | **Done** — D1–D4 approved |
| US-PRIV-001 + US-OPS-SPA-HOST | Development | Story IDs, AC, test evidence |
| DEPLOY-01 | Dev/Ops | Public URLs + health/login evidence |
| Privacy/docs | Planning (+ Dev) | Phase 3 + backlog status |
| Quality gate | QA | Pass/fail on anonymization + SPA base URL + public smoke + regression |
| Defects | Debugging | Only if QA fails |

## 8. Definition of done — final master’s delivery

Aligned with Phase 1 §11, tightened for the remaining window:

1. [x] Six MVP features runnable e2e on synthetic data (regression suite green).
2. [x] AI plans always `requires_practitioner_review: true` / `pending_review` (demo + tests).
3. [x] **US-PRIV-001** merged with tests proving LLM egress scrub.
4. [x] **US-OPS-SPA-HOST** merged; SPA production build targets public API.
5. [ ] **DEPLOY-01** complete: public Render app + API URLs reachable; demo login path works.
6. [x] Phase docs 01–06 internally consistent enough for tutor review (esp. §7 FR/NFR + Phase 3 privacy).
7. [x] Short RAG/AI quality report attached.
8. [ ] Demo package executed against **public** deployment (+ local smoke as CI gate).
9. [x] Clinician feedback form **or** documented waiver for synthetic-only validation.
10. [x] Explicit out-of-scope list (mobile, JWT harden/IdP, full ARCO automation) acknowledged in submission notes.

## 9. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep (mobile / IdP) | Miss docs + privacy + deploy | Hard cut list in Track C |
| Over-scrubbing harms clinical summary quality | Worse RAG plans | Scrub identifiers only; keep clinical fields; golden smoke after change |
| Public deploy blocked (Render free cold start / secrets / pgvector) | No Entrega 2 parity | Follow `deploy-final-demo.md`; Neon fallback if Render lacks `vector`; warn TA about cold start |
| CORS / Static Site misconfig | SPA cannot call API | Exact Static Site origin in `CORS_ORIGINS`; `VITE_API_BASE_URL` set at build |
| Legal Q1 unresolved | Cannot claim full LFPDPPP compliance | Document control + residual legal risk; synthetic-only for now |
| Phase 3 under-specified | Academic reject | Prioritize dictionary + privacy mapping alongside deploy |

## 10. Immediate next action

**Development Agent** starts **US-PRIV-001** (TDD) and **US-OPS-SPA-HOST** (TDD) as the next code slices. Planning drafts Phase 3 / FR-NFR in parallel. DEPLOY-01 follows once SPA base URL is mergeable.
