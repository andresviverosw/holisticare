# Sprint 4 — Backend: US-DIARY-001 (daily patient diary check-ins)

## Sprint parameters

| Field | Value |
|-------|--------|
| Length | 1 week |
| Primary story | US-DIARY-001 |
| Scope | Backend API + persistence + pytest |
| E2E | Deferred |

## Goal

Persist daily self-reported outcomes (pain, sleep quality, mood, function) per patient, with one check-in per calendar day (upsert) and history listing for clinician dashboards and patient apps.

## Delivered backend slice

- `POST /rag/diary` — validate `patient_diary_v0`, upsert by `(patient_id, checkin_date)`.
- `GET /rag/diary/patient/{patient_id}` — `limit`/`offset`, optional `date_from` / `date_to` (ISO dates), newest first.
- `ensure_diary_subject_access`: role `patient` may only access their own `patient_id` (`sub` must be that UUID); `clinician` and `admin` may access any patient in this slice.

## Test evidence

- `backend/tests/test_diary_api.py` — validation, persistence, patient self vs `403`, list order.
- `backend/tests/test_diary_service.py` — insert vs upsert paths.
- Full backend suite: `71 passed`.

## Risks / follow-ups

- UI and patient onboarding (linking auth `sub` to registered patient).
- US-DIARY-002 optional free-text field can extend `patient_diary_v0` without breaking versioning.
