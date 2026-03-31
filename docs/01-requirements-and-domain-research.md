# Phase 1 - Requirements and Domain Research

## Document control

- Owner:
- Contributors:
- Version:
- Last updated:
- Status: `[ ]` Draft `[~]` In progress `[x]` Complete

## 1. Objective

Define the clinical, operational, and technical problem space for HolistiCare and produce validated requirements for the MVP.

## 2. Scope

### In scope

- Holistic rehab outpatient workflows
- Practitioner decision support needs
- Patient between-session follow-up needs
- MVP functional and non-functional requirements

### Out of scope

- Inpatient hospital workflows
- Autonomous diagnosis
- Fully automated treatment authorization

## 3. Stakeholders and users

- Primary users: holistic clinical experts attending rehab patients
- Secondary users: rehab patients themselves 
- Tertiary users: clinic admins
- Decision makers: product owner, clinical advisors
- Clinical advisors: clinical experts working in rehab clinics

## 4. Domain Research Summary

> **Nota metodológica:** Las secciones 4.1 y 4.2 constituyen hipótesis de investigación derivadas de literatura académica, análisis de herramientas existentes y conocimiento del dominio. Serán validadas y refinadas durante la sesión de co-design clínico antes de convertirse en requisitos confirmados.

---

### 4.1 Care Workflows Today

**Intake:**
El proceso de intake en consultorios de medicina naturopática y Nueva Medicina Germánica (NMG) es significativamente más extenso que en medicina convencional. Incluye anamnesis biográfica profunda: línea de tiempo vital, eventos emocionales significativos (*Bioshocks*), historial familiar transgeneracional, patrones de lateralidad y conflictos biológicos activos o en fase de resolución. Una primera sesión puede extenderse entre 90 y 120 minutos. Actualmente, este proceso se documenta en papel, cuadernos personales del practicante, o en hojas de Word/Excel sin estructura estandarizada. No existe un esquema de campos común entre practicantes.

**Session documentation:**
Las notas de sesión se registran durante o después de la consulta, típicamente en texto libre. En NMG, el practicante documenta el conflicto identificado, la capa embrionaria involucrada, la fase activa/de curación, síntomas esperados y "rieles" (disparadores de recaída). Este nivel de especificidad estructurada no es capturado por ninguna herramienta generalista. En México, solo el 42% de los médicos utiliza expediente electrónico, mientras que el 47% sigue usando expediente físico (FUNSALUD, Estudio Médic@ Digital, 2022) — y en el segmento de medicina alternativa, la adopción digital es presumiblemente menor aún, dada la ausencia de presión institucional.

**Follow-up:**
El seguimiento entre sesiones ocurre mayoritariamente por WhatsApp. El 79% de los médicos en México usa mensajería instantánea como herramienta de comunicación con pacientes (FUNSALUD, 2022), lo que implica que información clínica relevante — síntomas nuevos, cambios en el estado emocional, reacciones a la terapia — queda dispersa en conversaciones informales sin integrarse al expediente. No existe un mecanismo estructurado de check-in entre sesiones.

**Outcome measurement:**
Los diagnósticos y las terapias de la medicina alternativa y complementaria (MAC) pueden no estar estandarizados; diferentes terapeutas emplean diferentes sistemas y los efectos varían ampliamente (Manual Merck, 2025). En la práctica clínica holística mexicana, la medición de outcomes se basa principalmente en la percepción subjetiva del practicante y del paciente. No se aplican de forma sistemática instrumentos validados como NRS/VAS, SF-12, PHQ-9 o equivalentes. La evolución se evalúa cualitativamente en cada sesión, sin línea base formal ni seguimiento longitudinal cuantificable.

---

### 4.2 Pain Points

**Continuity gaps:**
La información generada entre sesiones — síntomas, cambios emocionales, reacciones adversas — no llega al practicante de forma estructurada. El practicante debe reconstruir el estado del paciente al inicio de cada sesión a partir de la memoria y notas propias. Los terapeutas de medicina alternativa en CDMX y Estado de México operan típicamente en su consultorio privado, trabajando en solitario (Scielo, 2019), sin sistemas de apoyo que mantengan continuidad clínica entre consultas. En NMG esto es especialmente crítico: el monitoreo de la fase curativa (síntomas esperados vs. inesperados) requiere seguimiento cercano que actualmente no es posible de manera sistemática.

