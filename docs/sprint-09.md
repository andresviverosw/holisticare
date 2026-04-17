# Sprint 9 — Intake UX: US-INT-005 (automatic patient UUID + retrieve existing)

## Sprint parameters

| Field | Value |
|-------|--------|
| Length | 1 week (estimate **M**) |
| Primary story | [US-INT-005](04-feature-specs-and-user-stories.md) (section **US-INT-005**) |
| Scope | Frontend-first: new patient UUID v4, validation, copy UX; optional local “recent patients”; backend listing only if scoped in sprint |
| Owner | _TBD (Planning Agent assigns)_ |
| E2E | Deferred (Playwright not required for slice) |
| Status | **Complete** (dev implementation); QA sign-off _TBD_ |

## Dependencies

- **US-INT-004** — structured intake on the plan generator with save/load (baseline UI and `patient_id` field).

## Goal

Clinicians never need to invent or hand-type **`patient_id`**: **new** patients get a fresh **RFC-4122 UUID v4** from the app with a copy-friendly control; **existing** patients can be selected or loaded without guessing IDs (reuse **Cargar intake guardado**, optional **recent patients** in `localStorage`, and/or a small API if added this sprint).

## Planned deliverables

- [x] **New patient:** control **«Nuevo paciente»** assigns `patient_id` via `crypto.randomUUID()` (`newPatientUuid` in `frontend/src/utils/uuidV4.js`); copy via **«Copiar ID»**.
- [x] **UUID validation:** invalid v4 blocks save/load/generate; helper text and `aria-invalid` on the field (`isValidUuidV4`).
- [x] **Existing patient:** **Cargar intake guardado** unchanged; **Pacientes recientes** (last 10, label + id) via `localStorage` (`frontend/src/utils/recentPatients.js`).
- [x] **Tests:** `uuidV4.test.js`, `recentPatients.test.js` (Vitest).
- [ ] **Optional (stretch):** `GET` listing/search over persisted intakes — deferred (authz/pagination); follow-up story.

## Test evidence (recorded)

- `npm run test` (Vitest) — **22 passed** (includes `uuidV4.test.js`, `recentPatients.test.js`).
- `npm run lint` (ESLint) — **clean**.

## Risks / follow-ups

- Server-backed patient search crosses tenancy/authz; keep minimal slice frontend-only unless product requires API this sprint.
- Optional warning when generating for a `patient_id` with no saved intake — product policy; can be a follow-on story.

## Handoff template (end of sprint)

- Backlog item ID: US-INT-005
- Scope: (what shipped vs deferred)
- Acceptance criteria: (pass/fail per bullet in story section)
- Test evidence: (commands + results)
- Risks/issues: (open items)
- Next owner: QA / Planning
