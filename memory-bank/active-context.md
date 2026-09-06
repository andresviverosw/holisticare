# Current Context

## Ongoing Tasks

- Track D: tag `capstone-final` + README/demo URL confirmation
- Optional: paid Render / longer timeout so live `POST /rag/plan/generate` completes for tutors
## Known Issues

- Public LLM generate on Render free tier often 502 at ~100s; DEMO-01 uses memory-bank instantiate → approve
- Free-tier cold start still ~50–60s on first `/health`
## Next Steps

- Track D packaging (tag + CHANGELOG/README closeout) or FEEDBACK-01 if still open
- Optional US-MOB-003 / US-PRIV-002 product polish
## Current Session Notes

- [2026-09-06] DEMO-01 PASS on public API: login → intake → memory-bank instantiate → pending_review → approve. Script: `backend/scripts/demo_public_walkthrough.py`. Evidence: `docs/demo-01-public-walkthrough.md`.
- [2026-09-06] DEPLOY-01 / US-OPS-DEMO-REPAIR-001 closed earlier same day.
