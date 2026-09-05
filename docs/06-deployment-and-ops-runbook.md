# Phase 6 - Deployment and Ops Runbook

## Document control

- Owner: Andrés Viveros (solo developer / product owner)
- Contributors: Planning / Development / QA agents
- Version: 1.1
- Last updated: 2026-09-05
- Status: `[ ]` Draft `[~]` In progress `[x]` Complete

## 1. Objective

Define repeatable deployment, monitoring, incident response, backup, and maintenance procedures for HolistiCare — especially the **public Render demo** used for tutor review.

## 2. Environments and infrastructure

| Environment | Purpose | Region | Stack | Access model |
|-------------|---------|--------|-------|--------------|
| Local Compose | Dev + CI-like stack | local | Docker Compose (`docker-compose.yml`), Postgres+pgvector, API, Vite | Developer laptop; `ALLOW_DEV_AUTH` optional via `.env` |
| Local prod overlay | TLS / no-dev-auth rehearsal | local | `docker-compose.prod.yml` + Caddy | `.env.prod` from `.env.prod.example` |
| Public demo (Render) | Tutor / portfolio demo | Render | Blueprint `render.yaml`: Postgres, Docker API, Static Site SPA | Render dashboard + GitHub CD (`cd-render.yml`) |

**Public URLs (canonical):**

- API: `https://holisticare-api.onrender.com`
- SPA: `https://holisticare-frontend.onrender.com`
- Liveness: `GET /health` (process only)
- Readiness: `GET /ready` (Postgres `SELECT 1`) — **US-OPS-HEALTH-001**

## 3. Release process

1. PR → CI (`ci.yml`: pytest, frontend lint/test/build, security audits).
2. Merge to `main`.
3. CD (`cd-render.yml`) triggers Render deploys (autoDeploy off) then runs `scripts/smoke_public_demo.py`.
4. Smoke must pass **health + ready + SPA + CORS + dev-login**.
5. Scheduled monitor (`public-demo-monitor.yml`, every 6h) repeats DB-aware smoke.

## 4. Deployment checklist

- [ ] Configuration and secrets validated (`SECRET_KEY`, DB URL, Anthropic/OpenAI as needed)
- [ ] `ALLOW_DEV_AUTH` intentional for demo only; false for any real clinic host
- [ ] If **`NUTRITION_SAFETY_TERMS_PATH`** is set, file present and schema-valid (API refuses to start otherwise)
- [ ] Database bootstrap via `./scripts/migrate.sh` (not ad-hoc patch memory) — **US-OPS-SCHEMA-001**
- [ ] Clinician seed + synthetic seed applied for demo
- [ ] Corpus ingest from an **existing** dir (`data/ci_smoke` / `data/pilot` / synthetic guidance) — **not** `data/mock`
- [ ] CORS allows Static Site origin
- [ ] Post-deploy: `smoke_public_demo.py` PASS including `/ready`
- [ ] Rollback plan: redeploy previous Render deploy; DB restore from Render backup if schema broken

## 5. Schema / data plane bootstrap

```bash
export DATABASE_URL='postgresql://...'   # Render External URL or local
./scripts/migrate.sh
# then seed (from backend/ with env pointing at same DB):
python -m scripts.seed_clinician
python -m scripts.seed_synthetic_dataset
```

Full public restore: [`ops-demo-repair-checklist.md`](ops-demo-repair-checklist.md).

## 6. Monitoring and alerts

| Signal | How | Action if fail |
|--------|-----|----------------|
| Process up | `GET /health` | Check Render API service / cold start |
| DB up | `GET /ready` | Run migrate/seed checklist; inspect Postgres suspended/reset |
| Demo E2E | CD + cron smoke | GitHub Actions failure email; repair checklist |

Do **not** treat `/health` alone as demo health.

## 7. Security ops notes

- Clinical GETs require clinician/admin JWT (**US-SEC-RBAC-001**).
- JWT still in SPA `localStorage` (residual XSS risk; **US-SEC-JWT-COOKIE-001** deferred).
- LLM egress anonymization remains mandatory (**US-PRIV-001**).

## 8. Related docs

- [`deploy-final-demo.md`](deploy-final-demo.md)
- [`sprint-17.md`](sprint-17.md)
- [`ai4devs-review-remediation-plan.md`](ai4devs-review-remediation-plan.md)
- [`09-security-audit-and-todos.md`](09-security-audit-and-todos.md)
