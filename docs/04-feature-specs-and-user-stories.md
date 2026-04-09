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
| US-INT-004 | Patient intake and profile | Clinician | to enter intake data using a structured form instead of raw JSON in the plan generator | I avoid syntax errors and confusion when preparing `generic_holistic_v0` for plan generation | Should | M | Done (UI + API) |
| US-INT-005 | Patient intake and profile | Clinician | the tool to assign a new RFC-4122 UUID v4 for a new patient and to retrieve or select an existing patient identifier | I never have to invent or type UUIDs by hand, and I can return to a known patient safely | Should | M | Planned |
| US-PLAN-001 | AI treatment planning | Clinician | to generate a draft multi-week treatment plan from patient profile and goals | I get a high-quality starting point faster | Must | L | Done (backend Sprint 1) |
| US-PLAN-002 | AI treatment planning | Clinician | to see source citations (REF-IDs) attached to each recommendation | I can trust and verify recommendations | Must | M | Done (backend Sprint 1) |
| US-PLAN-003 | AI treatment planning | Clinician | to approve or reject AI plans before activation | treatment remains practitioner-controlled | Must | S | Done (backend Sprint 1) |
| US-RAG-001 | Knowledge base (RAG) | Admin | to ingest PDF and HTML sources into the vector index | clinical references are searchable for retrieval and citations | Must | S | Done (backend) |
| US-RAG-002 | Knowledge base (RAG) | Admin | to load my curated clinical corpus into the running system and confirm retrieval works | plan generation uses my real evidence base instead of mock samples | Must | M | Done (ops + verification) |
| US-SESS-001 | Session logging | Clinician | to log session interventions and observations in structured format | progress can be tracked across time | Must | M | Done (backend API slice) |
| US-SESS-002 | Session logging | Clinician | AI to suggest note completion from structured inputs | documentation time decreases | Should | M | Done (backend API slice) |
| US-DIARY-001 | Patient diary | Patient | to submit daily pain, sleep, mood, and function check-ins | my progress between sessions is visible | Must | M | Done (backend API slice) |
| US-DIARY-002 | Patient diary | Patient | to add optional free-text notes in Spanish | I can provide relevant context in my own words | Should | S | Done (backend API slice) |
| US-ANLY-001 | Progress analytics | Clinician | to view trends for core outcomes over time | I can evaluate therapy effectiveness | Must | M | Done (backend API slice) |
| US-ANLY-002 | Progress analytics | Clinician | to detect plateaus and worsening trends automatically | I can intervene earlier | Must | M | Done (backend API slice) |
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
- `GET /rag/intake/{patient_id}/audit` implemented as admin-only, returning newest-first audit entries.
- Regression tests in `backend/tests/test_plan_generate_api.py` for update success, audit retrieval (`200/404`), and non-admin forbidden (`403`).

### US-INT-004 - Clinician intake form in plan generator (replace raw JSON)

- Given the plan generation screen (`generic_holistic_v0`), when a clinician fills separate fields (chief complaint, conditions, goals, list-style fields, optional demographics, baseline pain, etc.), then the UI builds a valid `intake_json` payload without requiring manual JSON editing.
- Given required intake fields are empty or invalid, when the clinician tries to generate a plan, then the UI blocks submit and shows clear, field-level validation (aligned with backend rules: at least one non-empty condition and goal, non-empty chief complaint, optional list fields normalized to arrays).
- Given the clinician still needs to debug or import data, when an advanced option exists, then they may view the derived JSON in a collapsible **Avanzado** panel (read-only preview).

Test intent:
- Unit: `frontend/src/utils/intakeBuilder.js` maps form state ↔ `generic_holistic_v0` (`buildIntakePayload`, `formStateFromIntakeJson`, `validateIntakeForm`).
- Component/integration: Dashboard calls `ragApi.generatePlan` with the assembled object; save/load intake via `POST /rag/intake` and `GET /rag/intake/{patient_id}`.
- E2E: deferred until Playwright (if introduced).

Implementation evidence (frontend):
- `frontend/src/pages/Dashboard.jsx` — structured fields only; **Guardar intake** / **Cargar intake guardado**; JSON shown under `<details>` for debugging only.
- `frontend/src/services/api.js` — `saveIntake`, `getIntake` alongside plan generation.
- Canonical schema: `backend/app/schemas/intake_v0.py` (`GenericHolisticIntakeV0`).

