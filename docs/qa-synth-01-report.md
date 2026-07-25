# QA Report — SYNTH-01 Synthetic Dataset v1

| Field | Value |
|-------|--------|
| Story | SYNTH-01 |
| Date | 2026-07-25 |
| Verdict | **PASS** |

## Scope validated

- Deterministic generator + committed `backend/data/synthetic/v1/dataset.json`
- Pydantic schema coverage for intake / diary / sessions
- Plan governance statuses + NOM-024 review flag
- Analytics cohorts: improving / high-pain plateau / worsening / short series
- Memory-bank de-identification
- Generate CLI smoke (no DB)

## Test evidence

```bash
python -m pytest backend/tests/test_synthetic_dataset.py \
  backend/tests/test_generate_synthetic_dataset_cli.py \
  backend/tests/test_plan_memory_bank_service.py -q
```

Result: **19 passed**.

## Risks / gaps

| Risk | Severity | Notes |
|------|----------|-------|
| Seed script not exercised against live Postgres in CI | Low | Idempotent upserts unit-shaped; needs Compose for integration smoke |
| Plans are synthetic (not LLM-generated) | Info | Intentional for offline/demo corpus; pilot RAG cases remain separate |
| Full 80-patient package not committed | Low | Regenerable via `--variants 10` |

## Handoff

- Backlog item ID: SYNTH-01
- Scope: e2e synthetic corpus for final demo / thesis appendix
- Acceptance criteria: met (see `docs/synthetic-dataset-v1.md`)
- Test evidence: PASS (19)
- Risks/issues: live DB seed smoke optional for DEPLOY-01
- Next owner: Ops/Demo (seed on Render after deploy) / Planning (thesis appendix link)
