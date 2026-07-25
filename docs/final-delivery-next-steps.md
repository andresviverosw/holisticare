# Final delivery — next steps (testable environment handoff)

Use this as the **single entry point** when continuing outside the cloud-agent sandbox (your laptop / CI / Render).

| Field | Value |
|-------|--------|
| Branch / PR | `cursor/final-delivery-exec-e84e` — https://github.com/andresviverosw/holisticare/pull/18 |
| Plan of record | [`final-delivery-plan.md`](final-delivery-plan.md) |
| What the agent could not finish | Live **DEPLOY-01** on Render (no account credentials in sandbox) |

---

## 0. What’s already done vs left

| Track | Status | Where |
|-------|--------|--------|
| US-PRIV-001 (LLM egress scrub) | Done in PR #18 | `backend/app/services/patient_anonymizer.py`, pipeline wire-up |
| US-OPS-SPA-HOST (`VITE_API_BASE_URL`) | Done in PR #18 | `frontend/src/utils/apiBaseUrl.js`, `api.js` |
| DOC-CLOSE (FR/NFR + Phase 3 privacy) | Done in PR #18 | `01-…`, `03-…` |
| EVAL-01 | Done | [`rag-evaluation-report.md`](rag-evaluation-report.md) |
| FEEDBACK-01 | Waiver filed | [`feedback-pending-clinical-alignment.md`](feedback-pending-clinical-alignment.md) |
| **DEPLOY-01** public Render URLs | **You** | [`deploy-final-demo.md`](deploy-final-demo.md) |
| DEMO-01 on public URL | **You** (after deploy) | Checklist below |
| Merge PR #18 + tag | **You** | After local/CI green |

Locked demo auth: **`ALLOW_DEV_AUTH=true`** on Render (TA “Entrar desarrollo”); seeded clinician login is secondary.

---

## 1. Bootstrap a testable local environment (do this first)

### 1.1 Checkout and deps

```bash
git fetch origin
git checkout cursor/final-delivery-exec-e84e
git pull origin cursor/final-delivery-exec-e84e

# Backend
cd backend && python -m pip install -r requirements.txt && cd ..

# Frontend (Node ≥ 22.22 required — React Router 8)
cd frontend && npm ci && cd ..
```

Copy env templates:

```bash
cp .env.example .env
# Set at least: SECRET_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY
# For local SPA proxy: leave VITE_API_BASE_URL unset (uses /api → Vite proxy)
```

### 1.2 Automated gates (no Docker required for unit/API mocks)

```bash
# Backend (CI-equivalent)
cd backend && python -m pytest tests/ -q

# Frontend
cd frontend && npm test && npm run lint && npm run build
```

**Pass bar:** pytest green; Vitest green; lint/build green.

### 1.3 Full stack smoke (Docker — closest to real demo)

```bash
# From repo root
docker compose up -d db backend frontend

# Health
curl -s http://localhost:8000/health
# Expect: {"status":"ok",...}

# Dev login + ingest (ALLOW_DEV_AUTH must be true in .env for this path)
TOKEN=$(curl -s -X POST http://localhost:8000/auth/dev-login \
  -H 'Content-Type: application/json' \
  -d '{"role":"admin","sub":"local-admin"}' | jq -r .access_token)

curl -s -X POST http://localhost:8000/rag/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"source_dir":"data/mock","force_reindex":false}' | jq .
```

UI: open `http://localhost:5173` → **Entrar (desarrollo)** → new patient → generate plan → Plan Review → approve/reject.

Optional AI quality smoke (needs keys + ingested corpus):

```bash
docker compose exec backend env PYTHONPATH=/app \
  python scripts/ai_quality_smoke.py --cases data/pilot/cases.json
```

Optional E2E (mocked network in Playwright; no live API required):

```bash
cd frontend && npx playwright install chromium && npm run test:e2e
```

More detail: [`setup.md`](setup.md), [`demo-smoke-checklist.md`](demo-smoke-checklist.md), [`quickstart-clinician.md`](quickstart-clinician.md).

---

## 2. Verify the two new final-delivery features locally

### 2.1 US-PRIV-001 (anonymization)

```bash
cd backend && python -m pytest tests/test_patient_anonymizer.py tests/test_pipeline_anonymization.py -v
```

Manual check (optional): temporarily log or breakpoint in tests — generator user prompt must contain `PATIENT_TOKEN`, not a raw UUID; intake emails must become `[REDACTED_EMAIL]`.

### 2.2 US-OPS-SPA-HOST (API base URL)

