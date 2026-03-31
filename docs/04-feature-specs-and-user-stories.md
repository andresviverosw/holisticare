# Phase 4 - Feature Specs and User Stories

## Document control

- Owner:
- Contributors:
- Version:
- Last updated:
- Status: `[ ]` Draft `[~]` In progress `[x]` Complete

## 1. Objective

Translate requirements into implementable product specifications, user stories, and acceptance criteria for the MVP.

## 2. MVP epics

1. Patient intake and profile
2. AI treatment planning
3. Session logging
4. Patient diary
5. Progress analytics
6. Outcome prediction

## 2.1 Backlog governance (Planning Agent ownership)

- The Planning Agent is the owner of the MVP backlog.
- Every epic and story must have a unique ID, priority, acceptance criteria, and test intent before development starts.
- The Planning Agent is responsible for sequencing dependencies and release slicing.
- Development, QA, and Debugging roles consume and update backlog status, but backlog structure and prioritization remain owned by Planning.

## 3. Feature specification template

## Feature: `<name>`

- Problem addressed:
- Users impacted:
- Business and clinical value:
- Dependencies:
- Risks:

### Functional behavior

- Inputs:
- Processing:
- Outputs:
- Error states:

### UX notes

- Primary flow:
- Edge cases:
- Accessibility and language:

### AI behavior (if applicable)

- Prompt strategy:
- Guardrails:
- Human override path:
- Logging and traceability:

### Acceptance criteria

- [ ] AC-01
- [ ] AC-02
- [ ] AC-03

## 4. User story backlog

| Story ID | Epic | As a | I want | So that | Priority | Estimate | Status |
|----------|------|------|--------|---------|----------|----------|--------|
| US-INT-001 | Patient intake and profile | Clinician | to complete a structured intake form with required clinical fields | patient baseline data is complete and analyzable | Must | M | Done (backend API slice) |
| US-INT-002 | Patient intake and profile | Clinician | AI to flag risk indicators from intake responses | I can identify contraindications early | Must | M | Done (backend API slice) |
| US-INT-003 | Patient intake and profile | Admin | to edit and correct patient demographic/contact data with audit trail | records remain accurate and compliant | Should | S | Done (backend API slice) |
| US-PLAN-001 | AI treatment planning | Clinician | to generate a draft multi-week treatment plan from patient profile and goals | I get a high-quality starting point faster | Must | L | Done (backend Sprint 1) |
| US-PLAN-002 | AI treatment planning | Clinician | to see source citations (REF-IDs) attached to each recommendation | I can trust and verify recommendations | Must | M | Done (backend Sprint 1) |
| US-PLAN-003 | AI treatment planning | Clinician | to approve or reject AI plans before activation | treatment remains practitioner-controlled | Must | S | Done (backend Sprint 1) |
| US-SESS-001 | Session logging | Clinician | to log session interventions and observations in structured format | progress can be tracked across time | Must | M | Planned |
| US-SESS-002 | Session logging | Clinician | AI to suggest note completion from structured inputs | documentation time decreases | Should | M | Planned |
| US-DIARY-001 | Patient diary | Patient | to submit daily pain, sleep, mood, and function check-ins | my progress between sessions is visible | Must | M | Planned |
| US-DIARY-002 | Patient diary | Patient | to add optional free-text notes in Spanish | I can provide relevant context in my own words | Should | S | Planned |
| US-ANLY-001 | Progress analytics | Clinician | to view trends for core outcomes over time | I can evaluate therapy effectiveness | Must | M | Planned |
| US-ANLY-002 | Progress analytics | Clinician | to detect plateaus and worsening trends automatically | I can intervene earlier | Must | M | Planned |
| US-PRED-001 | Outcome prediction | Clinician | to estimate recovery trajectory based on patient history | I can set realistic treatment expectations | Should | L | Planned |
| US-PRED-002 | Outcome prediction | Clinician | to receive adjustment suggestions when predicted progress declines | I can adapt plans proactively | Should | L | Planned |

## 5. Story-level acceptance criteria

### US-INT-001 - Structured intake form

