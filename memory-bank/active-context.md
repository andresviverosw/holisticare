# Current Context

## Ongoing Tasks

- **Sprint 14 merged** to `main` (PR #13).
- **Sprint 15 planning complete:** `docs/sprint-15.md` — US-OPS-PROD-COMPOSE ready for Development Agent.
- Locked: docker-compose.prod.yml + Caddyfile + .env.prod.example; force ALLOW_DEV_AUTH=false; CI contract tests.

## Known Issues

- Existing DBs need app_users / patient_diary_invites DDL when upgrading.
- SPA Pages host + GHCR publish may still be needed for a full live pilot.

## Next Steps

- Development Agent: prod compose + Caddy + env example → contract tests → docs → QA.
