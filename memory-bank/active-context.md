# Current Context

## Ongoing Tasks

- **Sprint 12 merged** to `main` (PR #9).
- **Sprint 13 planning complete:** `docs/sprint-13.md` — US-DIARY-AUTH-PROD ready for Development Agent.
- Locked: single-use invite link → patient JWT with `exp`; no OTP/IdP/email send this slice.

## Known Issues

- Clinician login when `ALLOW_DEV_AUTH=false` still needs `US-AUTH-CLINICIAN-PROD`.
- Prod compose overlay (`US-OPS-PROD-COMPOSE`) still not in repo.
- Pilot GO/NO-GO optional/deferred.

## Next Steps

- Development Agent: TDD invite model/service → redeem API → Dashboard/Login SPA → QA.
