# Pilot Rehearsal Log

Track each rehearsal run here so trends are visible before clinician handoff.

## Run template

- Date/time:
- Operator:
- Branch/commit:
- Environment:
  - Docker Desktop version:
  - OS:
- Commands run:
  - `scripts\health-check-clinician.bat`
  - `scripts\run-pilot-rehearsal.bat`

## Results summary

- Health check: `PASS` / `FAIL`
- Rehearsal overall: `PASS` / `FAIL`
- Cases:
  - `pilot-001-lumbar-pain`: `PASS` / `FAIL` (latency ms: )
  - `pilot-002-ibs-anxiety`: `PASS` / `FAIL` (latency ms: )
  - `pilot-003-fatigue-sleep`: `PASS` / `FAIL` (latency ms: )
- Blocking issues found:
- Workarounds applied:

## Notes

- UX observations:
- Clinical content concerns:
- Follow-up actions (owner + due date):

---

## Example entry

- Date/time: 2026-04-17 10:30
- Operator: Internal QA
- Branch/commit: `main` / `17959fc`
- Environment:
  - Docker Desktop version: 4.x
  - OS: Windows 11
- Commands run:
  - `scripts\health-check-clinician.bat`
  - `scripts\run-pilot-rehearsal.bat`

## Results summary

- Health check: `PASS`
- Rehearsal overall: `PASS`
- Cases:
  - `pilot-001-lumbar-pain`: `PASS` (latency ms: 48176)
  - `pilot-002-ibs-anxiety`: `PASS` (latency ms: 28478)
  - `pilot-003-fatigue-sleep`: `PASS` (latency ms: 28401)
- Blocking issues found: none
- Workarounds applied: none

## Notes

- UX observations: intake and plan review flow understandable for pilot scenario.
- Clinical content concerns: to be validated with real clinician data next week.
- Follow-up actions (owner + due date): run one more rehearsal on clean Windows profile (owner: Andres, due: Monday).