- Given a clinician starts a new patient intake, when required fields are missing, then the form blocks submission and shows field-level validation.
- Given all required fields are completed, when clinician submits intake, then patient profile and baseline outcomes are persisted.
- Given a saved intake, when reopened, then previously entered values are shown without data loss.

Test intent:
- Unit: validation rules by field.
- Integration: API persistence and schema checks.
- E2E: clinician completes intake and sees saved profile.

Implementation evidence (backend):
- `POST /rag/intake` implemented with `generic_holistic_v0` validation and persistence (`intake_profiles`).
- `GET /rag/intake/{patient_id}` implemented for retrieval.
- Regression tests in `backend/tests/test_plan_generate_api.py` cover save/retrieve/not-found contracts.

### US-INT-002 - Intake risk flagging

- Given a completed intake, when risk-flag analysis is requested, then system returns zero or more risk flags with explanation text.
- Given identified risk flags, when clinician reviews them, then they can acknowledge each flag.
- Given risk analysis fails, when fallback occurs, then clinician sees a clear error and can continue manually.

Test intent:
- Unit: risk output parser and severity mapping.
- Integration: LLM call contract, timeout, and fallback path.
- E2E: generate and acknowledge risk flags.

Implementation evidence (backend):
- `GET /rag/intake/{patient_id}/risk-flags` implemented with deterministic rule-based risk analysis.
- Returns `404` when intake is missing and `503` fallback message if risk analysis fails unexpectedly.
- Regression tests in `backend/tests/test_plan_generate_api.py` for success and not-found contracts.

### US-INT-003 - Intake edit with audit trail

- Given an existing intake, when an admin updates it, then the latest intake state is persisted.
- Given an intake update, when persistence completes, then an audit record stores before/after payload and actor identity.
- Given non-admin user, when update is attempted, then operation is blocked with authorization error.

Test intent:
- Unit: audit payload composition and actor attribution.
- Integration: admin-only update endpoint + audit persistence.
- E2E: deferred.

Implementation evidence (backend):
- `PATCH /rag/intake/{patient_id}` implemented as admin-only.
- `intake_profile_audit` persistence added (`before_json`, `after_json`, `actor_sub`, `changed_at`).
- Regression tests in `backend/tests/test_plan_generate_api.py` for admin success and non-admin forbidden.

### US-PLAN-001 - Draft treatment plan generation

**Input framing (locked for Sprint 1):** Option **A** — **generic holistic rehab** profile in `intake_json` (chief complaint, conditions, goals, modalities, contraindications, baseline outcomes such as NRS). NMG-specific fields (e.g. Bioshock, capas) are **out of scope** for v0; see `docs/sprint-01.md` for the normative JSON shape and sprint slice.

- Given a validated **generic holistic v0** `intake_json` and non-empty `available_therapies`, when the clinician requests a plan, then the system returns structured multi-week recommendations.
- Given no relevant evidence is retrieved, when generation runs, then the output includes an explicit insufficiency notice (no silent fabrication).
- Given successful generation, when persistence is implemented, then plan version and metadata are persisted (**persistence optional for Sprint 1 backend-only slice**).

Test intent:
- Unit: plan schema validation; `intake_json` v0 validation (required fields, 422 on bad payloads).
- Integration: retrieval + generation pipeline; `POST /rag/plan/generate` contract.
- E2E: deferred (generate, view, and save plan draft in UI later).

### US-PLAN-002 - Citation traceability

- Given a generated plan, when clinician views recommendation details, then each recommendation includes at least one REF-ID source.
- Given a REF-ID, when opened, then source metadata is visible (title, therapy type, evidence level, language).
- Given missing citations, when validation runs, then plan is marked invalid for approval.

Test intent:
- Unit: citation integrity validator.
- Integration: source metadata retrieval.
- E2E: clinician opens citations from plan UI.

### US-PLAN-003 - Practitioner approval gate

- Given a draft plan, when clinician approves, then status changes to `approved` and approval event is logged.
- Given a draft plan, when clinician rejects, then status changes to `rejected` and reason is required.
- Given non-approved plan, when activation is attempted, then operation is blocked.

Test intent:
- Unit: status transition rules.
- Integration: audit event persistence.
- E2E: approve/reject flow and activation guard.