**Personalization gaps:**
Los planes de tratamiento se construyen desde la experiencia personal del practicante y su acceso informal a bibliografía. No existe un mecanismo que integre evidencia clínica actualizada con el perfil específico del paciente. El 49% de los proveedores de atención médica citan la falta de estandarización y validación científica como barreras para la adopción generalizada de terapias complementarias (Business Research Insights, 2025). Para practicantes de NMG, la personalización es filosóficamente central — cada conflicto biológico es único — pero la herramienta para sistematizarla no existe.

**Measurement gaps:**
Más del 50% de los pacientes usan la MAC junto con sus medicamentos recetados, pero solo el 6% informa a sus prescriptores convencionales sobre este uso (Rev. Salud y Bienestar Social, 2024). Esto evidencia la ausencia de puentes de comunicación entre sistemas de atención, y también la falta de registro estructurado de outcomes en el lado holístico. Sin medición de línea base y seguimiento longitudinal, es imposible demostrar efectividad, identificar estancamientos o ajustar protocolos.

**Data quality gaps:**
Los datos que existen — en papel, cuadernos o WhatsApp — son fragmentados, no estructurados, no buscables y no analizables. La calidad del expediente depende enteramente de los hábitos documentales del practicante individual. No hay estandarización de terminología, campos obligatorios ni validación de integridad. Esto impide cualquier análisis retrospectivo, benchmarking entre pacientes o alimentación de modelos predictivos.

---

### 4.3 Existing Alternatives

**Tools evaluated:**

| Herramienta | Tipo | Uso en el contexto |
|---|---|---|
| Papel / cuaderno personal | No digital | Estándar de facto en consultorios holísticos México |
| Excel / Word | Ofimática | Expediente informal sin estructura clínica |
| Doctoralia | Directorio + agenda | Adquisición de pacientes, no gestión clínica |
| SimplePractice | EHR para terapeutas (EUA) | No disponible/adaptado para México ni MAC |
| Jane App | EHR para terapias manuales (Canadá) | Sin soporte para NMG/naturopatía; sin español |

**Strengths:**

- *Papel/cuaderno:* Máxima flexibilidad, cero fricción tecnológica, refleja el estilo personal del practicante holístico. Adecuado para capturar la complejidad narrativa de una anamnesis NMG.
- *Doctoralia:* Presencia de mercado consolidada en México, confianza del paciente, agenda online, perfil público del practicante.
- *SimplePractice / Jane App:* Expediente estructurado, notas de sesión, facturación, telehealth. Diseño orientado a terapeutas individuales.

**Weaknesses:**

- *Papel/cuaderno:* No searchable, no analizable, no compartible, sin trazabilidad, sin backup. La información muere con el practicante o en una mudanza.
- *Excel/Word:* Sin estructura clínica, sin validación de datos, sin historial longitudinal automatizado, sin visualización de progreso.
- *Doctoralia:* Es un directorio y gestor de agenda, no un sistema de gestión clínica. No tiene notas de sesión, planes de tratamiento, registro de outcomes ni soporte para el paradigma diagnóstico de NMG o naturopatía.
- *SimplePractice / Jane App:* Diseñados para el contexto anglosajón (idioma, regulación, tipos de terapia). Sin campos para conflictos biológicos, capas embrionarias, fases de resolución, Bioshock ni ninguno de los constructos centrales de NMG. Sin integración con modelos de IA clínica. Costo en USD, soporte en inglés.

**Opportunity for differentiation:**

