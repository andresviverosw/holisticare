# Current Context

## Ongoing Tasks

- **Final delivery plan Approved** (D1–D4 locked 2026-07-25): `docs/final-delivery-plan.md`, `docs/sprint-16.md`.
- **D2 locked:** public hybrid deployment (Hetzner/VPS + Neon + Cloudflare Pages), same approach as second delivery — not local-demo-only.
- Next code: **US-PRIV-001** (LLM egress anonymization) and **US-OPS-SPA-HOST** (`VITE_API_BASE_URL`).
- Companion Must: **DEPLOY-01**, Phase 1 FR/NFR + Phase 3 privacy, RAG eval report, public demo, clinician feedback artifact.

## Known Issues

- Replace `api.example.com` in `Caddyfile` before first LE issue (DEPLOY-01).
- SPA still hardcodes `baseURL: "/api"` — blocks Cloudflare Pages until US-OPS-SPA-HOST.
- Phase 3 privacy doc and Phase 1 §7 FR/NFR tables are still stubs (academic DoD gap).
- Raw intake JSON + `patient_id` can still reach Claude/OpenAI (R-02) until US-PRIV-001.

## Next Steps

1. Development: US-PRIV-001 TDD (scrubber + pipeline choke point).
2. Development: US-OPS-SPA-HOST TDD (API base URL helper + axios wiring).
3. Planning: DOC-CLOSE Phase 3 + FR/NFR in parallel.
4. Ops: DEPLOY-01 after SPA base URL is mergeable.
5. QA: anonymization + SPA base URL + public smoke + regression; then package/tag.
