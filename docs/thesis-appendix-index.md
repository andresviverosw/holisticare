# Thesis appendix index (Track D)

Canonical map of academic / submission artifacts for the HolistiCare AI4devs capstone.

| Field | Value |
|-------|--------|
| Track | **Track D — Submission packaging** |
| Date | 2026-09-06 |
| Freeze tag | `capstone-final` (apply on `main` after packaging PR merges; historical release remains `v1.0-final-AVW`) |
| Public SPA | https://holisticare-frontend.onrender.com |
| Public API | https://holisticare-api.onrender.com (`/health`, `/ready`) |

## Phases 01–06

| Phase | Document |
|-------|----------|
| 01 Requirements & domain | [`01-requirements-and-domain-research.md`](01-requirements-and-domain-research.md) |
| 02 System architecture | [`02-system-architecture.md`](02-system-architecture.md) |
| 03 Data dictionary & privacy | [`03-data-dictionary-and-privacy-framework.md`](03-data-dictionary-and-privacy-framework.md) |
| 04 Feature specs & stories | [`04-feature-specs-and-user-stories.md`](04-feature-specs-and-user-stories.md) |
| 05 Test plan | [`05-test-plan.md`](05-test-plan.md) |
| 06 Deployment & ops | [`06-deployment-and-ops-runbook.md`](06-deployment-and-ops-runbook.md) |

Supporting guides: [`07-user-guide.md`](07-user-guide.md), [`08-developer-guide-and-architecture.md`](08-developer-guide-and-architecture.md), [`09-security-audit-and-todos.md`](09-security-audit-and-todos.md), [`10-solution-diagrams.md`](10-solution-diagrams.md).

## Privacy / compliance

| Artifact | Path |
|----------|------|
| Phase 3 privacy framework (LFPDPPP / NOM-024 mapping) | [`03-data-dictionary-and-privacy-framework.md`](03-data-dictionary-and-privacy-framework.md) |
| US-PRIV-001 egress control | Sprint 16 / ADRs (see [`final-delivery-plan.md`](final-delivery-plan.md)) |
| Synthetic-demo clinical feedback waiver (FEEDBACK-01) | [`feedback-01-synthetic-demo-waiver.md`](feedback-01-synthetic-demo-waiver.md) |
| Post-submission clinician form | [`pilot-clinician-feedback-form.md`](pilot-clinician-feedback-form.md) |

## Evaluation / AI quality

| Artifact | Path |
|----------|------|
| EVAL-01 RAG / AI quality report | [`rag-evaluation-report.md`](rag-evaluation-report.md) |
| Synthetic corpus appendix | [`synthetic-dataset-v1.md`](synthetic-dataset-v1.md) |

## Deploy evidence

| Artifact | Path |
|----------|------|
| Final Render deploy guide (DEPLOY-01) | [`deploy-final-demo.md`](deploy-final-demo.md) |
| Public demo repair closeout | [`ops-demo-repair-checklist.md`](ops-demo-repair-checklist.md) |
| DEMO-01 public walkthrough evidence | [`demo-01-public-walkthrough.md`](demo-01-public-walkthrough.md) |
| Local / CI demo smoke checklist | [`demo-smoke-checklist.md`](demo-smoke-checklist.md) |
| Consolidated entrega (MD/PDF) | [`entrega-final-capstone.md`](entrega-final-capstone.md) · [`entrega-final-capstone.pdf`](entrega-final-capstone.pdf) |

## How to demo (submission path)

### Public (preferred for tutors)

1. Open https://holisticare-frontend.onrender.com — allow ~50–60s on first API hit (Render free cold start).
2. **Entrar (desarrollo — clínico)** (or seeded `clinician`; see deploy doc).
3. Reliable clinical gate path (DEMO-01): memory-bank instantiate → `pending_review` → approve (NOM-024).
4. Scripted evidence:

```bash
cd backend
PYTHONPATH=. python scripts/demo_public_walkthrough.py --skip-generate
```

### Local fallback

See root [`README.md`](../README.md) Quick start + [`setup.md`](setup.md).

```bash
cp .env.example .env
docker compose up -d
# Frontend http://localhost:5173 · API http://localhost:8000/docs
```

## Tagging procedure (after merge to `main`)

```bash
git checkout main && git pull origin main
git tag -a capstone-final -m "HolistiCare AI4devs capstone freeze (Track D)"
git push origin capstone-final
```

Do **not** force-move `v1.0-final-AVW` unless explicitly requested; keep it as the Jul 2026 historical release.
