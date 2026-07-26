# FEEDBACK-01 — Clinician feedback / synthetic-demo waiver

| Field | Value |
|-------|--------|
| Date | 2026-07-26 |
| Owner | Andrés V (product owner) |
| Related | Phase 1 DoD item 6; final-delivery-plan D4; [`pilot-clinician-feedback-form.md`](pilot-clinician-feedback-form.md) |

## Decision for master’s submission

**Documented waiver (synthetic-only validation)** — pending full clinical alignment session with collaborating practitioner.

Per locked decision **D4**, the capstone may ship with either a completed clinician feedback form **or** an explicit “pending clinical alignment” appendix. This file is that appendix.

## What was validated without live clinician sign-off

- End-to-end MVP loop on **synthetic** patients (SYNTH-01 corpus + automated tests / Playwright suites for Sprints 11–14).
- NOM-024-style gate: AI plans remain `pending_review` until explicit approve/reject.
- Privacy egress scrub (US-PRIV-001) and public-demo ops path (US-OPS-SPA-HOST / DEPLOY-01).

## What remains for post-submission clinical alignment

1. Schedule structured review using [`pilot-clinician-feedback-form.md`](pilot-clinician-feedback-form.md).
2. Capture GO/NO-GO for pilot expansion (`PILOT-GO`).
3. Review US-PRED outputs for clinical plausibility before any real-PHI deployment.

## Explicit non-claims

- This waiver does **not** assert that generated plans are clinically validated for real patients.
- HolistiCare remains a **decision-support** tool; licensed practitioners retain treatment authority.
- No real patient PHI was used in development or this submission package.