### US-INT-005 - Automatic patient UUID (new) and retrieval (existing)

- Given a **new** patient workflow on the plan/intake screen, when the clinician chooses “new patient” (or equivalent), then the UI assigns a **new RFC-4122 UUID version 4** for `patient_id` and shows it in a copy-friendly field (read-only or confirm-before-edit).
- Given an **existing** patient, when the clinician needs that patient’s id, then the UI provides a way to **retrieve** it without manual typing — e.g. load by prior saved intake (**Cargar intake guardado** already uses `patient_id`), a **recent patients** list (session/local storage or server-backed), and/or a **search/list patients** API once available.
- Given a pasted or edited UUID, when it is not a valid v4 UUID, then the UI blocks save/generate and explains the format expected.
- Optional (product policy): warn if generating a plan for a `patient_id` that has no saved intake yet.

Test intent:

- Unit: UUID v4 validation helper; generator uses `crypto.randomUUID()` or equivalent.
- Integration: Dashboard (or patient picker component) wires new vs existing flows; contract tests if a new `GET /rag/patients` (or search) endpoint is added.
- E2E: deferred until Playwright (if introduced).

Implementation notes:

- **Minimal slice (frontend-only):** “Nuevo paciente” button sets `patient_id` via `crypto.randomUUID()`; show copy button; keep manual override under advanced if needed.
- **Existing patients without a new API:** reuse **patient_id** field + **Cargar intake guardado**; optional “recientes” storing last N `(id, label, date)` in `localStorage`.
- **Richer slice (backend):** add listing/search endpoints over `intake_profiles` / patients (scoped by clinic/practitioner) — requires authz design and possibly pagination; follow-on task.

### US-SESS-001 - Structured session logging

- Given a clinical encounter, when the clinician submits a session log, then interventions and observations are stored in a structured, validated payload.
- Given prior sessions for a patient, when the clinician lists session history, then entries are returned in reverse chronological order by session time.
- Given an unauthenticated caller, when create or list is attempted, then the API returns `401`.

Test intent:
- Unit: `clinical_session_v0` validation (required interventions, observations).
- Integration: `POST /rag/sessions` and `GET /rag/sessions/patient/{patient_id}` with persistence.
- E2E: deferred (UI session form).

Implementation evidence (backend):
- `clinical_session_v0` schema in `backend/app/schemas/session_v0.py`.
- `care_sessions` table and model; service layer `backend/app/services/session_service.py`.
- `POST /rag/sessions` and `GET /rag/sessions/patient/{patient_id}` (JWT roles `clinician` or `admin`).
- Contract tests in `backend/tests/test_session_api.py`.

### US-SESS-002 - AI-assisted note completion

- Given structured interventions and optional draft text, when a clinician requests note assistance, then the API returns suggested observations and patient-reported response text.
- Given empty interventions, when assistance is requested, then validation fails with `422`.
- Given an unauthenticated caller, when assistance is requested, then the API returns `401`.

Test intent:
- Integration: `POST /rag/sessions/suggest-note` contract tests and auth checks.

Implementation evidence (backend):
- `SessionNoteAssistV0` schema in `backend/app/schemas/session_v0.py`.
- Suggestion service in `backend/app/services/session_note_service.py`.
- `POST /rag/sessions/suggest-note` endpoint (JWT roles `clinician`/`admin`).
- Tests in `backend/tests/test_session_api.py`.

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

Implementation evidence (backend):
- `patient_diary_v0` schema (`pain_nrs_0_10`, `sleep_quality_0_10`, `mood_0_10`, `function_0_10`, `checkin_date`) in `backend/app/schemas/diary_v0.py`.
- `patient_diary_entries` table with unique `(patient_id, entry_date)`; ORM `PatientDiaryEntry`; upsert in `backend/app/services/diary_service.py`.
- `POST /rag/diary` and `GET /rag/diary/patient/{patient_id}` with optional `date_from` / `date_to` query filters; list ordered by `entry_date` descending.
- JWT roles: `patient`, `clinician`, or `admin`. **Patient** tokens must use `sub` equal to the target `patient_id` (UUID) or the API returns `403`.
- Tests: `backend/tests/test_diary_api.py`, `backend/tests/test_diary_service.py`.

