# Despliegue demo — Entrega final (Render)

Guía canónica para la **entrega final** del capstone. Misma topología que Entrega 2:

**Render Blueprint** = PostgreSQL 16 + Web Service (Docker API) + Static Site (SPA).

Documento base histórico: [`deploy-entrega2-demo.md`](deploy-entrega2-demo.md)  
Blueprint: [`../render.yaml`](../render.yaml)  
Plan: [`final-delivery-plan.md`](final-delivery-plan.md) (D2 locked → Render)

**No** usar Hetzner + Cloudflare Pages para esta entrega (eso queda como topología post-piloto en `holisticare_deployment_quickstart.md`).

---

## 1. Qué reutilizar de Entrega 2

| Pieza | Entrega 2 | Entrega final |
|-------|-----------|---------------|
| Hosting | Render Blueprint | **Igual** |
| DB | Render Postgres 16 (+ Neon fallback si falta `vector`) | **Igual** |
| API | Docker web service `holisticare-api` | **Igual** |
| SPA | Static Site + `VITE_API_BASE_URL` | **Igual** (`resolveApiBaseUrl` / US-OPS-SPA-HOST Done on `main`) |
| SPA routing | rewrite `/* → /index.html` + `frontend/public/_redirects` | **Igual** |
| Schema bootstrap | `psql` + `infra/init.sql` (manual) | **Igual** (+ patches nuevos si aplica, p.ej. memory bank / invites / `app_users`) |
| Corpus | `POST /rag/ingest` con `data/mock` | **Igual** (sintético) |

---

## 2. Deltas respecto a Entrega 2 (producto actual)

Desde Entrega 2 el producto añadió auth “prod” (Sprints 13–14). Para la demo académica en Render:

| Tema | Recomendación para entrega final |
|------|----------------------------------|
| `ALLOW_DEV_AUTH` | Mantener **`true`** en el Blueprint demo (mismo flujo TA: “Entrar desarrollo”), *y* documentar login username/password con usuario seed |
| Clinician seed | Ejecutar `backend/scripts/seed_clinician.py` (o equivalente) tras schema |
| Patient diary | Invite redeem (`US-DIARY-AUTH-PROD`) además del path clinician-proxy |
| Anonymization | Deploy **después** de merge de **US-PRIV-001** |
| Cold start | Tier free ~50 s+; aviso en README / Typeform |

Si el tutor exige `ALLOW_DEV_AUTH=false` en la URL pública, cambiar solo esa variable, seed clinician, y demo vía `/auth/login` (no `/auth/dev-login`).

---

## 3. Pasos (resumen — detalle en Entrega 2)

1. **New → Blueprint** en Render; conectar repo; rama de entrega final; detectar `render.yaml`.
2. Setear secretos en **holisticare-api**: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `CORS_ORIGINS` (URL exacta del Static Site).
3. Setear en **holisticare-frontend**: `VITE_API_BASE_URL=https://<api-host>`.
4. Aplicar schema: `CREATE EXTENSION vector;` + `infra/init.sql` (+ patches listados en `docs/setup.md` si no están en init).
5. Seed clinician; ingest `data/mock`.
6. Verificar: `curl https://<api>/health` → 200; abrir SPA; login; generar + aprobar plan.
7. Pegar URLs en README sección proyecto / notas de entrega.

Troubleshooting: misma tabla de [`deploy-entrega2-demo.md`](deploy-entrega2-demo.md) §10 (CORS, cold start, SSL Postgres, schema missing).

---

## 4. Evidencia para DoD (DEPLOY-01)

- [x] Frontend público responde (SPA carga).
- [x] API `/health` pública 200.
- [x] CORS permite origen del Static Site.
- [ ] Flujo demo: login → intake → generar plan → review → approve/reject.
- [x] URLs documentadas en README / paquete de entrega.
- [x] Nota de cold start free tier si aplica.

**Live (2026-07-26):** SPA `https://holisticare-frontend.onrender.com` · API `https://holisticare-api.onrender.com` · branch `main`.

---

## 6. CI-gated CD (GitHub Actions)

After Sprint 16, deploys are owned by [`.github/workflows/cd-render.yml`](../.github/workflows/cd-render.yml):

1. **CI** workflow must succeed on a **push** to `main`.
2. **CD Render** triggers API + Static Site deploys via Render API (clear cache).
3. Waits until both are `live`, then runs `backend/scripts/smoke_public_demo.py` (health, SPA, CORS, `dev-login`).

**Render `autoDeploy` is OFF** on both services so pushes do not double-deploy.

### One-time GitHub secret

Repo → **Settings → Secrets and variables → Actions** → add:

| Secret | Value |
|--------|--------|
| `RENDER_API_KEY` | Render Account API key (**rotate** if it was pasted in chat) |
| `RENDER_API_SERVICE_ID` | optional — defaults to `srv-d98oj6mcjfls73f14aug` |
| `RENDER_FE_SERVICE_ID` | optional — defaults to `srv-d98oiiecjfls73f12u2g` |

Manual run: Actions → **CD Render** → **Run workflow**.

Local smoke:

```bash
cd backend
PYTHONPATH=. python scripts/smoke_public_demo.py
```

---

## 5. Relación con US-OPS-SPA-HOST

Código Must (Done en Sprint 16):

- `frontend/src/utils/apiBaseUrl.js` + `api.js` usan `VITE_API_BASE_URL` con fallback `/api`.
- `frontend/public/_redirects` para SPA deep links.
- `render.yaml` versionado en raíz (este repo).
