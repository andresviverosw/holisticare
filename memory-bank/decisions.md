# Decisions

## 2026-04-07 — Use Memory Bank MCP for project memory

### Context

Project context and security remediation details were spread across chat and docs, making continuity slower between sessions.

### Decision

Adopt `@movibe/memory-bank-mcp` and store memory files in repository folder `memory-bank/`, configured via `.cursor/mcp.json`.

### Consequences

- Faster onboarding/resume for future work.
- Centralized context snapshots (`active-context`, `progress`, `decisions`).
- Requires team discipline to keep memory files updated.
