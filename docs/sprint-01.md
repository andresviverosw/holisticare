# Sprint 1 — Backend: US-PLAN-001 (draft plan generation)

## Sprint parameters

| Field | Value |
|-------|--------|
| Length | 1 week |
| Primary story | US-PLAN-001 |
| Scope | Backend only (API + validation + RAG pipeline wiring + pytest) |
| E2E | Deferred |
| User-facing language | Spanish-first (`preferred_language: es` default; human-readable strings in Spanish where returned) |

## Product decision — plan input framing (locked)

**Option A — Generic holistic rehab input (Sprint 1 and v0 API contract)**

- First implementation uses a **cross-modality holistic** profile: chief complaint, conditions, goals, modalities, contraindications, optional meds, baseline outcomes (e.g. NRS), **without** NMG-specific required fields (Bioshock, capa embrionaria, etc.).
- **Rationale:** Validates RAG + schema + safety behavior quickly; NMG/naturopathy-specific fields remain candidates for co-design (Phase 1 R-01) and a future intake version or `intake_profile.variant` extension.
- **Traceability:** Documented here and in Phase 4 under US-PLAN-001.

## Goal

Deliver a working `POST /rag/plan/generate` that:

1. Accepts a validated **generic holistic** `intake_json` plus `available_therapies`.
2. Runs the existing RAG pipeline (or minimal slice) and returns a **structured** multi-week draft plan.
3. Returns an explicit **insufficiency** state when retrieval/context is inadequate (no silent hallucination).
4. Marks draft plans as requiring practitioner review (align with existing generator validation tests).

Stretch scope completed during Sprint 1 backend execution:
- Persist generated drafts to `treatment_plans`.
- Retrieve persisted plans and cited sources.
- Practitioner approval/rejection endpoint.

## API contract (v0)

Existing route (to be implemented): `POST /rag/plan/generate`

Top-level body remains aligned with `PlanGenerateRequest`:

- `patient_id` (UUID) — may reference a future patient row; for Sprint 1 tests may use a fixture UUID.
- `practitioner_id` (optional UUID).
- `available_therapies` — list of modality strings the clinic offers (e.g. `["acupuntura", "fisioterapia"]`).
- `preferred_language` — default `"es"`.
- `intake_json` — object satisfying **generic holistic v0** below.

### `intake_json` — generic holistic v0 (normative for Sprint 1)

Minimal shape for generation and validation tests (field names can be English snake_case in JSON; **content** should be Spanish where clinical free text is used):

```json
{
  "profile_version": "generic_holistic_v0",
  "demographics": {
    "age_range": "40-49",
    "sex_at_birth": "femenino"
  },
  "chief_complaint": "Dolor lumbar mecánico de 6 meses de evolución.",
  "conditions": ["lumbalgia subaguda"],
  "goals": ["Reducir dolor para retomar caminatas diarias."],
  "contraindications": ["anticoagulación activa"],
  "current_medications": ["—"],
  "allergies": [],
  "baseline_outcomes": {
    "pain_nrs_0_10": 6,
    "notes": "Peor por las mañanas."
  },
  "psychosocial_summary": "Estrés laboral moderado; sueño fragmentado.",
  "prior_interventions_tried": ["AINES", "calor local"]
}
```

**Validation rules (initial):**

- Required: `profile_version`, `chief_complaint`, `conditions` (non-empty), `goals` (non-empty), `available_therapies` (non-empty at request root).
- Optional: remainder; empty lists allowed where shown.
- `preferred_language` must be `es` or `en` for v0 (default `es`).

Future extension (not Sprint 1): `intake_json.profile_version: nmg_v1` with additional optional objects without breaking v0.

## Definition of Done — Sprint 1

- [x] Pydantic models for `intake_json` generic v0 (`app/schemas/intake_v0.py`); list/custom validation mensajes en español donde aplica.
- [x] `POST /rag/plan/generate` implementado (`app/api/rag.py`) y delega en `RAGPipeline.generate_plan`.
- [x] Rama explícita sin chunks tras rerank: `insufficient_evidence: true` + `confidence_note` en español (`app/rag/pipeline.py`).
- [x] `pytest`: `test_intake_v0.py`, `test_plan_generate_api.py`, `test_pipeline_insufficient.py`, `test_rag.py`.
- [x] CI discipline: GitHub Actions pytest (`.github/workflows/ci.yml`), `dependency_overrides` + `conftest.py` env defaults (sin PostgreSQL ni API keys para la suite por defecto).
- [x] Persistencia de planes draft en `treatment_plans` (incluye `insufficient_evidence=true` cuando aplica).
- [x] `GET /rag/plan/{plan_id}` implementado.
- [x] `GET /rag/plan/{plan_id}/sources` implementado con orden determinístico según `citations_used`.
- [x] `PATCH /rag/plan/{plan_id}/approve` implementado (`approve|reject`) con actualización de estado en DB.
- [ ] No secrets logged (revisión continua); compose: usar `scripts/compose-config-safe.ps1`.

## Test outline (pytest)

| Layer | Focus |
|-------|--------|
| Unit | `intake_json` validation — missing required fields, wrong types, empty `conditions`/`goals`. |
| Unit | Plan output schema / citation rules (extend existing `test_rag.py` patterns). |
| Integration | `POST /rag/plan/generate` with fixture body — 200 + shape; persistence path mocked for CI. |
| Integration | `GET /rag/plan/{plan_id}`, `GET /rag/plan/{plan_id}/sources`, `PATCH /rag/plan/{plan_id}/approve` contracts. |
| Deferred | E2E UI flows and real DB integration tests in containerized environment. |

## Test evidence snapshot

- Backend suite status after latest slice: `35 passed`.
- Key files: `backend/tests/test_plan_generate_api.py`, `backend/tests/test_plan_persistence.py`, `backend/tests/test_pipeline_insufficient.py`.

## Handoff template (end of sprint)

- Backlog item ID: US-PLAN-001 (Sprint 1 slice)
- Scope: Backend draft generation + generic v0 intake validation
- Acceptance criteria: see Phase 4 US-PLAN-001 + DoD checklist above
- Test evidence: `pytest` output / CI
- Risks: corpus small — insufficiency path must be user-visible; co-design may add NMG fields later
- Next owner: Planning Agent (Sprint 2: US-PLAN-002 or persistence + US-INT-001)
