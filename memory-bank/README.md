# Memory Bank

This folder is the project memory bank used by `memory-bank-mcp`.

## Files

- `project-brief.md` — stable project identity and goals
- `active-context.md` — current focus, blockers, and next steps
- `progress.md` — dated implementation log
- `decisions.md` — architecture/security decisions with rationale

## How to use in Cursor

1. Open Cursor command palette and run `MCP: List Available Servers`.
2. Confirm `memory-bank-mcp` is active.
3. Use MCP commands, for example:
   - initialize memory bank files
   - read/write `active-context.md`
   - log decisions and progress items

## Update discipline

- Update `active-context.md` at session start/end.
- Append to `progress.md` after each completed slice.
- Record design/security decisions in `decisions.md`.
