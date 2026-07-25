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
| SPA | Static Site + `VITE_API_BASE_URL` | **Igual** (re-aplicar en `main` — hoy `api.js` hardcodea `/api`) |
| SPA routing | rewrite `/* → /index.html` + `frontend/public/_redirects` | **Igual** |
| Schema bootstrap | `psql` + `infra/init.sql` (manual) | **Igual** (+ patches nuevos si aplica, p.ej. memory bank / invites / `app_users`) |
| Corpus | `POST /rag/ingest` con `data/mock` | **Igual** (sintético) |

---

## 2. Deltas respecto a Entrega 2 (producto actual)

Desde Entrega 2 el producto añadió auth “prod” (Sprints 13–14). Para la demo académica en Render:

| Tema | Decisión bloqueada (2026-07-25) |
|------|----------------------------------|
| `ALLOW_DEV_AUTH` | **`true`** en el Blueprint demo (mismo flujo TA: “Entrar desarrollo”), *y* documentar login username/password con usuario seed como path secundario |
| Clinician seed | Ejecutar `backend/scripts/seed_clinician.py` (o equivalente) tras schema |
| Patient diary | Invite redeem (`US-DIARY-AUTH-PROD`) además del path clinician-proxy |
| Anonymization | Deploy **después** de merge de **US-PRIV-001** |
| Cold start | Tier free ~50 s+; aviso en README / Typeform |

Solo cambiar a `ALLOW_DEV_AUTH=false` si el tutor lo exige explícitamente (entonces demo vía `/auth/login` + seed).

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

- [ ] Frontend público responde (SPA carga).
- [ ] API `/health` pública 200.
- [ ] CORS permite origen del Static Site.
- [ ] Flujo demo: login → intake → generar plan → review → approve/reject.
- [ ] URLs documentadas en README / paquete de entrega.
- [ ] Nota de cold start free tier si aplica.

---

## 5. Relación con US-OPS-SPA-HOST

Código Must antes/en paralelo al redeploy:

- `frontend/src/services/api.js` debe usar `import.meta.env.VITE_API_BASE_URL || "/api"` (ya existía en `feature-entrega2-AVW`; reintroducir en la rama de entrega final con tests).
- `frontend/public/_redirects` para SPA deep links.
- `render.yaml` versionado en raíz (este repo).
