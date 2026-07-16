# Current Context

## Ongoing Tasks

- **Sprint 13 complete / QA PASS:** US-DIARY-AUTH-PROD — invite-link patient auth.
- PR: https://github.com/andresviverosw/holisticare/pull/11

## Known Issues

- Existing deployments must apply `patient_diary_invites` DDL from `infra/init.sql`.
- Clinician login when `ALLOW_DEV_AUTH=false` still needs `US-AUTH-CLINICIAN-PROD`.
- Prod compose overlay still follow-on.

## Next Steps

- Planning Agent: merge PR #11; prioritize clinician prod auth, prod compose, or R4 mobile.
