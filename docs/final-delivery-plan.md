# Final Delivery Plan — AI4devs Capstone (HolistiCare)

| Field | Value |
|-------|--------|
| Owner | Planning Agent |
| Audience | Solo developer / product owner (Andrés) |
| Horizon | Short final-submission window (aggressive scope control) |
| Status | **Ready for confirmation** — execute after locking open decisions below |
| Related | MVP DoD in [`01-requirements-and-domain-research.md`](01-requirements-and-domain-research.md) §11; backlog in [`04-feature-specs-and-user-stories.md`](04-feature-specs-and-user-stories.md) |

## 1. Verdict on current state

**Product MVP (code) is largely done.** R1 through R3 product stories and Sprints 1–15 are complete, including clinician/patient auth and production Compose. The remaining risk for the master’s submission is **not feature breadth** — it is **academic closeout, privacy evidence (anonymization), demo package, and tutor-facing documentation completeness**.

| Area | Status | Gap vs DoD |
|------|--------|------------|
| 6 MVP features e2e (intake → plan → approve → sessions → diary → analytics) | **Done** (Sprint 11 UI + APIs) | Keep regression green for submission |
| NOM-024 practitioner gate | **Done** (`pending_review`, no auto-activation) | Keep as non-negotiable demo talking point |
| Prediction + memory bank (R3) | **Done** | Optional in live demo; cite as stretch |
| Prod auth + Compose (R2+) | **Done** (Sprints 13–15) | SPA host still open if public URL required |
| Phase 1 FR/NFR tables | **Stub / empty** | Must fill for academic DoD item 5 |
| Phase 3 data dictionary & privacy | **Stub** | Must complete; anchors anonymization story |
| RAG golden-eval thresholds (hit≥0.80, faith≥0.85) | Partial (AI quality smoke exists) | Need a short eval report artifact |
| Practitioner collaborator feedback | Pilot GO/NO-GO still `IN_PROGRESS` | Need documented feedback or explicit synthetic-demo waiver |
| Patient anonymization before LLM egress | **Missing** (R-02 / Q1) | **New Must for this delivery** (US-PRIV-001) |
| R4 mobile (`US-MOB-*`) | Planned | **Cut** from final window |
| `US-OPS-SPA-HOST`, JWT harden, IdP | Planned | **Cut** unless tutor requires public URL |

## 2. Open decisions (confirm before build)

| # | Decision | Recommended default | Why |
|---|----------|---------------------|-----|
| D1 | Anonymization scope for US-PRIV-001 | **LLM egress scrub + docs** (not full ARCO portal) | Closes R-02 for the thesis; ARCO UI is multi-sprint |
| D2 | Public deploy vs local demo | **Local Docker + recorded walkthrough** unless tutor demands URL | SPA host is follow-on; Compose prod overlay already exists |
| D3 | R4 mobile in submission | **Out of scope / future work** | Should/R4; consumes the whole remaining window |
| D4 | Clinician sign-off evidence | Capture **one structured feedback form** (or document “synthetic-only demo + pending clinical alignment”) | DoD item 6; do not block code on a late co-design |

## 3. Final backlog slice (ordered)

Execute **only** tracks A → D in order. Everything else stays backlog.

### Track A — Capstone must-ship (blocking)

| ID | Work | Priority | Owner role | Exit criteria |
|----|------|----------|------------|---------------|
| **US-PRIV-001** | Patient anonymization / pseudonymization before external LLM calls | **Must** | Dev → QA | Failing tests first; no `patient_id` or contact-like PII in outbound LLM prompts; phase-3 privacy section updated |
| **DOC-CLOSE-01** | Complete Phase 1 §7 FR/NFR from implemented system | **Must** | Planning | Tables filled; MoSCoW aligned with backlog |
| **DOC-CLOSE-02** | Complete Phase 3 data dictionary + privacy framework (LFPDPPP / NOM-024 mapping) | **Must** | Planning (+ Dev notes) | Entities/fields, sensitivity classes, anonymization control, ARCO *policy* (manual process OK) |
| **DOC-CLOSE-03** | Mark phases 1–6 / guides consistent; fill owners/dates/status | **Must** | Planning | Checklists honest; cross-links valid |
| **EVAL-01** | Short RAG evaluation / AI quality report for thesis | **Must** | QA | Document smoke metrics + known limits; link `ai_quality_smoke` + pilot cases |
| **DEMO-01** | Submission demo package | **Must** | Dev/QA | `demo-smoke-checklist` green + scripted walkthrough notes (+ optional short recording) |
| **FEEDBACK-01** | Clinician feedback artifact | **Must** | Planning | Completed [`pilot-clinician-feedback-form.md`](pilot-clinician-feedback-form.md) **or** explicit “pending clinical alignment” appendix |

### Track B — Strongly recommended if capacity remains

