# HolistiCare User Guide

## Audience and scope

This guide is for clinicians using the current web app MVP.

Current UI modules:
- Login (`/login`)
- Dashboard: AI plan generation (`/dashboard`)
- Plan review and approval (`/plan/:planId`)
- Plan sources (`/plan/:planId/sources`)
- Knowledge base browser (`/chunks`)

## Before you start

You need:
- Running services (`docker compose up -d --build`)
- Backend reachable at `http://localhost:8000`
- Frontend reachable at `http://localhost:5173`
- A valid clinician/admin JWT, or dev login enabled (`ALLOW_DEV_AUTH=true`)

## Login

1. Open `http://localhost:5173/login`.
2. Choose one:
   - **Dev login**: click `Entrar (desarrollo — clínico)` (works only when backend allows dev auth).
   - **Manual token**: paste a JWT in `Pegar token JWT (Bearer)` and submit.

If login fails, an actionable message is shown (e.g. auth disabled, invalid token).

## Generate a treatment plan

1. Open `Dashboard`.
2. Fill:
   - `ID del paciente (UUID v4)`
   - `Intake JSON (generic_holistic_v0)`
   - `Modalidades disponibles`
   - `Idioma del plan`
3. Click `Generar plan IA`.

Result:
- On success, app navigates to plan review.
- On failure, errors are shown clearly (including `502/503` model/provider failures).

## Review and approve/reject plan

1. In plan review, inspect:
   - Confidence note
   - Retrieval metadata
   - Weekly goals/therapies
   - Contraindications
   - Citations
2. Add optional practitioner notes.
3. Click:
   - `✓ Aprobar plan`, or
   - `✕ Rechazar`.

Behavior:
- Plans are generated as `pending_review`.
- Approval/rejection updates status and is persisted.

## View source evidence

From plan review, click `Ver contenido completo de las fuentes`.

You can inspect:
- `REF` citation IDs
- Source text chunk
- Language, evidence level, contraindication flag
- Source file/page

## Browse indexed knowledge chunks

Open `/chunks` to:
- Filter by therapy, language, contraindication
- Verify ingestion output and retrieval corpus

## Typical issues and what to do

- **`503` provider unavailable/quota/auth**
  - Check Anthropic/OpenAI keys and billing.
  - Retry after a short wait for quota propagation.
- **`502` invalid model JSON**
  - Retry; if persistent, check backend logs for generation output parsing issue.
- **No retrieved evidence / insufficient plan**
  - Re-run ingestion and verify chunk coverage in `/chunks`.
- **Unauthorized (`401/403`)**
  - Re-login with a valid token and correct role.

## Minimal smoke flow (manual)

1. Login.
2. Generate plan from Dashboard sample intake.
3. Open generated plan.
4. Approve/reject once.
5. Open plan sources.
6. Open chunk browser and filter.