Existe un espacio no cubierto entre el directorio generalista (Doctoralia) y el EHR convencional (SimplePractice): una plataforma de gestión clínica diseñada específicamente para el paradigma holístico integrativo, con IA que habla el lenguaje del practicante. La personalización basada en datos está llenando la brecha entre la tecnología actual y las antiguas artes curativas, colocando la medicina alternativa en un entorno más accesible, eficiente y compatible con la atención médica contemporánea (Global Market Statistics, 2025). HolistiCare ocupa ese espacio: expediente estructurado en el paradigma holístico, IA clínica con RAG, seguimiento longitudinal de outcomes, y acompañamiento del paciente entre sesiones — todo en español, para el mercado mexicano, bajo NOM-024-SSA3-2012.

---

## 5. Problem Statement

Los practicantes de medicina naturopática y Nueva Medicina Germánica en México operan sin herramientas digitales diseñadas para su paradigma clínico: documentan en papel, pierden continuidad entre sesiones, no miden outcomes de forma sistemática y construyen planes de tratamiento desde la intuición clínica individual sin respaldo de evidencia estructurada. El resultado es una atención de alta calidad relacional pero baja trazabilidad y escala, en un mercado donde más del 70% de los pacientes del Hospital Universitario de Nuevo León había usado algún producto o terapia complementaria en los últimos tres meses (UANL, 2016) y la demanda del sector crece sostenidamente. La ausencia de un bucle de retroalimentación clínico impide al practicante demostrar efectividad, detectar estancamientos oportunamente y personalizar tratamientos más allá de su experiencia acumulada — limitando tanto la calidad del cuidado como la capacidad de crecer como práctica clínica.

---

## 6. Value Proposition

**Clinical value:**
Proporciona al practicante naturopático y de NMG un expediente estructurado en su propio paradigma: campos para conflicto biológico, Bioshock, capa embrionaria, fase activa/curativa y rieles de recaída, complementados con intake estructurado y notas de sesión asistidas por IA. El motor RAG sugiere planes de tratamiento basados en evidencia clínica relevante al caso, que el practicante revisa y aprueba — reduciendo el tiempo de preparación por sesión y expandiendo su acceso a literatura actualizada. La detección automática de contraindicaciones añade una capa de seguridad clínica ausente en el flujo actual.

**Patient value:**
El paciente recibe acompañamiento estructurado entre sesiones mediante un diario de síntomas y bienestar accesible desde su móvil — capturando en tiempo real información que hoy se pierde o llega por WhatsApp. Visualiza su progreso longitudinal en instrumentos validados (NRS, PSQI, PHQ-9), lo que refuerza su adherencia al tratamiento. El 57% de los pacientes ya adoptan enfoques de tratamiento híbrido (Business Research Insights, 2025) — HolistiCare les da la herramienta para hacerlo de forma coordinada con su practicante.

**Operational value:**
Elimina la reconstrucción manual del estado del paciente al inicio de cada sesión. El resumen clínico generado por IA al abrir una consulta ofrece al practicante una síntesis del periodo intersesión en segundos. El registro longitudinal de outcomes permite identificar pacientes en plateau, ajustar protocolos y — a escala de consultorio — detectar qué combinaciones terapéuticas correlacionan con mejores resultados para perfiles similares.

**Business value:**
Para el practicante, un expediente trazable y estructurado bajo NOM-024-SSA3-2012 reduce riesgo legal y habilita la facturación formal. Para la firma consultora, HolistiCare es el primer producto de una línea de soluciones verticales para el sector MAC en México — un mercado que a nivel global se proyecta crecer de USD 131 mil millones en 2025 a USD 407 mil millones en 2033 a una CAGR del 17.2% (Proficient Market Insights, 2025), con escasa penetración de herramientas digitales especializadas en el segmento hispanohablante.


## 7. Requirements

### 7.1 Functional requirements (MVP)

| ID | Requirement | Priority (MoSCoW) | Rationale | Acceptance reference |
|----|-------------|-------------------|-----------|----------------------|
| FR-01 |  |  |  |  |
| FR-02 |  |  |  |  |

### 7.2 Non-functional requirements

| ID | Requirement | Category | Target |
|----|-------------|----------|--------|
| NFR-01 |  | Performance |  |
| NFR-02 |  | Security |  |
| NFR-03 |  | Privacy |  |
| NFR-04 |  | Reliability |  |
| NFR-05 |  | Explainability |  |

## 8. Constraints and Assumptions

