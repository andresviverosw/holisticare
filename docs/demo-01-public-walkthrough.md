# DEMO-01 — Public demo walkthrough evidence

| Field | Value |
|-------|--------|
| Story | **DEMO-01** (final delivery Must) |
| Date | 2026-09-06 |
| API | https://holisticare-api.onrender.com |
| SPA | https://holisticare-frontend.onrender.com |
| Operator | Cloud agent (API walkthrough) |
| Result | **PASS** (memory-bank path) |

## Acceptance mapping

| AC | Evidence |
|----|----------|
| Walkthrough against live app/API | `backend/scripts/demo_public_walkthrough.py --skip-generate` → `DEMO-01 PASS` |
| Login works on public API | `POST /auth/dev-login` → 200 clinician JWT |
| Intake persists | `POST /rag/intake` → 200 |
| Plan reaches practitioner gate | Instantiated plan `status=pending_review` |
| Approve activates plan | `PATCH /rag/plan/{id}/approve` → `status=approved` |
| Local smoke checklist remains CI gate | unchanged; see `docs/demo-smoke-checklist.md` |

## Path used

**Memory-bank instantiate → approve** (reliable on Render free tier).

LLM **generate** (`POST /rag/plan/generate`) was attempted separately and returned **HTTP 502 after ~100–102s** with an empty body — consistent with Render free-web request timeout while Claude/embeddings run. Data plane and NOM-024 gate remain intact; generation works locally / with longer proxy timeouts.

Script supports both:

```bash
cd backend
PYTHONPATH=. python scripts/demo_public_walkthrough.py --skip-generate   # DEMO-01 gate
PYTHONPATH=. python scripts/demo_public_walkthrough.py                   # try generate, fallback to memory-bank
```

## Run log (2026-09-06, memory-bank path)

```
health: HTTP 200
ready: HTTP 200
dev-login: HTTP 200
save-intake: HTTP 200
list-memory-bank: HTTP 200
instantiate-memory-bank: HTTP 200
get-plan: HTTP 200 (status=pending_review)
get-sources: HTTP 200
approve: HTTP 200 (status=approved)
DEMO-01 PASS
```

Example approved plan id from this run is recorded in the operator console output / CI artifact when re-run.

## Known limits

1. **Free-tier cold start** — first `/health` after idle can take ~50–60s.
2. **LLM generate on free Render** — often 502 near ~100s; use memory-bank for tutor-facing demo unless API keys + paid tier / longer timeout are available.
3. **SPA UI walkthrough** — API path proves the clinical gate; optional browser recording can be attached later.

## Related

- Deploy evidence: `docs/deploy-final-demo.md` (DEPLOY-01)
- Demo repair: `docs/ops-demo-repair-checklist.md` (US-OPS-DEMO-REPAIR-001)
- Local commands: `docs/demo-smoke-checklist.md`