### US-DIARY-002 - Optional Spanish free-text notes

- Given a diary check-in, when a patient includes optional `notes_es`, then the value is trimmed, persisted, and returned in the API payload.
- Given blank `notes_es`, when a check-in is submitted, then the field is normalized to `null`.
- Given excessive note length, when a check-in is submitted, then validation rejects the payload.

Test intent:
- Integration: `POST /rag/diary` persistence/response includes `notes_es`.

Implementation evidence (backend):
- `notes_es` added to `patient_diary_v0` in `backend/app/schemas/diary_v0.py`.
- Existing diary upsert flow persists `notes_es` within `diary_json`.
- Tests updated in `backend/tests/test_diary_api.py`.

### US-ANLY-001 - Outcome trends (baseline analytics)

- Given diary check-ins in a date range, when a clinician requests analytics, then the API returns an ordered time series suitable for trend charts (pain, sleep, mood, function).
- Given an invalid window (`date_from` after `date_to`, or span over 731 days), then the API returns `422` with a clear message.
- Given role `patient`, when outcomes trend is requested, then access is denied (`403`); `clinician` and `admin` may query any patient in this slice.

Test intent:
- Unit: date window resolution and validation.
- Integration: `GET /rag/analytics/patient/{patient_id}/outcomes-trend`.
- E2E: deferred (dashboard charts).

Implementation evidence (backend):
- `GET /rag/analytics/patient/{patient_id}/outcomes-trend` with optional `date_from` / `date_to` (defaults: end = today, start = end − 90 days).
- Series built from `patient_diary_entries`, ascending by `entry_date`, source tag `patient_diary_v0`.
- Service: `backend/app/services/analytics_service.py`; diary range query: `list_diary_entries_in_date_range` in `diary_service.py`.
- Tests: `backend/tests/test_analytics_api.py`, `backend/tests/test_analytics_service.py`.

### US-ANLY-002 - Plateau detection

- Given longitudinal outcome data, when trend analysis runs, then plateau/worsening cases are flagged using defined thresholds.
- Given a flagged case, when clinician opens dashboard, then the flag includes rationale and affected metrics.
- Given insufficient data points, when detection runs, then system returns "insufficient data" without false alerts.

Test intent:
- Unit: plateau rule calculations.
- Integration: scheduled analytics job.
- E2E: flagged patient appears in dashboard.

Implementation evidence (backend):
- Heuristic rules on diary outcome series (first vs second chronological half): `PAIN_WORSENING`, `HIGH_PAIN_PLATEAU`, `FUNCTION_WORSENING` in `backend/app/services/plateau_service.py` (minimum 7 días de diario; ≥3 valores por métrica y mitad).
- `GET /rag/analytics/patient/{patient_id}/plateau-flags` with same ventana de fechas y autenticación que US-ANLY-001 (`clinician`/`admin`). Respuesta: `analysis_status` (`ok` | `insufficient_data`), `flags` con `code`, `severity`, `metric`, `message`, `detail` (español).
- Orquestación en `get_patient_plateau_flags_payload` (`analytics_service.py`).
- Tests: `backend/tests/test_plateau_service.py`, `backend/tests/test_plateau_api.py`.

### US-RAG-001 - Multi-format corpus ingestion

- Given a directory used as `source_dir` for `POST /rag/ingest`, when it contains `.pdf`, `.html`, and `.htm` files, then each supported file is indexed (PDFs via the existing reader; HTML via text extraction with script/style stripped).
- Given an HTML file, when ingested, then chunk metadata remains consistent with PDFs (`file_name`, `page_label` for non-paged HTML as a single logical page).
- Given a non-PDF file, when the pipeline evaluates “thin” document replacement, then OCR / hybrid PDF logic runs **only** for `.pdf` files (HTML is never passed to the PDF hybrid path).

Test intent:

- Unit / integration: `backend/tests/test_html_ingestion.py`, `backend/tests/test_loader_security.py` (extension registration and guards).

Implementation evidence (backend):

- `backend/app/rag/ingestion/html_reader.py` — `HolisticareHTMLReader`, UTF-8 read, BeautifulSoup `html.parser`.
- `backend/app/rag/ingestion/loader.py` — `required_exts` includes `.pdf`, `.html`, `.htm`; shared HTML reader instance; OCR thin-file path gated to `.pdf` only.

