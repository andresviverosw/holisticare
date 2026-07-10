# Despliegue demo — Entrega 2 LIDR (Render)

Guía para montar HolistiCare **desde cero** en un entorno accesible por URL pública (requisito Entrega 2).

**Tiempo estimado:** 45–90 min (primera vez).

**Costo:** tier free de Render (con limitaciones de cold start ~50 s).

---

## 1. Prerrequisitos

1. Cuenta en [Render](https://render.com) (login con GitHub).
2. Repositorio `andresviverosw/holisticare` en GitHub (rama `feature-entrega2-AVW` o `main` tras merge).
3. API keys:
   - `ANTHROPIC_API_KEY` (Claude — generación de planes)
   - `OPENAI_API_KEY` (embeddings)
4. (Opcional) Acceso al TA si el repo es privado.

---

## 2. Crear servicios desde Blueprint

1. En Render: **New → Blueprint**.
2. Conecta el repo `holisticare` y selecciona la rama `feature-entrega2-AVW`.
3. Render detectará `render.yaml` en la raíz.
4. Al crear, Render provisionará:
   - **PostgreSQL 16** (`holisticare-db`)
   - **Web Service** Docker backend (`holisticare-api`)
   - **Static Site** frontend (`holisticare-frontend`)

---

## 3. Variables de entorno (obligatorias)

En el servicio **holisticare-api**, configura manualmente (Render → Environment):

| Variable | Valor |
|----------|--------|
| `ANTHROPIC_API_KEY` | tu clave Anthropic |
| `OPENAI_API_KEY` | tu clave OpenAI |
| `ALLOW_DEV_AUTH` | `true` *(solo demo académica)* |
| `DEBUG` | `true` |
| `RAG_LLM_FALLBACK_OPENAI` | `true` |
| `CORS_ORIGINS` | URL del frontend (paso 5) |

Las variables `POSTGRES_*` se enlazan automáticamente desde la base de datos si usaste el Blueprint.

En **holisticare-frontend**:

| Variable | Valor |
|----------|--------|
| `VITE_API_BASE_URL` | `https://holisticare-api.onrender.com` *(ajusta al URL real del API)* |

> Sin `VITE_API_BASE_URL`, el frontend en producción intentará llamar `/api` en su propio dominio y fallará.

---

## 4. Inicializar PostgreSQL (pgvector + schema)

Render Postgres **no** ejecuta `infra/init.sql` automáticamente.

1. Render → **holisticare-db** → **Connect** → abre **PSQL** o copia la **External Database URL**.
2. Ejecuta la extensión y el schema:

```bash
# Desde tu máquina (con psql instalado), usando External Database URL:
psql "<EXTERNAL_DATABASE_URL>" -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql "<EXTERNAL_DATABASE_URL>" -f infra/init.sql
```

Si `init.sql` falla por objetos existentes, es seguro re-ejecutar (usa `IF NOT EXISTS`).

3. Verifica:

```sql
\dt
-- Debe listar intake_profiles, treatment_plans, clinical_chunks, etc.
```

---

## 5. Obtener URLs y cerrar CORS

Tras el primer deploy exitoso:

1. Copia la URL del **Static Site** (ej. `https://holisticare-frontend.onrender.com`).
2. Copia la URL del **Web Service** (ej. `https://holisticare-api.onrender.com`).
3. En **holisticare-api**, actualiza `CORS_ORIGINS` con la URL exacta del frontend (sin barra final).
4. Redeploy backend si cambiaste CORS.

Verifica:

```bash
curl https://holisticare-api.onrender.com/health
# {"status":"ok","version":"0.1.0"}
```

---

## 6. Ingesta inicial del corpus demo

Con el backend en línea y un JWT de dev-login:

```bash
# 1) Obtener token (solo si ALLOW_DEV_AUTH=true)
curl -X POST https://holisticare-api.onrender.com/auth/dev-login \
  -H "Content-Type: application/json" \
  -d '{"role":"clinician","sub":"demo-clinician"}'

# 2) Ingesta mock (admin)
curl -X POST https://holisticare-api.onrender.com/rag/ingest \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"source_dir":"data/mock","force_reindex":false}'
```

> El primer request tras cold start puede tardar ~1–2 min (descarga modelo cross-encoder).

---

## 7. Flujo demo para el evaluador

1. Abrir URL del frontend.
2. Clic en **Entrar (desarrollo)**.
3. En Dashboard: generar UUID de paciente → completar intake → **Generar plan**.
4. Ir a **Plan Review** → revisar citaciones → **Aprobar** o **Rechazar**.

Documenta este flujo en el Typeform si piden instrucciones.

---

## 8. Actualizar README (sección 0.4)

Edita `README.md` sección **0.4. URL del proyecto** con tus URLs reales antes de enviar el Typeform:

```markdown
### **0.4. URL del proyecto:**
- Frontend: https://holisticare-frontend.onrender.com
- API: https://holisticare-api.onrender.com/health
```

Commit en la rama `feature-entrega2-AVW`.

---

## 9. Enviar Typeform (Entrega 2)

1. [https://lidr.typeform.com/proyectoai4devs](https://lidr.typeform.com/proyectoai4devs)
2. Selecciona **Entrega 2 — Código funcional**.
3. Enlace principal (instrucciones TA):

   `https://github.com/andresviverosw/holisticare/tree/feature-entrega2-AVW`

4. Enlace alternativo (PR, si lo piden):

   `https://github.com/andresviverosw/holisticare/pull/<N>`

5. Incluye URL del frontend desplegado en el campo de demo si existe.

---

## 10. Problemas frecuentes

| Síntoma | Causa | Solución |
|---------|-------|----------|
| Frontend 404 en `/dashboard` | SPA sin rewrite | Verificar `frontend/public/_redirects` |
| CORS error en browser | `CORS_ORIGINS` incorrecto | URL exacta del frontend en env del API |
| 503 al generar plan | API keys inválidas o cuota | Revisar Anthropic/OpenAI billing |
| 500 `relation does not exist` | Schema no aplicado | Ejecutar `infra/init.sql` (paso 4) |
| `/auth/dev-login` 404 | `ALLOW_DEV_AUTH=false` | Setear `true` solo en demo |
| Timeout 50+ s | Cold start Render free | Reintentar; considerar plan paid para demo |

---

## Alternativa: Neon + Render (pgvector garantizado)

Si Render Postgres no permite `vector` en tu plan:

1. Crea proyecto free en [Neon](https://neon.tech) con extensión pgvector habilitada.
2. Ejecuta `infra/init.sql` contra Neon.
3. En Render API, sobrescribe `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` con credenciales Neon.
4. Mantén frontend en Render Static Site.

Ver también: `holisticare_deployment_quickstart.md` (Hetzner + Neon + Cloudflare).
