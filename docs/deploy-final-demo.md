# Despliegue demo — Entrega final (Render)

Guía canónica para la **entrega final** del capstone. Misma topología que Entrega 2:

**Render Blueprint** = PostgreSQL 16 + Web Service (Docker API) + Static Site (SPA).

Documento base histórico: [`deploy-entrega2-demo.md`](deploy-entrega2-demo.md)  
Blueprint: [`../render.yaml`](../render.yaml)  
Plan: [`final-delivery-plan.md`](final-delivery-plan.md) (D2 locked → Render)

**No** usar Hetzner + Cloudflare Pages para esta entrega (eso queda como topología post-piloto en `holisticare_deployment_quickstart.md`).

---

## 0. Estado DEPLOY-01

| Item | Estado |
|------|--------|
| Código `US-OPS-SPA-HOST` (`VITE_API_BASE_URL`) | En rama de ejecución / PR |
| Código `US-PRIV-001` (anonymizer) | En rama de ejecución / PR |
| `render.yaml` + `_redirects` | En `main` (PR #16) |
| Live URLs en este entorno de agente | **Bloqueado** — no hay `RENDER_API_KEY` / cuenta Render en el sandbox |
| Operador humano | Debe ejecutar §§1–7 abajo y pegar URLs en README |
| Handoff completo (local → Render) | [`final-delivery-next-steps.md`](final-delivery-next-steps.md) |

---

## 1. Qué reutilizar de Entrega 2

| Pieza | Entrega 2 | Entrega final |
|-------|-----------|---------------|
| Hosting | Render Blueprint | **Igual** |
| DB | Render Postgres 16 (+ Neon fallback si falta `vector`) | **Igual** |
| API | Docker web service `holisticare-api` | **Igual** |
| SPA | Static Site + `VITE_API_BASE_URL` | **Igual** |
| SPA routing | rewrite `/* → /index.html` + `frontend/public/_redirects` | **Igual** |
| Schema bootstrap | `psql` + `infra/init.sql` (manual) | **Igual** — `init.sql` actual ya incluye invites, `app_users`, memory bank |
| Corpus | `POST /rag/ingest` con `data/mock` | **Igual** (sintético) |

---

## 2. Decisiones bloqueadas (2026-07-25)

| Tema | Decisión |
|------|----------|
| `ALLOW_DEV_AUTH` | **`true`** en Blueprint demo (flujo TA “Entrar desarrollo”) + seed clinician documentado como path secundario |
| Clinician seed | `backend/scripts/seed_clinician.py` tras schema |
| Anonymization | Deploy con **US-PRIV-001** mergeado |
| Cold start | Tier free ~50 s+; aviso en README / Typeform |

---

## 3. Pasos operativos

1. **New → Blueprint** en Render; conectar repo; rama con US-PRIV-001 + US-OPS-SPA-HOST; detectar `render.yaml`.
2. Secretos en **holisticare-api**: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `CORS_ORIGINS` = URL exacta del Static Site (sin `/` final).
3. En **holisticare-frontend**: `VITE_API_BASE_URL=https://<api-host>` (sin `/` final) → **Trigger Redeploy** del Static Site tras setear (Vite bake-time).
4. Schema:
   ```bash
   psql "<EXTERNAL_DATABASE_URL>" -c 'CREATE EXTENSION IF NOT EXISTS vector;'
   psql "<EXTERNAL_DATABASE_URL>" -f infra/init.sql
   ```
5. Seed clinician (compose/exec o one-off):
   ```bash
   # Example inside API container — adjust to Render shell
   python scripts/seed_clinician.py
   ```
6. Ingest:
   ```bash
   TOKEN=$(curl -s -X POST https://<api>/auth/dev-login \
     -H 'Content-Type: application/json' \
     -d '{"role":"admin","sub":"demo-admin"}' | jq -r .access_token)
   curl -X POST https://<api>/rag/ingest \
     -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"source_dir":"data/mock","force_reindex":false}'
   ```
7. Verificar checklist §4; pegar URLs en README § proyecto.

Troubleshooting: [`deploy-entrega2-demo.md`](deploy-entrega2-demo.md) §10.

---

## 4. Evidencia para DoD (DEPLOY-01)

- [ ] Frontend público responde (SPA carga).
- [ ] API `/health` pública 200.
- [ ] CORS permite origen del Static Site.
- [ ] `VITE_API_BASE_URL` correcto (Network tab → API host, no Static Site `/api`).
- [ ] Flujo demo: Entrar desarrollo → intake → generar plan → review → approve/reject.
- [ ] (Secundario) login username/password con usuario seed.
- [ ] URLs documentadas en README / paquete de entrega.
- [ ] Nota de cold start free tier.

### URL log (llenar al desplegar)

| Service | URL |
|---------|-----|
| Frontend | `https://________________.onrender.com` |
| API health | `https://________________.onrender.com/health` |
| Deployed git SHA | |

---

## 5. Relación con US-OPS-SPA-HOST

- `frontend/src/services/api.js` → `resolveApiBaseUrl(import.meta.env.VITE_API_BASE_URL)`.
- `frontend/public/_redirects` + `render.yaml` routes rewrite.
- Sin `VITE_API_BASE_URL`, el Static Site llama `/api` en su propio dominio y falla.
