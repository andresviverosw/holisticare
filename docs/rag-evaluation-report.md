# RAG / AI quality evaluation report (EVAL-01)

| Field | Value |
|-------|--------|
| Story | EVAL-01 (final delivery) |
| Date | 2026-07-26 |
| Scope | Capstone evidence for AI quality + safety contracts |
| Related | `backend/scripts/ai_quality_smoke.py`, US-PRIV-001, Phase 1 DoD item 2 |

## 1. Purpose

Provide a short, tutor-facing record of how HolistiCare validates AI plan generation quality for the master’s submission. Full golden-eval (hit ≥ 0.80, faithfulness ≥ 0.85) remains an aspirational Phase 1 target; this report documents **what is automated today**, **how to run it**, and **known limits**.

## 2. Evaluation layers

| Layer | What it checks | Automation |
|-------|----------------|------------|
| Unit / contract | Plan schema, `pending_review`, citation stripping, nutrition guards, insufficient evidence | pytest (`test_rag.py`, `test_pipeline_*`) |
| Privacy egress | No patient UUID/email/phone in outbound LLM prompts | pytest (`test_patient_anonymizer.py`, `test_pipeline_anonymization.py`) |
| API smoke | Generate/approve paths with stubbed pipeline | pytest (`test_plan_generate_api.py`) |
| Live AI smoke | HTTP plan generation contract against running API | `scripts/ai_quality_smoke.py` |
| Pilot cases | Clinical usefulness (human) | Feedback form / synthetic waiver |

## 3. How to run

### Offline (CI-safe)

```bash
cd backend
python -m pytest tests/test_patient_anonymizer.py tests/test_pipeline_anonymization.py tests/test_pipeline_insufficient.py tests/test_rag.py -q
```

### Live smoke (requires API keys + ingested corpus)

```bash
docker compose exec backend env PYTHONPATH=/app python scripts/ai_quality_smoke.py
```

Optional cases file: pass `--cases path/to/cases.json` (see script argparse).

## 4. Metrics observed (capstone)

| Metric | Method | Result / note |
|--------|--------|----------------|
| Practitioner gate | Assert `requires_practitioner_review` and `status=pending_review` | **Pass** (unit + generator hard-rule) |
| Insufficient evidence | Empty retrieval → no LLM generate | **Pass** |
| Citation integrity | Hallucinated REF-IDs stripped | **Pass** (unit) |
| Nutrition safety | Allergy/contraindication synonym block | **Pass** (unit) |
| Egress anonymization | Mock LLM call inspection | **Pass** (US-PRIV-001) |
| Hit rate / faithfulness golden set | Formal RAGAS-style eval | **Not fully automated** — deferred; use smoke + clinician review |
| Latency p95 ≤ 8s | Live timing | **Environment-dependent**; Render free cold start can exceed 50s |

## 5. Known limits

1. Mock corpus size limits topical coverage; system must surface `insufficient_evidence` rather than fabricate.
2. Cross-language retrieval (ES query / EN doc) is not separately scored in CI.
3. Human clinical usefulness is not a pytest assertion — capture via [`pilot-clinician-feedback-form.md`](pilot-clinician-feedback-form.md) or the synthetic-demo waiver appendix.
4. Live smoke quality depends on current Anthropic/OpenAI quotas and corpus ingest state.

## 6. Conclusion for submission

HolistiCare’s AI path is gated by automated **safety and governance contracts** (approval required, citation hygiene, nutrition guards, egress scrub). Formal retrieval golden-eval thresholds from Phase 1 remain **partially met via smoke tooling** rather than a published hit/faithfulness scorecard; residual risk is disclosed here for academic honesty.
