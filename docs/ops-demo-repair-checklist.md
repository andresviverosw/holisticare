# US-OPS-DEMO-REPAIR-001 — Restore public Render demo data plane

| Field | Value |
|-------|--------|
| Story | US-OPS-DEMO-REPAIR-001 |
| Depends on | US-OPS-HEALTH-001, US-OPS-SCHEMA-001 (`scripts/migrate.sh`) |
| Owner | Ops / solo developer with Render dashboard access |
| Last verified | _pending — run after next successful restore_ |

## Why

Tutor review (19 Aug 2026): public API `/health` stayed 200 while every DB-backed route returned 500 (often shown as a CORS error in the browser). Root cause class: Postgres volume recreate / missing schema+seed without an active monitor.

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
   Expect: health 200, ready **503** (or ready 200 with later clinical 500 if schema half-applied).

2. **Apply schema (single path)**
   ```bash
   export DATABASE_URL='postgresql://USER:PASS@HOST/DB'   # Render External URL
   ./scripts/migrate.sh
   ```

3. **Seed clinician**
   ```bash
   # From an environment that can reach the same DATABASE_URL, e.g. one-off Render shell
   # or local with PYTHONPATH=backend and env pointing at Render DB:
   cd backend
   python -m scripts.seed_clinician
   ```
   (Use the project’s documented seed CLI if the module path differs in your checkout.)

4. **Seed synthetic patients (demo richness)**
   ```bash
   cd backend
   python -m scripts.seed_synthetic_dataset   # or documented SYNTH-01 seed command
   ```

5. **Optional: ingest corpus**
   ```bash
   # Prefer existing dirs: data/ci_smoke (tiny), data/pilot, or data/synthetic guidance.
   # data/mock is NOT in the repo — do not use it on a clean clone.
   docker compose exec backend python -m scripts.ingest --source data/ci_smoke
   ```
   On Render, use admin JWT + `POST /rag/ingest` with a path that exists in the image/volume.

6. **Verify**
   ```bash
   curl -sS https://holisticare-api.onrender.com/ready
   python backend/scripts/smoke_public_demo.py \
     --api-base https://holisticare-api.onrender.com \
     --spa-base https://holisticare-frontend.onrender.com \
     --origin https://holisticare-frontend.onrender.com
   ```
   Then, with a clinician token, `GET /rag/intake/{known-synthetic-id}` → 200.

7. **Record**
   - Date, operator, migrate.sh output, smoke PASS line.
   - Update this doc’s “Last verified” field.

## Prevention

- CD smoke now checks **`/ready`** (US-OPS-MONITOR-001).
- GitHub Actions workflow `public-demo-monitor.yml` runs every 6 hours.
- Do not rely on process `/health` alone for demo uptime.
