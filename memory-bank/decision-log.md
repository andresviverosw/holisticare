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
