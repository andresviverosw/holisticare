# Sprint 5 — Backend: US-ANLY-001 (outcome trends / baseline analytics)

## Sprint parameters

| Field | Value |
|-------|--------|
| Length | 1 week |
| Primary story | US-ANLY-001 |
| Scope | Backend API + pytest (reads diary series) |
| E2E | Deferred |

## Goal

Expose a clinician-facing time series of core patient-reported outcomes from the existing diary data so dashboards can plot trends without ad-hoc client-side aggregation.

## Delivered backend slice

- `GET /rag/analytics/patient/{patient_id}/outcomes-trend`
  - Optional `date_from`, `date_to` (inclusive). If omitted: `date_to = today`, `date_from = date_to − 90 days`.
  - Maximum span 731 days; invalid windows → `422` (Spanish `detail` strings).
- Response: `patient_id`, `source` (`patient_diary_v0`), resolved `date_from` / `date_to`, and `series` (date + four 0–10 metrics when present in stored JSON).
- **Roles:** `clinician` or `admin` only (`401` / `403`).

## Test evidence

- `backend/tests/test_analytics_api.py` — ordering, validation, auth.
- `backend/tests/test_analytics_service.py` — default window and guardrails.
- Full backend suite: `79 passed`.

## Risks / follow-ups

- Merge session- or intake-reported outcomes into the same series (explicit `source` versioning).
- US-ANLY-002 plateau detection as a separate endpoint or job.
