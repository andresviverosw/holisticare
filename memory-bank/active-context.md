# Current Context

## Ongoing Tasks

- Merge DEMO-01 PR if still open; merge US-OPS-OOM-001 passthrough fix and redeploy Render
- Track D: tag capstone-final + README confirmation
## Known Issues

- Free-tier cold start still ~50–60s on first `/health`; 5s health-check alerts during restart are expected noise
- LLM generate on free Render may still 502 near ~100s (proxy timeout) even after OOM fix
## Next Steps

- Deploy passthrough reranker fix to public API; re-smoke DEMO-01 memory-bank path
- Track D packaging after DEMO-01 merge
## Current Session Notes

- [2026-09-06] Render OOM after DEMO-01: root cause was CrossEncoder load despite `RERANKER_BACKEND=passthrough`. Fix: `PassthroughReranker` + factory wiring (US-OPS-OOM-001).
- [2026-09-06] DEPLOY-01 / US-OPS-DEMO-REPAIR-001 closeout: public `/health`+`/ready` 200, SPA 200, CORS OK, authenticated `/rag/chunks` 200.
