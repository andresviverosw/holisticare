# prompts.md — HolistiCare (AI4devs final project)

Documentación de **prompts** usados en el desarrollo asistido por IA y en el runtime del producto.
Autor: Andrés Viveros (AVW). Rama de entrega: `finalproject-AVW`.

---

## 1. Propósito

Este archivo cumple la plantilla de entrega AI4devs (`readme.md` + `prompts.md`) y distingue:

1. **Prompts de producto (runtime)** — enviados a Claude/OpenAI en la API RAG.
2. **Prompts / instrucciones de desarrollo** — usados con agentes (Cursor / Claude Code) bajo TDD, SOLID y el modelo multi-agente del repo.

---

## 2. Prompts de producto (runtime RAG)

Fuente de verdad en código: `backend/app/rag/generation/`.

### 2.1 Generación de plan de tratamiento (`PlanGenerator`)

Archivo: `backend/app/rag/generation/generator.py` — constante `SYSTEM_PROMPT`.

Resumen de reglas hard-codeadas (NOM-024 / calidad clínica):

- Rol: asistente de apoyo a la decisión en rehabilitación holística (no sustituye al clínico).
- Salida: JSON estructurado de plan multi-semana.
- Toda recomendación debe citar evidencia recuperada con **REF-ID**.
- `requires_practitioner_review: true` siempre (sin auto-activación).
- Respetar contraindicaciones / alergias del perfil.
- Si la evidencia es insuficiente: señalizar `insufficient_evidence` (ruta sin LLM en pipeline).

El user message incluye el perfil clínico **anonimizado** (`PATIENT_TOKEN` / proyección US-PRIV-001), modalidades disponibles, idioma preferido y chunks recuperados.



### Excerpt (SYSTEM_PROMPT) — tutor-readable snapshot (2026-09-05)

> Code remains the source of truth: `backend/app/rag/generation/generator.py`.

```text
You are a clinical decision support assistant for holistic rehabilitation.
You generate evidence-based treatment plan suggestions for licensed practitioners.

RULES — follow strictly:
1. ONLY use information from the clinical context provided (referenced by REF-ID)
2. Cite the REF-ID for every clinical recommendation using the format [REF-XXXXXX]
3. Explicitly flag ALL contraindications found in the context
4. Never make definitive diagnoses
5. Always output valid JSON — no preamble, no markdown fences
6. If the context is insufficient for a recommendation, say so explicitly in confidence_note
7. requires_practitioner_review must ALWAYS be true — never override this
8. Write rationale in the same language as the patient profile (es or en)
```

### Excerpt (SUMMARIZER_PROMPT)

> Source: `backend/app/rag/generation/query_builder.py`.

```text
You are a clinical summarization assistant for a holistic rehabilitation platform.

Given a patient's intake JSON, produce a concise 100–150 word clinical summary
optimized for semantic search against a knowledge base of clinical guidelines.

Focus on:
- Chief complaint and duration
- Relevant medical history and comorbidities
- Current medications and contraindications
- Prior treatments and outcomes
- Baseline outcome scores (pain, function, sleep, mood)

Return ONLY the clinical summary. No preamble, no labels.
```

### Excerpt (QUERY_EXPANSION_PROMPT)

```text
You are a clinical search assistant for a holistic rehabilitation knowledge base.

Given a patient clinical summary, generate {n} distinct search queries to retrieve
relevant clinical guidelines and protocols. Each query should approach the case
from a different angle:
1. Symptom-focused (what the patient presents with)
2. Treatment-focused (what therapies are relevant)
3. Contraindication-focused (what to avoid and why)
4. Outcome-focused (expected recovery trajectory)

Patient summary:
{summary}

Return ONLY a JSON array of {n} query strings. No preamble, no labels.
Example: ["query 1", "query 2", "query 3", "query 4"]
```

### 2.2 Resumen clínico del intake (`QueryBuilder`)

Archivo: `backend/app/rag/generation/query_builder.py` — `SUMMARIZER_PROMPT`.

- Convierte el intake JSON (ya proyectado/anonimizado) en un resumen clínico breve para retrieval.
- Evita inventar datos no presentes en el perfil.

