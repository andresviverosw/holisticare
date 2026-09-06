# Current Context

## Ongoing Tasks

- Track D: tag `capstone-final` + README/demo URL confirmation
- Confirm CD deployed US-OPS-OOM-001 passthrough fix on Render
## Known Issues

- Free-tier cold start still ~50–60s on first `/health`; 5s health-check alerts during restart are expected noise
- Public LLM generate on Render free tier often 502 at ~100s; DEMO-01 uses memory-bank instantiate → approve
## Next Steps

- Track D packaging (tag + CHANGELOG/README closeout)
- Optional US-MOB-003 / US-PRIV-002 product polish; optional paid Render for live generate
## Current Session Notes

- [2026-09-06] DEMO-01 merged (PR #24). Re-verified PASS (plan `7654eeed-4377-431b-8648-ff9ffe6c9114`). Script: `backend/scripts/demo_public_walkthrough.py --skip-generate`. Evidence: `docs/demo-01-public-walkthrough.md`. FEEDBACK-01 waiver Done.
- [2026-09-06] US-OPS-OOM-001 merged (PR #25): PassthroughReranker so free-tier does not OOM on CrossEncoder load.
- [2026-09-06] DEPLOY-01 / US-OPS-DEMO-REPAIR-001 closed earlier same day.