### Regulatory constraints

- **NOM-024-SSA3-2012** — Todo expediente clínico electrónico generado por HolistiCare debe cumplir con los requisitos de estructura, integridad, autenticidad y confidencialidad establecidos por esta norma. Implica: identificador único por paciente, trazabilidad de modificaciones, firma electrónica del practicante en cada registro y política de retención definida.
- **LFPDPPP** — Todos los datos personales y sensibles (datos de salud) requieren: aviso de privacidad explícito, consentimiento informado documentado, mecanismos de acceso/rectificación/cancelación/oposición (derechos ARCO), y controles de transferencia a terceros (incluyendo APIs de Anthropic y OpenAI). Se debe contar con un DPA (Data Processing Agreement) con cada proveedor de nube.
- **Localización de datos** — Los datos de pacientes no pueden procesarse fuera del territorio nacional sin base legal explícita. Las llamadas a la Claude API y OpenAI Embeddings API involucran transferencia internacional; esto requiere cláusulas contractuales aprobadas o anonymización antes del envío.
- **Aprobación humana obligatoria** — Ningún plan de tratamiento generado por IA puede activarse en el expediente del paciente sin aprobación explícita del practicante certificado. Este es un requisito regulatorio y de seguridad clínica no negociable para el MVP ni para versiones posteriores.
- **Alcance de práctica** — HolistiCare es una herramienta de apoyo a la decisión clínica (Clinical Decision Support), no un dispositivo médico diagnóstico. El sistema nunca debe emitir diagnósticos definitivos. Todo output de IA debe incluir disclaimers consistentes con este alcance para evitar responsabilidad legal.

### Technical constraints

- **Latencia del pipeline RAG** — El tiempo de respuesta extremo a extremo (intake → plan generado) debe mantenerse por debajo de 8 segundos en condiciones normales de carga. Dependencias de latencia: OpenAI Embeddings API, pgvector similarity search, Claude API, cross-encoder reranker. El reranker (cross-encoder local) es el cuello de botella más probable en el primer deploy.
- **Límites de contexto del LLM** — Claude Sonnet tiene una ventana de contexto de 200K tokens, pero el costo por token y la latencia limitan prácticamente el contexto de generación a ~4,000–6,000 tokens de chunks recuperados. Esto impone un techo al número y tamaño de chunks que se pueden pasar al modelo, lo que hace crítica la calidad del reranking.
- **Calidad del corpus RAG en fase MVP** — El pipeline RAG es tan bueno como los documentos que lo alimentan. Con 10–15 PDFs clínicos iniciales (mock + curados), la cobertura temática será limitada. El sistema debe comunicar explícitamente al practicante cuando el contexto recuperado es insuficiente, en lugar de generar respuestas especulativas.
- **Multilingüismo** — La base de conocimiento incluirá documentos en inglés y español. El modelo de embeddings (text-embedding-3-small) maneja ambos idiomas, pero la calidad de retrieval cross-language (query en español, documento en inglés) debe validarse empíricamente durante la fase de evaluación.
- **Infraestructura MVP** — El MVP corre en Docker Compose sobre una sola VM (GCP e2-standard-4 o equivalente). No hay alta disponibilidad, autoescalado ni CDN en esta fase. Esto limita el número de usuarios concurrentes y la tolerancia a fallos.
- **Sin app nativa** — El diario del paciente es una web app responsiva. Notificaciones push para check-ins diarios no están disponibles sin service worker o app nativa; las alternativas en MVP son email o WhatsApp Business API.

### Resource constraints