### 2.3 Expansión multi-query

Archivo: mismo `query_builder.py` — `QUERY_EXPANSION_PROMPT`.

- Genera N variantes de consulta (default 4) desde el resumen clínico para mejorar recall en pgvector.
- Enfoque: condición, terapia, contraindicaciones, objetivos funcionales.

### 2.4 Sugerencia de nota de sesión

Endpoint de asistencia de notas clínicas: prompt de completado a partir de intervenciones estructuradas (ver servicio / API de `suggest-note`). El clínico siempre edita antes de guardar.

### 2.5 Anonimización previa al LLM (US-PRIV-001)

No es un “prompt” de chat, pero es un **control de prompt engineering / privacy**:

- Choke point: `patient_anonymizer` antes de `QueryBuilder` / `PlanGenerator`.
- Elimina o sustituye identificadores (UUID, email/tel patterns) y reduce el intake a proyección clínica.
- Si falla la anonimización → error controlado (no se llama al LLM con PII cruda).

---

## 3. Instrucciones de desarrollo (agentes)

### 3.1 Contexto de proyecto (siempre activo en el repo)

Archivos canónicos:

- `CLAUDE.md` / `AGENTS.md` — visión de producto, NOM-024, stack, convenciones.
- `.cursor/rules/engineering-principles.mdc` — **TDD obligatorio** (Red → Green → Refactor), SOLID, DRY.
- `.cursor/rules/agent-workflow.mdc` — roles Planning / Development / QA / Debugging.
- `docs/final-delivery-plan.md` — backlog de cierre (US-PRIV-001, DEPLOY-01, etc.).

### 3.2 Plantilla de handoff entre agentes

```text
Backlog item ID:
Scope:
Acceptance criteria:
Test evidence:
Risks/issues:
Next owner:
```

### 3.3 Prompt-tipo para features (Development Agent)

```text
Implementa la historia {US-ID} con TDD estricto:
1) Escribe/actualiza tests que fallen y demuestren el comportamiento.
2) Implementa el mínimo código para pasar.
3) Refactor solo con tests en verde.
4) No auto-activar planes IA (NOM-024).
5) Mapear el cambio al ID de backlog y criterios de aceptación.
```

### 3.4 Prompt-tipo para bugs (Debugging Agent)

```text
Reproduce el defecto de forma determinista, aísla la causa raíz,
añade un test de regresión que falle primero, luego aplica el fix mínimo
y verifica CI (pytest / Vitest / Playwright según el área).
```

### 3.5 Prompt-tipo para documentación de entrega

```text
Prepara el documento de entrega final del capstone: resumen de sprints,
features, arquitectura por capas con diagramas Mermaid, tech stack,
seguridad/compliance, datos sintéticos, CI/CD, y capturas del demo público
(clínico + paciente). Debe poder exportarse a PDF.
```

---

## 4. Evidencia de uso de IA en el ciclo de vida

| Fase | Uso de IA | Artefacto |
|------|-----------|-----------|
| Diseño / backlog | Agente Planning + docs de fases | `docs/sprint-*.md`, `docs/04-feature-specs-and-user-stories.md` |
| Implementación | Agente Development (TDD) en Cursor | Código + tests en `backend/` y `frontend/` |
| RAG runtime | Claude + embeddings OpenAI | `app/rag/` |
| Evaluación | Smoke de calidad + informe | `docs/rag-evaluation-report.md` |
| Cierre | Documento + PDF de entrega | `docs/entrega-final-capstone.md` / `.pdf` |

---

## 5. Cómo reproducir prompts de producto

1. Levantar API con claves Anthropic/OpenAI (ver `.env.example`).
2. Ingerir corpus: endpoint admin `/rag/ingest` o scripts de ingesta.
3. Generar plan desde el Dashboard clínico (`POST /rag/plan/generate`).
4. Inspeccionar logs/tests de anonimización: `backend/tests/test_patient_anonymizer.py`, `test_pipeline_anonymization.py`.

Los textos exactos de system/user evolucionan con el código; **este archivo apunta a las constantes versionadas en git** para trazabilidad académica.
