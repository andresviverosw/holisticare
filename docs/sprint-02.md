# Sprint 2 — Backend: US-INT-001 / US-INT-002 / US-INT-003 (intake persistence, risk flags, and audit trail)

## Sprint parameters

| Field | Value |
|-------|--------|
| Length | 1 week |
| Primary story | US-INT-001, US-INT-002, US-INT-003 |
| Scope | Backend API + persistence + pytest |
| E2E | Deferred |

## Goal

Deliver an initial intake persistence flow that allows clinicians to save and retrieve a validated `generic_holistic_v0` intake profile per patient.

## Delivered backend slice

- `POST /rag/intake` to validate and persist intake payloads.
- `GET /rag/intake/{patient_id}` to retrieve persisted intake data.
- `intake_profiles` table and SQLAlchemy model (`JSONB` intake payload).
- Upsert-like behavior in service layer (save new row or update existing patient row).
- `GET /rag/intake/{patient_id}/risk-flags` endpoint with rule-based risk detection.
- Role-based auth guards on write endpoints:
  - `POST /rag/intake` (`clinician` or `admin`)
  - `POST /rag/plan/generate` (`clinician` or `admin`)
  - `PATCH /rag/plan/{plan_id}/approve` (`clinician` or `admin`)
  - `POST /rag/ingest` (`admin`)
- `PATCH /rag/intake/{patient_id}` admin-only update with persisted `intake_profile_audit` records.
- `GET /rag/intake/{patient_id}/audit` admin-only retrieval for intake audit history (newest-first).

## Test evidence

- New API contract tests:
  - `test_save_intake_200_persists_payload`
  - `test_get_intake_200_returns_saved_payload`
  - `test_get_intake_404_when_missing`
  - `test_get_intake_risk_flags_200_returns_flags`
  - `test_get_intake_risk_flags_404_when_intake_missing`
  - `test_generate_plan_401_when_not_authenticated`
  - `test_ingest_403_for_non_admin_role`
  - `test_update_intake_200_admin_creates_audit`
  - `test_update_intake_403_for_non_admin`
  - `test_get_intake_audit_200_admin_returns_newest_first`
  - `test_get_intake_audit_404_when_intake_missing`
  - `test_get_intake_audit_403_for_non_admin`
- Full backend suite after this slice: `55 passed`.

## Risks / follow-ups

- UI and E2E flow still pending.
- Risk flags are deterministic heuristics for now (LLM-assisted interpretation deferred).