- **Equipo:** Proyecto unipersonal durante fase de maestría. Toda la arquitectura, desarrollo, pruebas y documentación recaen en un solo desarrollador. Implica priorización estricta y scope control agresivo.
- **Tiempo:** El MVP debe estar funcional para la entrega final de la maestría (fecha límite a confirmar). El plan de build en 9 fases debe ajustarse a ese calendario.
- **Presupuesto API:** Las llamadas a Claude API y OpenAI Embeddings tienen costo variable por token. Con el volumen de desarrollo y pruebas, se estima un gasto mensual de USD 30–80 en APIs durante la fase de desarrollo. Debe monitorizarse para evitar sorpresas.
- **Datos clínicos reales:** No se cuenta con pacientes reales durante la fase MVP. Toda validación funcional se realizará con datos sintéticos (~80–100 perfiles generados). Esto limita la validez externa de los resultados hasta que se haga una prueba piloto con practicantes reales.
- **Soporte clínico:** No hay un clínico de planta en el equipo. El conocimiento del dominio de NMG y naturopatía depende de la sesión de co-design y de la revisión del practicante colaborador. Cambios en el modelo clínico durante el desarrollo pueden generar retrabajo.

### Assumptions to validate

| # | Supuesto | Método de validación | Fecha objetivo |
|---|---|---|---|
| A-01 | Los practicantes de NMG en México están dispuestos a usar una herramienta digital si respeta su paradigma clínico | Sesión de co-design + encuesta de intención | Abril 2026 |
| A-02 | El intake estructurado de NMG (Bioshock, capas embrionarias, fase activa/curativa) puede modelarse en campos de formulario sin perder riqueza clínica | Validación de esquema en co-design | Abril 2026 |
| A-03 | Los practicantes están dispuestos a revisar y aprobar planes de IA generados, y no los verán como una amenaza a su rol | Co-design — pregunta directa | Abril 2026 |
| A-04 | Los pacientes adoptarán el diario de síntomas si es mobile-first y toma menos de 3 minutos completar | Prueba con 3–5 pacientes piloto | Mayo 2026 |
| A-05 | El corpus de 10–15 PDFs iniciales es suficiente para producir planes útiles en el dominio de naturopatía/dolor crónico | Evaluación RAG con golden set | Abril 2026 |
| A-06 | Las llamadas a Claude API y OpenAI desde México no violan LFPDPPP si se anonymizan datos personales antes del envío | Revisión legal con asesor o análisis de DPAs públicos | Abril 2026 |
| A-07 | El presupuesto de infraestructura cubre el período de desarrollo y pruebas sin interrupciones | Estimación de costos API + VM a partir del primer mes de uso | Continuo |

---

## 9. Open Questions

**Q1 — Transferencia internacional de datos de salud (LFPDPPP × APIs externas)**
¿Es suficiente anonymizar o pseudonymizar los datos del paciente antes de enviarlos a la Claude API y OpenAI Embeddings para cumplir con LFPDPPP? ¿O se requiere una base legal adicional (consentimiento explícito para transferencia internacional, cláusulas contractuales)? Esta pregunta bloquea decisiones de arquitectura sobre qué información puede incluirse en los prompts y cuál debe quedarse local.
*Owner:* Andrés Viveros · *Plazo:* Antes de primer deploy con datos reales

**Q2 — Nivel de adopción tecnológica del practicante objetivo**
¿Qué tan cómodo está el practicante de NMG/naturopatía con herramientas digitales en su flujo de trabajo diario? ¿Ha intentado antes usar algún software clínico y lo abandonó? ¿Cuáles fueron las fricciones? La respuesta define si el onboarding debe ser autoguiado o asistido, y qué tan simple debe ser la UI en el MVP.
*Owner:* Andrés Viveros · *Fuente:* Sesión de co-design — Bloque 1

**Q3 — Terminología y campos del expediente NMG**
¿Cuáles son los campos mínimos indispensables que un practicante de NMG considera que debe tener un expediente para ser útil? Específicamente: ¿cómo nombran y estructuran el conflicto biológico, los rieles, la fase activa/curativa y el seguimiento de la crisis curativa? ¿Existe un estándar de facto entre la comunidad, o varía por escuela de formación?
*Owner:* Andrés Viveros · *Fuente:* Sesión de co-design — Bloque 2

**Q4 — Umbral de confianza para usar un plan generado por IA**
¿Qué tendría que ser verdad para que el practicante usara el plan sugerido por la IA como punto de partida — no como sustituto — de su propio criterio clínico? ¿Qué información de trazabilidad (fuentes, nivel de evidencia, advertencias) necesita ver para confiar en la sugerencia? Esta es la pregunta central de la sesión de co-design y define el diseño del output del pipeline RAG.
*Owner:* Andrés Viveros · *Fuente:* Sesión de co-design — Bloque 3

