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
