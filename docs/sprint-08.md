# Sprint 8 — Safety config: US-RAG-004 (config-driven nutrition synonym dictionaries)

## Sprint parameters

| Field | Value |
|-------|--------|
| Length | 1 week |
| Primary story | [US-RAG-004](04-feature-specs-and-user-stories.md) |
| Scope | Backend config loading/validation + matcher wiring + tests |
| Owner | _TBD (Planning Agent assigns)_ |
| E2E | Deferred |
| Status | **Complete** |

## Dependencies

- **US-RAG-003** — nutrition safety matcher must already be active.
- **US-PLAN-002** — citation/safety traceability remains in place.

## Goal

Replace hardcoded nutrition synonym rules with a validated, versioned configuration source so clinics can update safety terms without code changes while preserving deterministic behavior and test coverage.

## Planned deliverables

- [x] Introduce a repo-tracked config file for nutrition safety synonyms (default dictionary).
- [x] Add schema validation for config structure and clear startup/runtime errors on invalid config.
- [x] Wire nutrition safety guard to load terms from config (bundled default when unset; optional env override; invalid override or malformed JSON fails at API startup).
- [x] Add unit tests for config parsing + normalization + positive/negative matching scenarios.
- [x] Add integration test proving `nutrition_safety_flags` still behave correctly with configured terms (existing `TestNutritionSafetyGuards` in `backend/tests/test_rag.py` remains green against loaded defaults).
- [x] Document update workflow for dictionary maintenance (who, where, how to validate) — see `setup.md`, `.env.example`, `08-developer-guide-and-architecture.md`, and `06-deployment-and-ops-runbook.md`.

## Test evidence (target)

- New/updated tests under `backend/tests/` for config and matcher behavior.
- Existing RAG/plan generation tests stay green.

**Implementation note (done):** Default JSON lives at `backend/app/config/nutrition_safety_terms.json`; loader and validation are in `backend/app/rag/nutrition_safety_config.py`; the API lifespan preloads synonyms so a bad file fails fast. Optional override: set **`NUTRITION_SAFETY_TERMS_PATH`** to an absolute path or a path relative to the backend process working directory (documented in `.env.example` and `setup.md`).

## Risks / follow-ups

- Risk of over-blocking if synonym list grows without governance; add ownership and review cadence.
- Environment-specific overrides are supported via **`NUTRITION_SAFETY_TERMS_PATH`**; treat overrides like any other config artifact (review, version control or secret-store process per clinic).

## Sprint outcome

- **Backlog:** [US-RAG-004](04-feature-specs-and-user-stories.md) marked **Done (Sprint 8)** in the story table; release notes updated (R2 includes completed US-RAG-004).
- **Next sprint:** [Sprint 9 — US-INT-005](sprint-09.md) (patient UUID + retrieve/select existing id).

## Test evidence (recorded)

- `pytest backend/tests/ --ignore=backend/tests/integration` — **142 passed** (local run, Sprint 8 closeout).
- Targeted: `pytest backend/tests/test_nutrition_safety_config.py backend/tests/test_rag.py::TestNutritionSafetyGuards` — green.
