# Sprint 2 — Backend: US-INT-001 / US-INT-002 (intake persistence and risk flags)

## Sprint parameters

| Field | Value |
|-------|--------|
| Length | 1 week |
| Primary story | US-INT-001, US-INT-002 |
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

## Test evidence

- New API contract tests:
  - `test_save_intake_200_persists_payload`
  - `test_get_intake_200_returns_saved_payload`
  - `test_get_intake_404_when_missing`
  - `test_get_intake_risk_flags_200_returns_flags`
  - `test_get_intake_risk_flags_404_when_intake_missing`
- Full backend suite after this slice: `48 passed`.

## Risks / follow-ups

- No auth/role checks yet on intake endpoints.
- No field-level audit trail for intake edits yet.
- UI and E2E flow still pending.
- Risk flags are deterministic heuristics for now (LLM-assisted interpretation deferred).
