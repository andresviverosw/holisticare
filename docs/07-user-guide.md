# HolistiCare User Guide

## Audience and scope

This guide is for clinicians and (pilot/dev) patients using the current web app MVP.

Current UI modules:
- Login (`/login`)
- Dashboard: AI plan generation (`/dashboard`) — also risk flags, clinician-proxy diary, progress/plateaus, session logging
- Patient diary (`/diario`) — self-serve daily check-ins (US-DIARY-UI-PATIENT)
- Plan review and approval (`/plan/:planId`)
- Plan sources (`/plan/:planId/sources`)
- Knowledge base browser (`/chunks`)

## Before you start

You need:
- Running services (`docker compose up -d --build`)
- Backend reachable at `http://localhost:8000`
- Frontend reachable at `http://localhost:5173`
- A valid clinician/admin or patient JWT, or dev login enabled (`ALLOW_DEV_AUTH=true`)

## Login

1. Open `http://localhost:5173/login`.
2. Choose one:
   - **Personal clínico (producción/staging):** enter **Usuario** / **Contraseña** and click **`Entrar`**. Requires a seeded account (`seed_clinician.py`). Works with `ALLOW_DEV_AUTH=false`.
   - **Invitación al diario (paciente)**: open the clinician-shared link (`/login?invite=…`) or paste the invite token and click **`Entrar con invitación`**.
   - **Dev login (clínico)**: click `Entrar (desarrollo — clínico)` (works only when backend allows dev auth).
   - **Dev login (paciente)**: paste the patient’s UUID v4, then click `Entrar (desarrollo — paciente)`. Opens `/diario` (dev/pilot only).
   - **Manual token**: paste a JWT in `Pegar token JWT (Bearer)` and submit.

If login fails, an actionable message is shown (e.g. wrong password, invalid/expired invite).

### Seed a clinician account (ops)

```bash
# With backend env / compose network available:
SEED_CLINICIAN_USERNAME=clinician \
SEED_CLINICIAN_PASSWORD='use-a-strong-password' \
SEED_CLINICIAN_ROLE=clinician \
python -m scripts.seed_clinician
```

Idempotent: re-running updates the password/role for the same username. Never commit real passwords. Apply `app_users` DDL from `infra/init.sql` on existing databases first.

### Invite patient to diary (clinician) — US-DIARY-AUTH-PROD

1. On the Dashboard, set a valid patient UUID v4.
2. Click **`Invitar al diario`**.
3. Copy the one-time link and share it out-of-band (WhatsApp/email outside the app).
4. The patient opens the link once; it expires after the configured TTL (default 7 days) or after first use.

Prefer invites over sharing the raw UUID as a login secret.

## Patient diary (`/diario`)

1. Sign in as patient (invite redeem, or dev UUID login / patient JWT).
2. Confirm the read-only patient ID matches the invited patient.
3. Enter date and scores (dolor / sueño / ánimo / función, 0–10); optional notes.
4. Click **`Guardar check-in`**. Same-day entries upsert.
5. Use **`Actualizar`** to refresh recent history.

Patients cannot open clinician Dashboard routes; clinicians cannot stay on `/diario` (proxy diary remains on the Dashboard).

## Generate a treatment plan

1. Open `Dashboard`.
2. Set **patient ID** (RFC-4122 UUID version 4):
   - Click **`Nuevo paciente`** to generate a new id, or paste an existing id, or pick from **`Pacientes recientes`** (stored in this browser) and then **`Cargar intake guardado`** if you need the saved intake from the server.
   - Use **`Copiar ID`** to copy the current id to the clipboard.
3. Fill the structured intake form (or **`Cargar intake guardado`** after selecting an id).
4. Set **`Modalidades disponibles`** and **`Idioma del plan`**.
5. Optionally **`Guardar intake`** before generating.
6. Click **`Generar plan IA`**.

Invalid UUIDs are rejected before save/load/generate; the field must be a valid **version 4** UUID (same rules as the backend).

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

### Plan library (memory bank)

After a plan is **approved**, you can **Guardar en biblioteca** on the plan review screen (title + optional tags). That stores a **de-identified** copy for your team.

On the **Dashboard**, **Biblioteca de plantillas** lists saved templates; use **Usar como borrador** to create a **new** `pending_review` plan for the **current patient ID** (you must review and approve again).

## Continuity panels (Sprint 11)

On the **Dashboard**, with a valid patient UUID:

1. **Banderas de riesgo** — after **Guardar** / **Cargar intake** or **Ver riesgos**.
2. **Registro de diario (practicante)** — enter daily scores (proxy for patient self-report in the pilot).
3. **Progreso** — load outcome trends and plateau/worsening flags.
4. **Sesión clínica** — log interventions, optional **Sugerir nota**, then **Guardar sesión**.

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

