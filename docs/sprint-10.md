# Sprint 10 — US-PLAN-004 (approved plan memory bank)

## Sprint parameters

| Field | Value |
|-------|--------|
| Length | ~1 week (estimate **L**) |
| Primary story | [US-PLAN-004](04-feature-specs-and-user-stories.md) |
| Scope | DB table + API + Dashboard / Plan review UI + tests |
| Status | **Complete** |

## Dependencies

- **US-PLAN-003** — approval gate (only **approved** plans can be added to the bank).

## Deliverables

- [x] `plan_memory_bank` table + ORM + idempotent SQL patch.
- [x] Sanitized snapshot storage (no `patient_id` in template JSON); new draft with new `plan_id` / `pending_review`.
- [x] REST endpoints under `/rag/plan/memory-bank` (add, list, instantiate).
- [x] Dashboard: list + search + instantiate for current patient UUID.
- [x] Plan review: save approved plan to library with title + tags.
- [x] Pytest coverage for helpers and HTTP contracts.

## Test evidence

- `pytest backend/tests/test_plan_memory_bank_service.py backend/tests/test_plan_memory_bank_api.py`
- Full backend suite green (see CI / local run).

## Ops note

Existing Docker DB volumes need:

`Get-Content -Raw "infra/patch_plan_memory_bank.sql" | docker compose exec -T db psql -U … -d …`

(documented in `setup.md`).
