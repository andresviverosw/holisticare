# Sprint 3 — Backend: US-SESS-001 (structured session logging)

## Sprint parameters

| Field | Value |
|-------|--------|
| Length | 1 week |
| Primary story | US-SESS-001 |
| Scope | Backend API + persistence + pytest |
| E2E | Deferred |

## Goal

Allow clinicians to persist structured session notes: interventions (therapy type, description, optional duration) and clinical observations, with per-patient history for longitudinal tracking.

## Delivered backend slice

- `POST /rag/sessions` — validate `clinical_session_v0`, persist to `care_sessions`.
- `GET /rag/sessions/patient/{patient_id}` — paginated list (`limit`, `offset`), newest `occurred_at` first.
- Role guards: `clinician` or `admin` on both endpoints (`401` without JWT).

## Test evidence

- `backend/tests/test_session_api.py` (validation, persistence wiring, list ordering, empty list, `401`).
- Full backend suite: `62 passed`.

## Risks / follow-ups

- UI session capture and E2E flows.
- Optional linkage to `treatment_plan_id` or billing codes in a later version.
