# Pilot Rehearsal Checklist (Pre-Clinician)

Use this checklist to validate pilot readiness with synthetic cases before clinician handoff.

## 1) Preconditions

- Docker Desktop is running.
- `.env` exists and has at least one valid AI key (`ANTHROPIC_API_KEY` or `OPENAI_API_KEY`).
- Backend, DB, and frontend containers can start.

## 2) Baseline health

Run:

`scripts\health-check-clinician.bat`

Expected:
- `holisticare_db`, `holisticare_backend`, `holisticare_frontend` are `Up`.
- `http://localhost:8000/health`, `/docs`, and `http://localhost:5173` return `200`.
- API smoke script completes without errors.

## 3) Synthetic pilot cases

Dataset file:

`backend/data/pilot/cases.json`

Current target set:
- `pilot-001-lumbar-pain`
- `pilot-002-ibs-anxiety`
- `pilot-003-fatigue-sleep`

## 4) Rehearsal run

Run:

`scripts\run-pilot-rehearsal.bat`

The runner executes each case against `POST /rag/plan/generate` and validates:
- HTTP `200`
- `status = pending_review`
- at least one generated week
- `insufficient_evidence = false`

## 5) Manual UX verification

For at least one case:
- Open frontend at `http://localhost:5173`.
- Confirm intake data can be entered without confusion.
- Generate and review plan.
- Confirm plan status and content are understandable for practitioner review.

## 6) Exit criteria for next-week pilot

- All synthetic cases pass in the rehearsal runner.
- No blocking startup or plan-generation errors.
- No critical UX confusion in intake + plan review flow.
- Known limitations documented and shared with clinician.

## 7) Clinician walkthrough checklist (final GO/NO-GO evidence)

Use one real-case walkthrough (or closest available non-synthetic case) and capture notes in `docs/pilot-go-no-go.md`.

- Open Dashboard and complete intake fields without facilitator intervention.
- Run **Calcular trayectoria** and confirm status/result are clinically interpretable.
- Run **Cargar recomendaciones** and confirm suggested actions are understandable and actionable.
- Compare trajectory/recommendations against clinician judgment:
  - Mark `Aligned`, `Partially aligned`, or `Not aligned`.
  - Record one reason when not fully aligned.
- Validate safety notes:
  - Confirm they appear when risk is perceived.
  - Confirm wording is clear and non-ambiguous.
- Review plan output and confirm practitioner control is preserved (`pending_review`, manual approve/reject).
- Log final verdict:
  - `Ready for pilot with accepted risks`, or
  - `Not ready` with explicit blocker and owner.