Implementation evidence (backend):
- `PATCH /rag/plan/{plan_id}/approve` implemented with action validation (`approve|reject`) and persistence updates.
- `GET /rag/plan/{plan_id}` implemented to read persisted `plan_json`.
- `GET /rag/plan/{plan_id}/sources` implemented with citation-ordered source payload.
- Regression tests in `backend/tests/test_plan_generate_api.py` for generate/persist/retrieve/sources/approval flows.
- Write endpoints are role-guarded via JWT roles (`clinician`/`admin`) with `401/403` contract tests.

### US-DIARY-001 - Daily patient diary

- Given a patient has active care plan, when submitting daily check-in, then pain/sleep/mood/function entries are saved.
- Given invalid values, when submit is attempted, then input validation errors are shown.
- Given clinician dashboard view, when date range is selected, then daily entries appear in trend charts.

Test intent:
- Unit: diary validation and score normalization.
- Integration: diary API + storage.
- E2E: patient submit -> clinician visibility.

### US-ANLY-002 - Plateau detection

- Given longitudinal outcome data, when trend analysis runs, then plateau/worsening cases are flagged using defined thresholds.
- Given a flagged case, when clinician opens dashboard, then the flag includes rationale and affected metrics.
- Given insufficient data points, when detection runs, then system returns "insufficient data" without false alerts.

Test intent:
- Unit: plateau rule calculations.
- Integration: scheduled analytics job.
- E2E: flagged patient appears in dashboard.

## 6. Non-functional acceptance criteria

- Performance: 95th percentile API response <= 800 ms for non-AI endpoints in staging baseline load.
- Security: JWT-protected clinician and patient routes; role checks enforced for all write endpoints.
- Privacy: only minimum required fields collected; consent status required before diary and plan workflows.
- Explainability: AI recommendations include citation refs and risk reasoning text where applicable.
- Reliability: failed AI services do not block core manual workflow; fallback paths are available.

## 7. Prioritization and release slicing

| Item | Priority | Release target | Dependency | Notes |
|------|----------|----------------|------------|-------|
| US-INT-001 | Must | R1 | None | Foundation for all downstream features |
| US-PLAN-001 | Must | R1 | US-INT-001 | Initial RAG core value |
| US-PLAN-002 | Must | R1 | US-PLAN-001 | Required trust control |
| US-PLAN-003 | Must | R1 | US-PLAN-001 | Required safety gate |
| US-SESS-001 | Must | R1 | US-INT-001 | Longitudinal tracking base |
| US-DIARY-001 | Must | R1 | US-INT-001 | Between-session continuity |
| US-ANLY-001 | Must | R1 | US-SESS-001, US-DIARY-001 | Outcome visibility |
| US-ANLY-002 | Must | R2 | US-ANLY-001 | Early intervention value |
| US-INT-002 | Must | R2 | US-INT-001 | Safety enhancement |
| US-SESS-002 | Should | R2 | US-SESS-001 | Productivity enhancement |
| US-DIARY-002 | Should | R2 | US-DIARY-001 | Patient engagement |
| US-PRED-001 | Should | R3 | US-ANLY-001 | Predictive model maturity |
| US-PRED-002 | Should | R3 | US-PRED-001 | Recommendation layer |

Release definition:
- R1 (MVP core): intake, plan generation/citations/approval, session log, diary, baseline analytics.
- R2 (MVP+): risk flags, AI note completion, plateau detection.
- R3 (advanced): trajectory prediction and adjustment suggestions.

## 8. Definition of ready / done

### Ready

- Story has unique ID, actor, and value statement
- Acceptance criteria are testable and unambiguous
- TDD test intent is defined (unit/integration/e2e)
- Dependencies, risks, and data/privacy impacts identified

### Done

- Tests created first and passing (Red -> Green -> Refactor evidence)
- Acceptance criteria pass in QA validation
- Logging/audit and citation traceability requirements implemented
- No avoidable duplication introduced; SOLID rationale captured for major design decisions
- Backlog status updated by Planning Agent

## Completion checklist

- [x] All MVP features have specs
- [x] User stories are testable
- [x] Acceptance criteria are unambiguous
- [x] Release priorities agreed
