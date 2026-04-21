# HolistiCare Clinician Quickstart (Windows)

This guide is for trying HolistiCare locally on a clinician computer.

## 1) What to install

Required:
- Docker Desktop for Windows (includes Docker Compose v2)

Optional (only for updates from Git):
- Git for Windows

You do not need to install Python, Node.js, PostgreSQL, or pgvector manually.

## 2) First-time setup

1. Install Docker Desktop and open it once.
2. Clone this repository (or unzip the provided package).
3. In the project root, copy `.env.clinician.example` to `.env`.
4. Edit `.env` and set at least one valid provider key:
   - `ANTHROPIC_API_KEY`, or
   - `OPENAI_API_KEY`

## 3) Start the app

From the project root, run:

`scripts\start-clinician.bat`

The script now:
- warns if no `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` is configured in `.env`,
- starts containers,
- runs a quick health check automatically.

Open:
- Frontend: http://localhost:5173
- Backend docs: http://localhost:8000/docs

## 4) Stop the app

Run:

`scripts\stop-clinician.bat`

## 5) Update to latest version

If the install was cloned with Git, run:

`scripts\update-clinician.bat`

If it was provided as a zip package, replace with a new package version from the team.

## 6) Run health check manually

If you want to verify readiness without restarting containers:

`scripts\health-check-clinician.bat`

## 7) Use prediction and recommendations (new)

In Dashboard:

1. Select or generate a valid patient UUID.
2. Click **Calcular trayectoria** in the "Predicción de recuperación (US-PRED-001)" panel.
3. Click **Cargar recomendaciones** in the "Recomendaciones clínicas (US-PRED-002)" panel.
4. Use results as clinician support, not as autonomous decisions.

What to expect:
- **Trajectory status**: available or insufficient data.
- **Recommendation status**: recommendations available or insufficient data.
- **Safety notes**: highlighted when projected pain suggests higher clinical risk.

Pilot validation points for next week:
- Confirm trajectory label matches clinician judgment on at least 3 real cases.
- Confirm recommendations are actionable and safe in real workflow.
- Record mismatches or unclear rationale in the pilot feedback form.

## 8) Troubleshooting

- If startup fails with Docker errors, make sure Docker Desktop is running.
- If startup warns about missing keys, add `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in `.env`.
- If AI plan generation fails, verify `.env` API keys are valid and have quota.
- If port conflicts occur (5432, 8000, 5173), close apps using those ports or edit `docker-compose.yml` port mappings.
