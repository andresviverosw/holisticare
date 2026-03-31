# Sprint 6 — Backend: US-ANLY-002 (plateau / worsening flags)

## Sprint parameters

| Field | Value |
|-------|--------|
| Length | 1 week |
| Primary story | US-ANLY-002 |
| Scope | Backend API + deterministic rules + pytest |
| E2E | Deferred |

## Goal

Surface early-warning flags when patient-reported pain or function shifts between the first and second half of a selected diary window, without LLM or scheduled jobs in this slice.

## Delivered backend slice

- `GET /rag/analytics/patient/{patient_id}/plateau-flags` — same optional `date_from` / `date_to` and validation as outcomes-trend (default 90 días, max 731).
- `analysis_status`: `insufficient_data` if fewer than 7 diary rows in range (`flags` vacío); otherwise `ok` (flags may still be empty).
- Flags (cuando aplica): `PAIN_WORSENING`, `HIGH_PAIN_PLATEAU`, `FUNCTION_WORSENING`, each with Spanish `message` / `detail`.

## Test evidence

- `backend/tests/test_plateau_service.py` — reglas puras.
- `backend/tests/test_plateau_api.py` — HTTP + mocks de DB.
- Full backend suite: `87 passed`.

## Risks / follow-ups

- Ajuste clínico de umbrales y ventanas; zonas horarias para `entry_date`.
- Job programado o agregación con sesiones clínicas además del diario.
