# Current Context

## Ongoing Tasks

- **Final delivery plan Approved** (D1–D4 locked): `docs/final-delivery-plan.md`, `docs/sprint-16.md`.
- **D2 corrected/aligned:** public deploy = **Render Blueprint** (Entrega 2 parity) — NOT Hetzner/Cloudflare Pages for the capstone demo.
  - Canonical: `docs/deploy-final-demo.md`
  - Historical: `docs/deploy-entrega2-demo.md`
  - Blueprint: `render.yaml`
- **SYNTH-01 done (this branch):** end-to-end synthetic corpus + seed CLI for demo KPIs (`docs/synthetic-dataset-v1.md`).
- Next code: **US-PRIV-001** + **US-OPS-SPA-HOST** (`VITE_API_BASE_URL` reintroduce from entrega2).
- Companion Must: **DEPLOY-01** on Render, Phase 1/3 docs, RAG eval, public demo, feedback artifact.

## Known Issues

- On `main`, SPA still hardcodes `baseURL: "/api"` — blocks Render Static Site until US-OPS-SPA-HOST.
- Phase 3 privacy doc and Phase 1 §7 FR/NFR tables are still stubs.
- Raw intake JSON + `patient_id` can still reach Claude/OpenAI until US-PRIV-001.
- Render free tier cold starts (~50s+) — document for TA.

## Next Steps

1. Development: US-PRIV-001 TDD.
2. Development: US-OPS-SPA-HOST TDD (restore `VITE_API_BASE_URL` pattern).
3. Ops: DEPLOY-01 via Render Blueprint after SPA base URL merges.
4. Planning: DOC-CLOSE Phase 3 + FR/NFR in parallel.
5. Confirm with owner if demo keeps `ALLOW_DEV_AUTH=true` (Entrega 2 default) vs false + seeded login only.
