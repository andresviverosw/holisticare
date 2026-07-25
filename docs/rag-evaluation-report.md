# RAG / AI quality evaluation report (MVP — final delivery)

| Field | Value |
|-------|--------|
| Story / track | EVAL-01 (final delivery) |
| Date | 2026-07-25 |
| Scope | Synthetic pilot cases + CI AI quality smoke + contract tests |
| Environment | Local/CI Docker compose; public Render deploy evidence tracked separately (DEPLOY-01) |

## 1. Objective

Provide a short, tutor-facing summary of how HolistiCare validates RAG plan quality for the master’s delivery, mapped to Phase 1 DoD item 2 (golden eval thresholds) with honest limits.

## 2. Evaluation assets

| Asset | Path / command | Role |
|-------|----------------|------|
| Synthetic pilot cases | `backend/data/pilot/cases.json` | Fixed intake scenarios for rehearsal |
| AI quality smoke | `backend/scripts/ai_quality_smoke.py` | Contract + citation gates on generated plans |
| CI job | `.github/workflows/ci.yml` → `ai-quality-smoke` | Blocking by default (advisory via `AI_QUALITY_SMOKE_ADVISORY`) |
| Unit/API tests | `backend/tests/` (pipeline, nutrition safety, insufficient evidence) | Deterministic regressions without live LLM |
| US-PRIV-001 tests | `test_patient_anonymizer.py`, `test_pipeline_anonymization.py` | Prove LLM egress scrub |

## 3. Metrics and gates (implemented)

Phase 1 aspirational thresholds (hit rate ≥ 0.80, faithfulness ≥ 0.85) require a labeled golden retrieval set and LLM-as-judge or human rubric. **MVP implements a pragmatic proxy gate:**

| Check | Pass criterion | Notes |
|-------|----------------|-------|
| HTTP success | 200 on generate for each case | Smoke runner |
| Status | `pending_review` | NOM-024 gate |
| Practitioner review flag | `requires_practitioner_review` implied by contract | Generator hard rule |
| Weeks | ≥ configured minimum (default 1+) | Configurable |
| Insufficient evidence | Fail by default; CI may `--allow-insufficient-evidence` with warn | Avoids fabricating plans |
| Citations | Suite-level non-empty `citations_used`; REF-ID shape | Optional per-case strict mode |
| Nutrition safety | Unit tests for synonym blocking | US-RAG-004 |

## 4. Results (known evidence)

| Source | Result | Date |
|--------|--------|------|
| Pilot rehearsal (`run-pilot-rehearsal`) | 3/3 synthetic cases PASS (2 consecutive runs) | 2026-04-21 (`pilot-go-no-go.md`) |
| Playwright clinician smoke | PASS (login → generate → approve + prediction panels) | 2026-04-21 / later sprint suites |
| CI `ai-quality-smoke` | Configured with `MIN_EVIDENCE_LEVEL=expert_opinion` + allow-insufficient warn for corpus size | Ongoing |
| Backend pytest | Full suite green including anonymization (201+ tests on exec branch) | 2026-07-25 |

**Faithfulness / hit-rate golden set:** not fully instrumented as offline IR metrics in this repo. Proxy = citation presence + insufficient_evidence short-circuit + practitioner review.

## 5. Privacy interaction (US-PRIV-001)

Before query summary / plan generation LLM calls:

1. Intake projected to clinical fields only.
2. Email / phone / UUID patterns redacted in free text.
3. Generator prompt uses `PATIENT_TOKEN`; persisted plan rebinds real `patient_id`.

Evidence: unit + pipeline mock tests (no PII in mocked `complete_claude_or_openai` args).

## 6. Limits and residual risks

- Small curated corpus → higher chance of `insufficient_evidence` or generic plans.
- Free-tier Render cold start can exceed soft 8s latency NFR.
- Clinical alignment of US-PRED outputs still needs live practitioner sign-off (FEEDBACK-01).
- True MRR/faithfulness dashboards remain future work.

## 7. Commands (reproduce)

```bash
# Contract smoke (needs running API + keys + ingested corpus)
docker compose exec backend env PYTHONPATH=/app \
  python scripts/ai_quality_smoke.py --cases data/pilot/cases.json

# Deterministic suite (no live LLM)
cd backend && python -m pytest tests/ -q
```

## 8. Conclusion

For master’s delivery, AI quality is evidenced by **deterministic contract gates**, **pilot synthetic rehearsal PASS**, **citation/insufficient-evidence safeguards**, and **egress anonymization tests**. Full IR golden metrics remain an acknowledged stretch beyond the MVP proxy.
