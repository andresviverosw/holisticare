# Pilot Go/No-Go Criteria

Use this checklist 24-48 hours before clinician handoff to decide if the pilot can proceed.

## Scope

- Environment: clinician local install with Docker Desktop.
- Validation inputs: synthetic pilot cases (`backend/data/pilot/cases.json`) and one manual UI walkthrough.
- Objective: confirm stable startup and safe intake-to-plan flow.

## Go criteria (all required)

1. **Startup reliability**
   - `scripts\start-clinician.bat` completes without blocking errors.
   - `scripts\health-check-clinician.bat` passes (containers up, HTTP 200 checks, API smoke green).

2. **Rehearsal consistency**
   - `scripts\run-pilot-rehearsal.bat` passes for all synthetic cases on two consecutive runs.
   - No case returns `insufficient_evidence = true`.
   - Each case returns `status = pending_review` and at least one generated week.

3. **UX minimum quality**
   - Intake can be completed without ambiguity for all mandatory fields.
   - Plan Review screen shows generated content and status clearly.
   - Error messages are actionable (missing API key, startup failure, port conflict).

4. **Operational readiness**
   - Known limitations are documented and shared with clinician.
   - Owner and response window for pilot-day incidents are defined.
   - Rollback path is known (`scripts\stop-clinician.bat`, previous stable commit/tag available).

## No-go triggers (any one blocks pilot)

- Startup fails in clean-machine run with official quickstart.
- Any synthetic case fails the rehearsal runner.
- Critical UX confusion in intake or plan review that prevents normal use.
- Unresolved blocker bug with no workaround.

## Decision log

- Decision date:
- Decision owner:
- Result: `GO` / `NO-GO`
- Evidence references:
  - Last successful rehearsal run:
  - Last health-check run:
  - Manual UI walkthrough notes:
- Open risks accepted for pilot:
