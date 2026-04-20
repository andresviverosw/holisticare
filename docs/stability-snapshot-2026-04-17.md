# Stability Snapshot - 2026-04-17

This note captures the CI and test hardening completed on 2026-04-17.

## Scope completed

- Frontend browser E2E introduced with Playwright and wired into CI.
- Backend AI quality smoke introduced and wired into CI.
- CI reliability hardened for env/bootstrap/parser/runtime edge cases discovered during rollout.

## Current CI quality gates

- `backend-tests` (pytest)
- `frontend-checks` (eslint, vitest, playwright smoke, vite build)
- `security-audit` (pip-audit, bandit, npm audit; advisory toggle via `SECURITY_AUDIT_ADVISORY=true`)
- `ai-quality-smoke` (blocking by default; advisory toggle via `AI_QUALITY_SMOKE_ADVISORY=true`)

## AI smoke operational notes

- Workflow prepares `.env` from `.env.example`.
- `OPENAI_API_KEY` is injected from GitHub Actions secret when present.
- CI ingests a minimal corpus from `backend/data/ci_smoke` before smoke checks.
- For CI stability, `MIN_EVIDENCE_LEVEL=expert_opinion` is enforced in generated `.env`.
- CI smoke runs with `--allow-insufficient-evidence` to warn instead of failing on constrained corpus retrieval behavior.

## Known caveats

- AI smoke in CI remains a contract/sanity signal, not full clinical quality assurance.
- Citation strictness is currently mixed by case expectations; tighten gradually as CI corpus expands.
- Local developer runs should prefer strict mode (without `--allow-insufficient-evidence`) when validating meaningful corpus states.

## Next hardening opportunities

- Persist AI smoke summary artifacts for trend visibility.
- Expand `backend/data/ci_smoke` references to reduce insufficient-evidence warnings.
- Add one additional Playwright E2E for intake validation edge path.
