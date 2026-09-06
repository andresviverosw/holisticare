# Sprint 18 — Clinician mobile shell + cold-start UX

| Field | Value |
|-------|--------|
| Length | Short product slice (post Sprint 17) |
| Primary stories | **US-MOB-001**, **US-UX-COLDSTART-001** |
| Companion | Light Plan Review mobile polish toward **US-MOB-003** (approve path usable on phone) |
| Deferred | **US-MOB-002** (PWA install/offline shell) — still future |
| Priority | Should (clinician pilot feedback) |
| Owner | Planning → Development (TDD) → QA |
| Status | **Done** (code + unit/e2e evidence) |
| Source | Clinician counterpart demo + phone screenshot (sidebar crush + slow “Entrar desarrollo”) |

## Problem statement

1. Clinician shell (`Layout`) uses a fixed `w-60` sidebar with no breakpoints. On ~390px phones the main column is unusable (matches US-MOB-001 AC failure).
2. Public Render free-tier cold starts make `POST /auth/dev-login` feel stuck on “Conectando…” with no explanation.

## Scope

| ID | Work | Exit criteria |
|----|------|---------------|
| **US-MOB-001** | Responsive clinician nav: hamburger + drawer &lt;768px; permanent sidebar ≥768px; Dashboard/Plan Review not clipped | No critical controls clipped at 360–767px; touch targets usable |
| **US-UX-COLDSTART-001** | Warm `/health` on login mount; show Spanish cold-start hint after ~2.5s while auth awaits | Unit tests for hint threshold; login UX shows hint during slow API |
| **US-MOB-003** (partial) | Ensure approve/reject controls remain reachable after layout fix + page padding | Smoke e2e at mobile viewport can open Plan Review |

## Out of scope

- PWA manifest / service worker (`US-MOB-002`)
- Paid Render always-on (ops cost decision)
- Native / React Native

## Test intent

- Unit: `coldStartFeedback`, `mobileNav` helpers
- E2E: login → dashboard at iPhone-sized viewport; menu toggles; main content visible
- Regression: existing clinician-smoke still green

## Handoff

- Backlog item ID: US-MOB-001 + US-UX-COLDSTART-001
- Next owner: Development Agent