```bash
cd frontend && npm test -- --run src/utils/apiBaseUrl.test.js
```

Simulate Render build:

```bash
cd frontend
VITE_API_BASE_URL=https://example-api.onrender.com npm run build
# Built JS should reference that host (search dist/assets for onrender.com)
```

Unset → local `/api` proxy behavior preserved.

---

## 3. DEPLOY-01 — public Render (your machine / dashboard)

Follow **[`deploy-final-demo.md`](deploy-final-demo.md)** end-to-end (Entrega 2 parity). Condensed order:

1. Merge or deploy from branch that includes PR #18 commits (or merge #18 to `main` first).
2. Render **Blueprint** from root `render.yaml`.
3. Set API secrets: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `CORS_ORIGINS=<static-site-origin>`.
4. Set Static Site `VITE_API_BASE_URL=<api-origin>` → **redeploy frontend** (bake-time).
5. `psql` → `CREATE EXTENSION vector;` + `infra/init.sql`.
6. Seed clinician (`scripts/seed_clinician.py`); ingest `data/mock` via admin/dev JWT.
7. Fill the URL log table in `deploy-final-demo.md` §4 and README project URL section.

**Public acceptance checks**

| # | Check | Command / action |
|---|--------|------------------|
| 1 | API up | `curl https://<api>/health` → 200 |
| 2 | SPA loads | Open frontend URL |
| 3 | CORS OK | Browser login without CORS errors |
| 4 | API host correct | DevTools Network → requests go to API host, not Static Site `/api` |
| 5 | Demo path | Entrar desarrollo → generate → approve |
| 6 | Cold start note | First hit may take ~50s+ on free tier — document for TA |

Neon fallback if Render Postgres rejects `vector`: see Entrega 2 doc § “Alternativa: Neon + Render”.

---

## 4. After public deploy — close the last DoD boxes

1. **DEMO-01:** Walk [`demo-smoke-checklist.md`](demo-smoke-checklist.md) against **public** URLs; keep a short note or recording.
2. **README:** paste Frontend + API health URLs (same pattern as Entrega 2 §8).
3. **FEEDBACK-01 (optional upgrade):** replace waiver with completed [`pilot-clinician-feedback-form.md`](pilot-clinician-feedback-form.md) if collaborator is available.
4. **Merge PR #18** when CI green; tag e.g. `capstone-final`.
5. **Submission package:** point Typeform/tutor at repo branch/tag + public frontend URL + docs hub (`docs/README.md`).

---

## 5. Suggested order on your machine (checklist)

```
[ ] Pull PR #18 branch
[ ] pytest + npm test/lint/build
[ ] docker compose up + health + ingest + UI generate/approve
[ ] Merge #18 (or deploy branch) when CI green
[ ] Render Blueprint + secrets + schema + seed + ingest
[ ] Public health + SPA login + generate/approve
[ ] Paste URLs into deploy-final-demo.md + README
[ ] Tag capstone-final / submit
```

---

## 6. Quick links

| Need | Doc |
|------|-----|
| Master plan / DoD | [`final-delivery-plan.md`](final-delivery-plan.md) |
| Render deploy | [`deploy-final-demo.md`](deploy-final-demo.md) |
| Entrega 2 detail / troubleshooting | [`deploy-entrega2-demo.md`](deploy-entrega2-demo.md) |
| Local setup | [`setup.md`](setup.md) |
| Demo commands | [`demo-smoke-checklist.md`](demo-smoke-checklist.md) |
| AI quality | [`rag-evaluation-report.md`](rag-evaluation-report.md) |
| Privacy | [`03-data-dictionary-and-privacy-framework.md`](03-data-dictionary-and-privacy-framework.md) |

---

## 7. If something fails

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `npm` / RR8 engine errors | Node &lt; 22.22 | Upgrade Node (CI uses 22.22) |
| Frontend calls wrong host on Render | Missing/mismatched `VITE_API_BASE_URL` | Set + **redeploy** Static Site |
| Browser CORS errors | `CORS_ORIGINS` ≠ SPA origin | Exact origin, no trailing slash; redeploy API |
| `relation does not exist` | Schema not applied | Re-run `infra/init.sql` |
| Ingest 0 chunks / SSL | Render Postgres SSL / bad OpenAI key | Entrega 2 §10; check `ingestion_log` |
| `/auth/dev-login` 404 | `ALLOW_DEV_AUTH=false` | Keep `true` for academic demo (locked decision) |
| First request times out | Free-tier cold start | Retry; warn TA |