| ID | Work | Priority | Notes |
|----|------|----------|-------|
| **US-PRIV-002** | Harden memory-bank de-identification (free-text scrub in snapshots) | Should | Extends Sprint 10 sanitize beyond stripping `patient_id` |
| **PILOT-GO** | Close pilot GO/NO-GO with evidence pointers | Should | Mostly documentation if rehearsals already green |
| **SYNTH-01** | Package existing pilot/synthetic cases as “dataset v1” appendix | Should | Do not regenerate 80–100 profiles unless required |

### Track C — Explicitly deferred (do not start)

- `US-MOB-001` … `US-MOB-003` (R4)
- `US-OPS-SPA-HOST` (Cloudflare Pages + `VITE_API_BASE_URL`)
- JWT harden / refresh tokens / password reset / IdP / MFA
- Admin audit UI (`US-INT-003` UI)
- OTP email/SMS diary invites
- Full automated ARCO cancellation workflow
- Production monitoring / Sentry / formal SLOs

### Track D — Submission packaging (last day)

1. Freeze branch / tag `capstone-final` (or equivalent).
2. Update `CHANGELOG.md` + `memory-bank/progress.md` + `active-context.md`.
3. README “how to demo in 15 minutes” path (point to `docs/demo-smoke-checklist.md` + `docs/quickstart-clinician.md`).
4. Thesis appendix index: phases 01–06, privacy, eval report, demo evidence, feedback form.

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

## 5. Documentation closeout checklist (Track A)

Map to Phase 1 DoD item 5 (“documentación académica … entregada”).

| Doc | Action |
|-----|--------|
| `01-requirements-and-domain-research.md` | Fill §7 FR/NFR from implemented features; update deliverable statuses; mark complete where honest |
| `02-system-architecture.md` | Add ADR for egress anonymization; close privacy checklist items |
| `03-data-dictionary-and-privacy-framework.md` | **Primary gap** — entities from ORM/schemas, sensitivity table, anonymization control, ARCO process (manual OK) |
| `04-feature-specs-and-user-stories.md` | Add US-PRIV-001 (+ optional US-PRIV-002); release slice R-final |
| `05-test-plan.md` | Add privacy/anonymization test row; point to new tests |
| `06-deployment-and-ops-runbook.md` | Note anonymization is app-layer; DPA checklist remains ops |
| `EVAL` short report | New `docs/rag-evaluation-report.md` (metrics + limits + commands) |
| Guides 07–10 | Spot-fix only; no redesign |

## 6. Suggested execution sequence (no calendar estimates)

Work is ordered by dependency and submission risk, not by day counts.

```
1) Confirm D1–D4 (this plan)
2) US-PRIV-001 — TDD anonymizer + pipeline wire-up + QA
3) DOC-CLOSE-02 (Phase 3) in parallel with remaining US-PRIV-001 polish
4) DOC-CLOSE-01 + DOC-CLOSE-03 (FR/NFR + consistency)
5) EVAL-01 report from existing smoke/pilot artifacts
6) DEMO-01 rehearsal + FEEDBACK-01 artifact
7) Optional US-PRIV-002 / PILOT-GO if still green
8) Tag + packaging (Track D)
```

### Agent handoffs

| Step | Owner | Handoff must include |
|------|-------|----------------------|
| Plan lock | Planning | D1–D4 answers; this doc status → Approved |
| US-PRIV-001 impl | Development | Story ID, AC, test evidence (pytest) |
| Privacy/docs | Planning (+ Dev) | Phase 3 + backlog status |
| Quality gate | QA | Pass/fail on anonymization + regression + demo smoke |
| Defects | Debugging | Only if QA fails |

## 7. Definition of done — final master’s delivery

Aligned with Phase 1 §11, tightened for the remaining window:

1. [ ] Six MVP features runnable e2e on synthetic data (regression suite green).
2. [ ] AI plans always `requires_practitioner_review: true` / `pending_review` (demo + tests).
3. [ ] **US-PRIV-001** merged with tests proving LLM egress scrub.
4. [ ] Phase docs 01–06 internally consistent enough for tutor review (esp. §7 FR/NFR + Phase 3 privacy).
5. [ ] Short RAG/AI quality report attached.
6. [ ] Demo package reproducible from README/quickstart.
7. [ ] Clinician feedback form **or** documented waiver for synthetic-only validation.
8. [ ] Explicit out-of-scope list (mobile, SPA host, full ARCO automation) acknowledged in submission notes.

## 8. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep (mobile / SPA / IdP) | Miss documentation + privacy | Hard cut list in Track C |
| Over-scrubbing harms clinical summary quality | Worse RAG plans | Scrub identifiers only; keep clinical fields; golden smoke after change |
| Tutor expects live URL | Demo friction | Prepare Compose + Pages notes; fallback to localhost recording |
| Legal Q1 unresolved | Cannot claim full LFPDPPP compliance | Document control + stated residual legal risk; synthetic-only for now |
| Phase 3 under-specified | Academic reject | Prioritize dictionary + privacy mapping over new features |

## 9. Immediate next action

**Planning → user confirmation on D1–D4**, then Development starts **US-PRIV-001** under TDD while Planning drafts Phase 3 from ORM/schemas.
