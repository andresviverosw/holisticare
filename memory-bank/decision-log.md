# Decision Log

## Decision 1
- **Date:** [Date]
- **Context:** [Context]
- **Decision:** [Decision]
- **Alternatives Considered:** [Alternatives]
- **Consequences:** [Consequences]

## Decision 2
- **Date:** [Date]
- **Context:** [Context]
- **Decision:** [Decision]
- **Alternatives Considered:** [Alternatives]
- **Consequences:** [Consequences]

## Sprint 14 — Clinician password login (not IdP / magic-link)
- **Date:** 2026-07-16
- **Author:** Planning Agent
- **Context:** After Sprint 13, patients can auth with ALLOW_DEV_AUTH=false; clinicians still need hand-minted JWTs or dev-login.
- **Decision:** Sprint 14 ships local app_users + bcrypt password login (`POST /auth/login`) and seed_clinician.py. JWT includes exp. No IdP, no clinician magic-link, no prod compose in this slice.
- **Alternatives Considered:**
  - Bundle docker-compose.prod (ops coupling)
  - Clinician invite/magic-link (bootstrap chicken-egg)
  - R4 mobile first (leaves clinician prod login broken)
- **Consequences:**
  - Unblocks clinician SPA in staging/production
  - Local credential store requires strong seed password + rotation ops
  - Compose overlay and JWT harden remain follow-ons

## Sprint 13 — Patient auth via invite-link (not OTP/IdP)
- **Date:** 2026-07-16
- **Author:** Planning Agent
- **Context:** After Sprint 12, `/diario` exists but patient login still depends on `ALLOW_DEV_AUTH` or UUID-as-password.
- **Decision:** Sprint 13 ships single-use opaque invite tokens (clinician creates, patient redeems → JWT with `exp`). No email/SMS provider, no clinic IdP, no OTP in this slice. Clinician copies link out-of-band.
- **Alternatives Considered:**
  - OTP email/SMS first (provider + PII/consent surface)
  - Clinic OIDC first (integration-heavy)
  - Prod compose only (turns off login without replacement)
  - R4 mobile first (leaves patient auth gap)
- **Consequences:**
  - Unblocks real patient diary with `ALLOW_DEV_AUTH=false`
  - Clinician prod login and compose overlay remain follow-ons
  - Invite leak risk mitigated by TTL + single-use + hash-at-rest

## Sprint 12 — Patient diary uses UUID-bound JWT (dev), not production IdP
- **Date:** 2026-07-16
- **Author:** Planning Agent
- **Context:** Next product slice after clinician-proxy diary; backend already requires patient `sub == patient_id`.
- **Decision:** Sprint 12 issues patient tokens only via extended `ALLOW_DEV_AUTH` login with UUID v4 `sub`, plus manual JWT paste. No magic links/OTP/IdP.
- **Alternatives Considered:**
  - Build invite-link auth first (larger scope, blocks diary UI)
  - Let patients type arbitrary patient_id (breaks server-side subject check / unsafe)
- **Consequences:**
  - Unblocks patient UI quickly for pilot/dev
  - Production auth tracked as `US-DIARY-AUTH-PROD`

## Sprint 11 — Clinician-proxy diary for R1-UI closeout
- **Date:** 2026-07-16
- **Author:** Planning Agent
- **Context:** US-DIARY-001/002 backend exists, but there is no patient UI or patient onboarding; analytics and prediction panels need diary series for pilot E2E.
- **Decision:** Sprint 11 ships **clinician-proxy** diary entry on the Dashboard (`US-DIARY-UI`). Patient self-serve route is deferred as `US-DIARY-UI-PATIENT`.
- **Alternatives Considered:**
  - Build patient auth + diary page first (higher risk, blocks analytics UI)
  - Seed diary only via scripts/API in pilot (no product UI, fails MVP DoD E2E)
- **Consequences:**
  - Unblocks US-ANLY-UI and pilot data entry quickly
  - Requires clear “practicante” labeling to avoid confusing proxy entries with patient self-report
  - True patient engagement remains a follow-on story

## Standardize Memory Bank MCP usage
- **Date:** 2026-04-07 12:18:31 PM
- **Author:** Unknown User
- **Context:** Memory Bank MCP is now enabled and should be the canonical continuity layer for active work state and security remediation tracking.
- **Decision:** Adopt memory-bank core files (product-context, active-context, progress, decision-log, system-patterns) and update them at the end of each meaningful implementation slice.
- **Alternatives Considered:** 
  - Use only docs folder for continuity
  - Rely on chat transcript continuity only
- **Consequences:** 
  - Improves session-to-session continuity and onboarding
  - Adds small process overhead to keep memory files current
