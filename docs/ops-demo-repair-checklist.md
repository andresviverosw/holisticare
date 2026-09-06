# US-OPS-DEMO-REPAIR-001 — Restore public Render demo data plane

| Field | Value |
|-------|--------|
| Story | US-OPS-DEMO-REPAIR-001 |
| Depends on | US-OPS-HEALTH-001, US-OPS-SCHEMA-001 (`scripts/migrate.sh`) |
| Owner | Ops / solo developer with Render dashboard access |
| Last verified | **2026-09-06** — health 200, ready `{db:ok}`, SPA 200, CORS OK, dev-login OK, authenticated `GET /rag/chunks` 200 (1+ items), memory-bank 200 |

## Why

Tutor review (19 Aug 2026): public API `/health` stayed 200 while every DB-backed route returned 500 (often shown as a CORS error in the browser). Root cause class: Postgres volume recreate / missing schema+seed without an active monitor.

## Current status (2026-09-06)

Public demo is **up** for the repair ACs:

| Check | Result |
|-------|--------|
| `GET https://holisticare-api.onrender.com/health` | 200 `status=ok` (cold start ~60s on free tier) |
| `GET …/ready` | 200 `status=ready`, `db=ok` |
| SPA `https://holisticare-frontend.onrender.com` | 200 |
| CORS allow-origin | Static Site origin |
| `POST …/auth/dev-login` | 200 clinician JWT |
| `GET …/rag/chunks?limit=3` (Bearer) | 200 with `items` |
| `GET …/rag/plan/memory-bank?limit=3` (Bearer) | 200 |

Re-run restore below only if `/ready` is 503 or authenticated clinical GETs return 500.

## Free-tier OOM / health-check alerts (2026-09-06)

Render may email **“exceeded its memory limit”** and **“HTTP health check failed (timed out after 5 seconds)”** after a plan-generate attempt on free tier. Cause: `get_reranker()` ignored `RERANKER_BACKEND=passthrough` and still constructed `CrossEncoderReranker` (loads torch). Process OOMs → restart → 5s health probes fail during boot (~50–60s cold start).

Mitigation (code): `PassthroughReranker` when backend is `passthrough` (see `render.yaml`). After deploy, light API + memory-bank demo paths stay within free RAM; full CrossEncoder still needs a larger instance.

## Prerequisites

- Render dashboard access (Postgres External Database URL + API service).
- Local `psql` and this repo checkout.
- Optional: Anthropic/OpenAI keys only if you will re-ingest corpus (not required to restore intake/diary CRUD).

## Restore procedure

1. **Confirm failure mode**
   ```bash
   curl -sS https://holisticare-api.onrender.com/health
   curl -sS -o /tmp/ready.json -w "%{http_code}\n" https://holisticare-api.onrender.com/ready
   cat /tmp/ready.json
   ```
   Expect when broken: health 200, ready **503** (or ready 200 with later clinical 500 if schema half-applied).

2. **Apply schema (single path)**
   ```bash
   export DATABASE_URL='postgresql://USER:PASS@HOST/DB'   # Render External URL
   ./scripts/migrate.sh
   ```

3. **Seed clinician**
   ```bash
   cd backend
   PYTHONPATH=. python -m scripts.seed_clinician
   ```

4. **Seed synthetic patients (demo richness)**
   ```bash
   cd backend
   PYTHONPATH=. python -m scripts.seed_synthetic_dataset
   ```

5. **Optional: ingest corpus**
   ```bash
   # Prefer existing dirs: data/ci_smoke (tiny), data/pilot, or data/synthetic.
   # data/mock is NOT in the repo — do not use it on a clean clone.
   docker compose exec backend python -m scripts.ingest --source data/ci_smoke
   ```

6. **Verify**
   ```bash
   curl -sS https://holisticare-api.onrender.com/ready
   cd backend && PYTHONPATH=. python scripts/smoke_public_demo.py \
     --api-base https://holisticare-api.onrender.com \
     --spa-base https://holisticare-frontend.onrender.com \
     --origin https://holisticare-frontend.onrender.com
   ```
   Smoke must print `SMOKE PASS: health + ready + spa + cors + dev-login + chunks`.

7. **Record**
   - Date, operator, migrate.sh output, smoke PASS line.
   - Update this doc’s “Last verified” field.

## Prevention

- CD / monitor smoke checks **`/ready`** and authenticated **`/rag/chunks`** (US-OPS-MONITOR-001 / DEMO-REPAIR).
- GitHub Actions workflow `public-demo-monitor.yml` runs every 6 hours.
- Do not rely on process `/health` alone for demo uptime.

## Free-tier OOM / health-check alerts (2026-09-06)

Render may email **“exceeded its memory limit”** and **“HTTP health check failed (timed out after 5 seconds)”** after a plan-generate attempt on free tier.

**Cause:** `get_reranker()` ignored `RERANKER_BACKEND=passthrough` (already set in `render.yaml`) and still constructed `CrossEncoderReranker`, which loads torch into the ~512MB instance → OOM → restart → 5s health probes fail during the ~50–60s cold start.

**Mitigation (US-OPS-OOM-001):** `PassthroughReranker` when backend is `passthrough`. After deploy, memory-bank and light API paths stay within free RAM. Full CrossEncoder still needs a larger instance; LLM generate may still 502 near ~100s on free proxy timeout.