**Q5 — Instrumentos de outcome preferidos por el practicante**
De los instrumentos validados candidatos (NRS/VAS, SF-12, PSQI, PHQ-9/GAD-7, Barthel, DASH, WOMAC, ODI), ¿cuáles son reconocidos y aceptados por los practicantes de NMG? ¿Algunos entran en contradicción con su paradigma (p.ej., instrumentos que asumen modelo biomédico)? ¿Prefieren construir su propia escala de seguimiento?
*Owner:* Andrés Viveros · *Fuente:* Sesión de co-design — Bloque 2

**Q6 — Modelo de negocio y disposición a pagar**
¿Cuánto estaría dispuesto a pagar un practicante individual por una herramienta como HolistiCare? ¿El modelo SaaS mensual es aceptable, o prefieren pago por uso, pago único, o un modelo freemium? ¿Existe disposición a pagar más si incluye soporte en español y capacitación inicial?
*Owner:* Andrés Viveros · *Fuente:* Sesión de co-design — Bloque 4 / entrevistas adicionales

---

## 10. Risks and Mitigations

| # | Riesgo | Probabilidad | Impacto | Mitigación | Owner |
|---|---|---|---|---|---|
| R-01 | El practicante en co-design invalida el modelo de campos del expediente NMG, requiriendo rediseño del esquema de datos | Alta | Alto | Diseñar el esquema como JSONB flexible desde el inicio; evitar campos rígidos hasta validación. Hacer co-design antes de codificar modelos de DB. | Andrés Viveros |
| R-02 | Las llamadas a APIs externas (Claude, OpenAI) violan LFPDPPP sin anonymización previa, bloqueando el uso con datos reales | Media | Crítico | Implementar capa de anonymización/pseudonymización antes de cualquier llamada API desde el MVP. Revisar DPAs públicos de Anthropic y OpenAI. Buscar asesoría legal antes del piloto. | Andrés Viveros |
| R-03 | Calidad insuficiente del pipeline RAG con corpus pequeño (10–15 docs): planes genéricos o incorrectos que el practicante rechaza | Alta | Alto | Construir golden eval set desde el inicio. Establecer umbral mínimo de calidad antes de mostrar output al usuario. Incluir "confidence_note" explícita cuando el contexto es insuficiente. | Andrés Viveros |
| R-04 | Latencia del pipeline RAG supera 8 segundos, afectando la experiencia de uso en consulta | Media | Medio | Perfilar cada fase del pipeline durante desarrollo. Pre-cargar el cross-encoder al inicio del servicio (no lazy load). Considerar caché de embeddings de queries frecuentes. | Andrés Viveros |
| R-05 | El practicante no adopta la herramienta por percibir la IA como amenaza a su autonomía clínica | Media | Alto | Diseño centrado en "asistente, no sustituto": el plan siempre requiere aprobación, el practicante puede editar antes de aprobar, el output cita fuentes transparentemente. Comunicación de posicionamiento desde el onboarding. | Andrés Viveros |
| R-06 | Los pacientes no adoptan el diario de síntomas entre sesiones, vaciando el principal canal de datos longitudinales | Media | Medio | Diseñar el check-in para completarse en < 3 minutos. Implementar recordatorio por WhatsApp o email. Mostrar al paciente su propio progreso para generar engagement. Validar en prueba piloto antes de invertir en notificaciones avanzadas. | Andrés Viveros |
| R-07 | Costos de API (Claude + OpenAI) escalan por encima del presupuesto disponible durante desarrollo | Baja | Medio | Implementar caché de embeddings para documentos ya procesados. Usar `max_tokens` conservador en generación. Monitorear gasto semanal desde el primer día. Tener límite de gasto configurado en ambas APIs. | Andrés Viveros |
| R-08 | Incumplimiento de NOM-024-SSA3-2012 por omisión de campos obligatorios en el expediente electrónico | Baja | Crítico | Revisar la norma completa antes de diseñar el esquema final. Documentar trazabilidad de modificaciones desde el MVP. Incluir campo de firma/aprobación del practicante en cada registro clínico. | Andrés Viveros |
| R-09 | Scope creep durante desarrollo: funcionalidades fuera del MVP consumen tiempo y retrasan la entrega de maestría | Alta | Alto | Mantener un backlog priorizado visible. Toda decisión de agregar funcionalidad pasa por un filtro explícito: ¿bloquea la entrega del MVP? Si no, va al backlog. | Andrés Viveros |
| R-10 | El modelo predictivo de outcomes (Feature 6) no tiene suficientes datos para ser estadísticamente válido con datos sintéticos | Alta | Bajo | Descope del modelo ML para la entrega de maestría si los datos sintéticos (~80–100 perfiles) son insuficientes. Reemplazar por análisis descriptivo + visualización de tendencias como proxy. | Andrés Viveros |

