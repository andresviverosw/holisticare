# Mobile Strategy v0 (Planning Draft)

## Objective

Define a practical path to offer HolistiCare on mobile devices without destabilizing the current web MVP.

## Why now

- Clinician demand exists for phone/tablet access.
- Pilot feedback is expected to include mobility and in-session usability constraints.
- Early planning avoids expensive rewrites later.

## Product scope framing

### Primary users (phase 1)

- Clinician only (no patient app in phase 1).

### Priority workflows for mobile

1. Open app quickly and authenticate.
2. Select recent patient.
3. Review latest approved plan.
4. Trigger plan generation and inspect result summary.
5. Add short practitioner notes.

### Out of scope (phase 1)

- Full administrative workflows.
- Large corpus operations/ingestion.
- Advanced analytics editing.
- Offline-first sync and push notifications.

## Delivery options

## Option A - Responsive web + PWA shell (recommended first)

- Reuse existing frontend and backend.
- Improve responsive layouts for key screens.
- Add installable PWA basics (manifest + icons + minimal offline shell).
- Fastest route, lowest engineering risk.

Pros:
- Lowest cost and fastest validation.
- One codebase.
- Immediate pilot learning.

Cons:
- Limited native capabilities.
- Offline behavior remains basic.

## Option B - React Native / Expo companion app

- Build dedicated app UI using existing APIs.
- Better control over mobile UX and native integrations.

Pros:
- Better mobile ergonomics and native features.
- Future-ready for notifications/camera integrations.

Cons:
- New app codebase and release pipeline.
- Higher maintenance cost.

## Option C - Fully native iOS/Android

- Maximum control, highest effort.
- Not recommended for current stage.

## Recommendation

Use **Option A (responsive + PWA)** as phase 1 and define objective adoption/quality thresholds to justify Option B.

## Architecture and platform implications

- Keep backend API contracts stable and UI-agnostic.
- Preserve JWT/auth rules; harden session handling on mobile browsers.
- Ensure responsive behavior in:
  - `Dashboard` (intake + generation),
  - `PlanReview`,
  - recent patient selection.
- Add mobile performance budget for first render and interaction.

## Security and compliance checkpoints

- Enforce short session timeout for mobile context.
- Avoid storing PHI in insecure local caches.
- Define lost-device procedure for clinician accounts.
- Ensure HTTPS/TLS for any hosted mobile access.

## Starter backlog (proposed)

| Story ID | Epic | As a | I want | So that | Priority | Estimate | Status |
|----------|------|------|--------|---------|----------|----------|--------|
| US-MOB-001 | Mobile clinician access | Clinician | to use Dashboard and Plan Review comfortably on a phone | I can review/generate plans during consultation without laptop dependency | Should | M | Planned |
| US-MOB-002 | Mobile clinician access | Clinician | to install the app as a PWA with stable startup and session continuity | I can access HolistiCare quickly from my home screen | Should | M | Planned |
| US-MOB-003 | Mobile clinician access | Clinician | to complete a fast "review + approve/reject + note" flow on mobile | I can finalize decisions in under 2 minutes | Should | M | Planned |

## Acceptance criteria (initial draft)

### US-MOB-001
- Given viewport widths between 360px and 1024px, when using Dashboard and Plan Review, then no critical controls are clipped or unreachable.
- Given touch interaction, when selecting recent patients and triggering plan generation, then controls are usable without precision cursor.
- Given a mobile browser session, when a recoverable API error occurs, then user sees a concise actionable message.

### US-MOB-002
- Given a supported mobile browser, when user installs PWA, then app launches from home screen with branded icon/name.
- Given temporary network interruption, when app shell is opened, then user sees deterministic offline/unavailable messaging (no blank screen).
- Given active authenticated session, when app is reopened within timeout window, then session behavior is predictable and secure.

### US-MOB-003
- Given an existing generated plan, when clinician opens mobile Plan Review, then summary/status/citations are readable without horizontal scrolling.
- Given clinician chooses approve or reject, when action is submitted, then status update is confirmed with clear success/failure feedback.
- Given clinician adds a short note, when saved, then note persists and is retrievable from standard workflow.

## Technical spikes before implementation

1. Responsive audit spike (Dashboard + PlanReview component map and breakpoints).
2. PWA feasibility spike (manifest/service worker strategy and cache boundaries).
3. Mobile auth/session spike (token storage/session expiration UX).

## Milestones

### M1 - Decision gate (1 week)
- Confirm mobile phase-1 workflows and non-goals with clinician.
- Finalize option selection and success metrics.

### M2 - MVP mobile readiness (1-2 sprints)
- Deliver US-MOB-001 and US-MOB-002.
- Run internal mobile smoke and clinician mini-pilot.

### M3 - Clinical efficiency slice (next sprint)
- Deliver US-MOB-003 and iterate from pilot feedback.

## Go/No-Go for moving to React Native (Option B)

Consider Option B only if at least one condition is true after phase 1:
- Repeated UX constraints cannot be solved acceptably in responsive web.
- Native capabilities become required (push, deeper device integration, robust offline).
- Mobile adoption and usage frequency justify dual-codebase cost.