### US-RAG-002 - Onboard curated research / clinical corpus

- Given a curated set of clinical reference files (PDF and/or HTML) owned by the project, when an admin places them under an agreed `source_dir` visible to the backend (local bind mount or image copy), then `POST /rag/ingest` indexes them without manual JSON or ad-hoc steps.
- Given a first-time load or a corpus refresh, when ingestion completes, then counts (files processed, chunks created) are recorded and **at least one** smoke check (e.g. chunk browse or plan generation with expected citations) confirms retrieval uses the new material.
- Given licensing or privacy constraints on the corpus, when documents are added, then the team documents consent/source provenance in the ops or research appendix (out of band from code, but required for acceptance in academic / pilot contexts).

Test intent:

- Integration / ops: scripted or documented sequence from `docker compose` + `POST /rag/ingest` with `source_dir` and optional `force_reindex=true`; capture expected HTTP `200` and non-empty chunk listing for a known filename or therapy tag if metadata allows.
- Regression: existing ingestion tests (`test_html_ingestion`, loader security) remain green after any path or wiring changes.

Implementation notes:

- Technical ingestion capability is covered by **US-RAG-001**; this story is about **operational delivery** of *your* corpus: directory layout, compose volume or image rebuild, env-safe ingest command, and verification checklist (see `docs/setup.md` ingestion smoke, `docs/demo-smoke-checklist.md` if extended).
- If the corpus must live outside `data/mock`, define a stable repo path (e.g. `data/corpus/`) and document it in deployment/runbook material without committing restricted PDFs if policy requires.
- Operational steps and verification commands: **`docs/setup.md` (section 4.4)**; container ingest: `backend/scripts/run_corpus_ingest.py`; ingestion failures: `backend/scripts/ingestion_log_report.py`.
- Retrieval/browse uses Postgres table **`data_clinical_chunks`** (LlamaIndex); smoke: `GET /rag/chunks`, plan generation with citations, optional `backend/scripts/e2e_plan_smoke.py`.

Implementation evidence (accepted):

- Corpus ingested under `backend/data/corpus` (gitignored); `force_reindex` + per-file delete fix documented in prior commits.
- Chunk listing and plan sources aligned to `data_clinical_chunks` in application SQL.

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
| US-RAG-001 | Must | R1 | None | Multi-format ingestion (PDF, HTML); enables retrieval corpus |
| US-RAG-002 | Must | R2 | US-RAG-001 | Load curated corpus + verify retrieval (ops slice) |
| US-PLAN-002 | Must | R1 | US-PLAN-001 | Required trust control |
| US-PLAN-003 | Must | R1 | US-PLAN-001 | Required safety gate |
| US-SESS-001 | Must | R1 | US-INT-001 | Longitudinal tracking base |
| US-DIARY-001 | Must | R1 | US-INT-001 | Between-session continuity |
| US-ANLY-001 | Must | R1 | US-SESS-001, US-DIARY-001 | Outcome visibility |
| US-ANLY-002 | Must | R2 | US-ANLY-001 | Early intervention value |
| US-INT-002 | Must | R2 | US-INT-001 | Safety enhancement |
| US-SESS-002 | Should | R2 | US-SESS-001 | Productivity enhancement |
| US-DIARY-002 | Should | R2 | US-DIARY-001 | Patient engagement |
| US-INT-004 | Should | R2 | US-PLAN-001 | Clinician UX: structured intake on plan generator |
| US-INT-005 | Should | R2 | US-INT-004 | Auto UUID for new patients; retrieve/select existing id |
| US-PRED-001 | Should | R3 | US-ANLY-001 | Predictive model maturity |
| US-PRED-002 | Should | R3 | US-PRED-001 | Recommendation layer |

Release definition:
- R1 (MVP core): intake, plan generation/citations/approval, session log, diary, baseline analytics.
- R2 (MVP+): risk flags, AI note completion, plateau detection, operational load of the curated clinical corpus into the vector store with verification (**US-RAG-002 — done**), clinician-facing structured intake on the plan generator with save/load (**US-INT-004 — done**); **US-INT-005** (auto patient UUID + retrieve existing) is the next intake UX slice.
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