---

## 11. Deliverables and Sign-off

### Deliverables

| Entregable | Descripción | Estado | Fecha objetivo |
|---|---|---|---|
| Problem framing summary | Secciones 4–6 de este documento: domain research, problem statement y value proposition | ✅ Borrador completo | Marzo 2026 |
| Constraints & risks document | Secciones 8–10 de este documento | ✅ Borrador completo | Marzo 2026 |
| Co-design session report | Notas estructuradas de la sesión clínica: hallazgos por bloque, validaciones y rechazos de supuestos, lista de campos del expediente NMG confirmados | ⏳ Pendiente sesión | Abril 2026 |
| Validated requirement list | Sección 7 completa: FR y NFR validados con el practicante, priorizados por MoSCoW | ⏳ Pendiente co-design | Abril 2026 |
| Prioritized MVP scope | Tabla de features con alcance confirmado, criterios de aceptación por feature y out-of-scope explícito | ⏳ Pendiente co-design | Abril 2026 |
| System architecture document | Diagrama de componentes, decisiones de diseño (ADRs), stack tecnológico justificado, modelo de datos completo | ⏳ En progreso | Abril 2026 |
| Data dictionary & privacy framework | Definición de todas las entidades y campos del sistema; clasificación de datos por sensibilidad; mapeo a LFPDPPP y NOM-024 | ⏳ Pendiente | Abril 2026 |
| Synthetic dataset (v1) | ~80–100 perfiles de pacientes sintéticos generados con Pydantic, validados con reglas de realismo clínico | ⏳ Pendiente | Abril 2026 |
| RAG evaluation report | Métricas de hit rate, MRR, faithfulness y contraindication detection rate sobre golden eval set | ⏳ Pendiente | Mayo 2026 |
| Stakeholder alignment notes | Resumen de acuerdos, compromisos y "never automate" list del practicante colaborador | ⏳ Pendiente co-design | Abril 2026 |
| MVP funcional | Aplicación desplegada con las 6 features del MVP, lista para prueba piloto | ⏳ Pendiente | Junio 2026 |

### Definition of Done — MVP

El MVP se considera completo cuando:

1. Los 6 features del alcance pueden ejecutarse end-to-end con datos sintéticos sin errores críticos
2. El pipeline RAG supera los umbrales mínimos de calidad en el golden eval set (hit rate ≥ 0.80, faithfulness ≥ 0.85)
3. Todo plan generado por IA tiene `requires_practitioner_review: true` y no puede activarse sin aprobación explícita
4. El expediente del paciente cumple los campos obligatorios de NOM-024-SSA3-2012
5. La documentación académica (secciones 1–11 + arquitectura + test plan) está entregada y aprobada por el tutor
6. Al menos un practicante colaborador ha revisado un plan generado por el sistema y ha dado retroalimentación documentada

### Sign-off

- Clinical lead: Hunahpu D
- Product owner: Andres V
- Technical lead: Andres V

## Completion checklist

- [ ] Stakeholders identified and validated
- [ ] Requirements prioritized with rationale
- [ ] Constraints and assumptions documented
- [ ] Risks captured with mitigations
- [ ] MVP scope formally agreed
