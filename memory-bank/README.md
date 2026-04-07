# Memory Bank

This folder is the **only** project memory bank used by `memory-bank-mcp`. It lives at the repository root (`memory-bank/`). Do **not** create a second nested folder such as `memory-bank/memory-bank/` — that was an accidental duplicate from an earlier MCP bootstrap and has been removed.

## Files

- `project-brief.md` — stable project identity and goals
- `product-context.md` — product/overview notes (keep aligned with reality over time)
- `active-context.md` — current focus, blockers, and next steps
- `progress.md` — dated implementation log
- `decision-log.md` — structured decisions (MCP-friendly filename)
- `decisions.md` — additional decision notes / narrative log
- `system-patterns.md` — recurring technical patterns

## How to use in Cursor

1. Open Cursor command palette and run `MCP: List Available Servers`.
2. Confirm `memory-bank-mcp` is active (workspace `.cursor/mcp.json` uses `--folder memory-bank` and `--path` `.`).
3. Use MCP commands, for example:
   - initialize memory bank files
   - read/write `active-context.md`
   - log decisions and progress items

## Update discipline

- Update `active-context.md` at session start/end.
- Append to `progress.md` after each completed slice.
- Record design/security decisions in `decision-log.md` and/or `decisions.md`.
- For detailed security remediation status, prefer `docs/09-security-audit-and-todos.md` as the source of truth; mirror short summaries here when useful.
