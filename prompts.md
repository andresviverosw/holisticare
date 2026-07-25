> Prompts principales utilizados con asistentes de código (Cursor / Claude) durante el desarrollo de HolistiCare. Máximo 3 por sección. Conversaciones completas disponibles en el historial del IDE y commits del repositorio.
>
> Rama de Entrega 1 (Typeform, proyecto propio): `feature-entrega1-AVW` — checklist en `docs/typeform-submission.md`.

## Índice

1. [Descripción general del producto](#1-descripción-general-del-producto)
2. [Arquitectura del sistema](#2-arquitectura-del-sistema)
3. [Modelo de datos](#3-modelo-de-datos)
4. [Especificación de la API](#4-especificación-de-la-api)
5. [Historias de usuario](#5-historias-de-usuario)
6. [Tickets de trabajo](#6-tickets-de-trabajo)
7. [Pull requests](#7-pull-requests)

---

## 1. Descripción general del producto

**Prompt 1:**

```text
Actúa como arquitecto de producto para una plataforma de rehabilitación holística en México.
Define el MVP académico (junio 2026) con intake generic_holistic_v0, RAG para planes multi-semana,
diario del paciente y gobernanza NOM-024 (aprobación obligatoria del practicante).
Entrega: problema, usuarios, alcance MVP, stack tecnológico y riesgos regulatorios LFPDPPP.
```

**Nota:** Usé este prompt para estructurar `docs/01-requirements-and-domain-research.md` y delimitar MVP vs visión NMG a futuro. Pedí explícitamente datos sintéticos y sin auto-activación de planes.

**Prompt 2:**

```text
Genera user stories con IDs (US-INT-*, US-PLAN-*, US-RAG-*) en formato tabla con
prioridad MoSCoW, criterios Given/When/Then y test intent (unit/integration/e2e).
Incluye gobernanza: Planning Agent es dueño del backlog.
```

**Nota:** Resultado en `docs/04-feature-specs-and-user-stories.md`. Revisé manualmente que cada story tuviera evidencia de implementación antes de marcar "Done".

**Prompt 3:**

```text
Redacta README de proyecto para GitHub en inglés: problema clínico en México,
solución HolistiCare, stack, arquitectura RAG de 5 capas, quick start Docker.
```

**Nota:** Base de `README-ORIGINAL.md`. Para Entrega 2 migré el contenido al formato LIDR en español.

---

## 2. Arquitectura del Sistema

### **2.1. Diagrama de arquitectura:**

**Prompt 1:**

```text
Diseña arquitectura C4 (contexto + contenedores) para FastAPI + React + PostgreSQL/pgvector.
Incluye diagrama Mermaid, flujo RAG secuencial (query builder → retrieval → rerank → generation)
y justifica por qué RAG in-process es adecuado para MVP solo-developer.
```

**Nota:** Diagramas en `docs/10-solution-diagrams.md` y `docs/02-system-architecture.md`.

**Prompt 2:**

```text
Implementa RAGPipeline.generate_plan() con early exit cuando rerank devuelve cero chunks:
retornar plan con insufficient_evidence=true sin llamar al LLM generador.
Escribe test pytest que lo pruebe con mock del retriever.
```

**Nota:** TDD en `test_pipeline_insufficient.py`. El asistente propuso el contrato; yo ajusté mensajes en español para la UI.

**Prompt 3:**

```text
Añade fallback OpenAI chat cuando Anthropic falle (RAG_LLM_FALLBACK_OPENAI).
Centraliza en llm_chat.py e incluye tests con mocks de ambos proveedores.
```

**Nota:** Ver `backend/app/rag/llm_chat.py` y `test_llm_chat_fallback.py`.

### **2.2. Descripción de componentes principales:**

**Prompt 1:**

```text
Separa lógica de negocio en app/services/ (async functions, reciben AsyncSession).
Las rutas en rag.py solo validan auth, llaman servicios y mapean HTTPException.
No pongas SQL en los routers.
```

**Nota:** Patrón aplicado en intake_service, diary_service, plateau_service, etc.

**Prompt 2:**

```text
Configura reranker con backend configurable: crossencoder (local MiniLM) o Cohere.
Default crossencoder; documenta variables en .env.example.
```

**Nota:** `app/rag/retrieval/reranker.py`.

**Prompt 3:**

```text
Frontend: AuthContext con JWT en localStorage, interceptor axios Authorization,
RequireClinician para rutas privadas. formatApiError centralizado para errores 4xx/5xx en español.
```

**Nota:** `frontend/src/context/AuthContext.jsx`, `utils/apiErrors.js`.

### **2.3. Descripción de alto nivel del proyecto y estructura de ficheros**

**Prompt 1:**

```text
Genera CLAUDE.md con convenciones del repo: TDD obligatorio, user story IDs,
flujo request HTTP → deps → services → ORM/RAG, comandos pytest y docker compose.
```

**Nota:** Archivo raíz `CLAUDE.md` usado como contexto persistente para el asistente.

**Prompt 2:**

```text
Crea docs/setup.md paso a paso para Windows PowerShell: docker compose, ALLOW_DEV_AUTH,
parches SQL idempotentes para volúmenes DB antiguos, verificación de salud.
```

**Nota:** Guía operativa usada en demos y CI local.

**Prompt 3:**

```text
Documenta estructura de carpetas backend/app/rag/ (ingestion, retrieval, generation)
con una tabla componente → responsabilidad → tecnología.
```

**Nota:** Sección en `docs/08-developer-guide-and-architecture.md`.

### **2.4. Infraestructura y despliegue**

**Prompt 1:**

```text
Compara opciones de deploy MVP (AWS, VPS Hetzner, hybrid Neon+Cloudflare, Render, Railway)
para ~10 clínicos en México. Criterios: costo, pgvector, NOM-024/LFPDPPP, complejidad solo-dev.
Entrega recomendación con costo mensual y path de escalamiento.
```

**Nota:** `holisticare_deployment_analysis.md` y `holisticare_deployment_quickstart.md`.

**Prompt 2:**

```text
Para Entrega 2 LIDR necesito deploy demo en Render. Genera render.yaml con Postgres 16,
backend Docker, frontend static site. Documenta variables de entorno y paso init.sql para pgvector.
```

**Nota:** `render.yaml` y `docs/deploy-entrega2-demo.md` en esta rama.

**Prompt 3:**

```text
Frontend en producción debe usar VITE_API_BASE_URL apuntando al backend desplegado.
Mantén /api como default en desarrollo con proxy Vite.
```

**Nota:** Cambio mínimo en `frontend/src/services/api.js`.

### **2.5. Seguridad**

**Prompt 1:**

```text
Implementa require_roles() en deps.py con JWT HS256. POST /auth/dev-login solo si
ALLOW_DEV_AUTH=true; en producción la ruta no debe existir (404). Tests para ambos casos.
```

**Nota:** `test_auth_dev_login.py`, `docs/09-security-audit-and-todos.md`.

**Prompt 2:**

```text
Guardas nutricionales: cargar nutrition_safety_terms.json al startup; si NUTRITION_SAFETY_TERMS_PATH
está seteado y el archivo es inválido, la API no debe arrancar. Bloquear dietas que matcheen
contraindicaciones del intake con grupos de sinónimos configurables (US-RAG-004).
```

**Nota:** `nutrition_safety_config.py`, tests en `test_nutrition_safety_config.py`.

**Prompt 3:**

```text
Audita endpoints de chunk query contra SQL injection en filtros de metadata.
Escribe test de regresión test_chunk_query_security.py.
```

**Nota:** Validación de parámetros en `chunk_query.py`.

### **2.6. Tests**

**Prompt 1:**

```text
Configura conftest.py con TestClient, AsyncMock de get_db, usuario clinician por defecto,
override de get_rag_pipeline para tests CI-safe sin PostgreSQL ni API keys reales.
```

**Nota:** Base de toda la suite backend.

**Prompt 2:**

```text
Añade job GitHub Actions: pytest backend, npm lint + vitest + build frontend en push a main y PRs.
```

**Nota:** `.github/workflows/ci.yml`.

**Prompt 3:**

```text
Escribe demo-smoke-checklist.md con comandos PowerShell para verificar health, ingest y
generate plan antes de demos al tutor.
```

**Nota:** `docs/demo-smoke-checklist.md`.

---

## 3. Modelo de Datos

**Prompt 1:**

```text
Diseña init.sql para PostgreSQL 16 + pgvector: clinical_chunks con embedding VECTOR(1536),
treatment_plans JSONB con status lifecycle, intake_profiles UNIQUE por patient_id,
patient_diary_entries UNIQUE (patient_id, entry_date). Incluye índices GIN e IVFFlat.
```

**Nota:** `infra/init.sql`.

**Prompt 2:**

```text
Crea Pydantic schema GenericHolisticIntakeV0 versionado (_v0 suffix) separado de modelos ORM.
Campos: chief_complaint, conditions, goals, contraindications, baseline outcomes opcionales.
```

**Nota:** `app/schemas/intake_v0.py`.

**Prompt 3:**

```text
US-PLAN-004: tabla plan_memory_bank para snapshots de-identificados de planes approved.
Patch SQL idempotente para volúmenes Docker existentes. Sin patient_id en template_json.
```

**Nota:** `infra/patch_plan_memory_bank.sql`, Sprint 10.

---

## 4. Especificación de la API

**Prompt 1:**

```text
Implementa POST /rag/plan/generate con PlanGenerateRequest, manejo de errores Anthropic/OpenAI
como 503 con mensajes en español para el clínico, persistencia automática del draft.
```

**Nota:** `rag.py` líneas 488–566.

**Prompt 2:**

```text
PATCH /rag/plan/{id}/approve: acciones approve|reject, notas del practicante, plan editado opcional.
Validar transiciones de estado; 404 si plan no existe.
```

**Nota:** Gobernanza NOM-024; tests en plan approval API.

**Prompt 3:**

```text
POST /rag/ingest admin-only: escanear source_dir PDF/HTML, skip chunks existentes salvo force_reindex,
log en ingestion_log. Tests con filesystem mock.
```

**Nota:** `ingestion_service.py`, `test_ingestion_service.py`.

---

## 5. Historias de Usuario

**Prompt 1:**

```text
US-INT-004: reemplazar textarea JSON crudo en Dashboard por formulario intakeBuilder.js
que construya generic_holistic_v0. Tests vitest para el builder.
```

**Nota:** Mejora UX crítica para demo académica.

**Prompt 2:**

```text
US-ANLY-002: servicio plateau_service que detecte meseta/empeoramiento en serie temporal
de diary entries. Endpoint GET plateau-flags con explicación textual en español.
```

**Nota:** `plateau_service.py`, dashboard panels.

**Prompt 3:**

```text
US-PRED-001/002: recovery trajectory + recommendations desde historial de diario.
Mostrar estados insufficient-data en Dashboard sin romper el layout.
```

**Nota:** Endpoints analytics + UI en Dashboard.jsx.

---

## 6. Tickets de Trabajo

**Prompt 1:**

```text
Sprint 1 ticket: TDD para POST /rag/plan/generate. Red test que falle sin implementación.
Green mínimo: validación intake_json + respuesta insufficient_evidence cuando mock retriever vacío.
```

**Nota:** Metodología Red→Green→Refactor documentada en `docs/sprint-01.md`.

**Prompt 2:**

```text
Sprint 8 ticket US-RAG-004: externalizar sinónimos de seguridad nutricional a JSON editable.
Workflow de validación schema + documentación en setup.md y runbook.
```

**Nota:** `docs/sprint-08.md`.

**Prompt 3:**

```text
Sprint 10 ticket US-PLAN-004: endpoints memory bank + UI Dashboard (listar, buscar, instanciar)
+ PlanReview (guardar plan aprobado en biblioteca con título y tags).
```

**Nota:** `docs/sprint-10.md`, tests dedicados.

---

## 7. Pull Requests

**Prompt 1:**

```text
Crea PR para US-RAG-003: nutrition guidance end-to-end. Título claro, descripción con qué cambia,
por qué, impacto clínico (guardas contraindicaciones), referencia US-RAG-003, test plan checklist.
```

**Nota:** PR #1 en GitHub.

**Prompt 2:**

```text
Revisa diff del PR nutrition: ¿hay duplicación de reglas de safety entre pipeline y servicio?
Aplica DRY si la misma validación aparece dos veces. Actualiza descripción del PR.
```

**Nota:** PR #2 — refinamiento post-review.

**Prompt 3:**

```text
Prepara PR Entrega 2 LIDR: README formato academia, prompts.md, render.yaml, guía deploy.
No incluir .agents/ ni secrets. Referenciar historias US-PLAN-001, US-INT-001, US-ANLY-002.
```

**Nota:** PR de la rama `feature-entrega2-AVW` (este entregable).
