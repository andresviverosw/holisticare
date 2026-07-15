# Typeform submission — HolistiCare (LIDR / AI4devs)

Checklist para rellenar el Typeform del máster con la documentación del proyecto.

## Rama canónica de documentación

Usa esta rama (formato LIDR en `README.md` + `prompts.md` + hub `docs/`):

**https://github.com/andresviverosw/holisticare/tree/cursor/docs-typeform-submission-82c5**

| Campo Typeform (típico) | Valor a pegar |
|-------------------------|---------------|
| Nombre completo | Andrés Viveros |
| Nombre del proyecto | HolistiCare |
| URL del repositorio | https://github.com/andresviverosw/holisticare |
| URL de la rama / documentación | https://github.com/andresviverosw/holisticare/tree/cursor/docs-typeform-submission-82c5 |
| URL del README LIDR | https://github.com/andresviverosw/holisticare/blob/cursor/docs-typeform-submission-82c5/README.md |
| URL de prompts | https://github.com/andresviverosw/holisticare/blob/cursor/docs-typeform-submission-82c5/prompts.md |
| URL demo (frontend) | https://holisticare-frontend.onrender.com |
| URL demo (API health) | https://holisticare-api.onrender.com/health |
| PR Entrega 1 (academia) | https://github.com/LIDR-academy/AI4Devs-finalproject/pull/185 |
| Rama demo + deploy Entrega 2 | https://github.com/andresviverosw/holisticare/tree/feature-entrega2-AVW |

> Si el Typeform pide un **PR hacia `LIDR-academy/AI4Devs-finalproject`**, usa el PR #185 (Entrega 1) o crea uno nuevo en tu fork `andresviverosw/AI4Devs-finalproject` copiando `README.md` → `readme.md` y `prompts.md` desde esta rama.

## Mapa de artefactos en esta rama

| Requisito LIDR | Archivo |
|----------------|---------|
| Ficha + producto + arquitectura + datos + API + HU + tickets + PRs | `README.md` |
| Bitácora de prompts (máx. 3 por sección) | `prompts.md` |
| README de producto (inglés) | `README-ORIGINAL.md` |
| Fases académicas 01–06 | `docs/01-` … `docs/06-` |
| Guías UI / developer / seguridad / diagramas | `docs/07-` … `docs/10-` |
| Plan de pruebas | `docs/05-test-plan.md` |
| Sprints 1–10 | `docs/sprint-01.md` … `docs/sprint-10.md` |
| Deploy demo Render | `docs/deploy-entrega2-demo.md` |
| Piloto / go-no-go | `docs/pilot-*.md` |
| Índice documentación | `docs/README.md` |

## Flujo recomendado antes de enviar

1. Abrir la rama canónica y verificar que `README.md` y `prompts.md` renderizan bien en GitHub.
2. Probar la demo (cold start ~1 min) o apuntar a instalación local según `docs/setup.md`.
3. Pegar en Typeform las URLs de la tabla superior.
4. Si piden zip: clonar la rama y comprimir, o usar “Download ZIP” de GitHub en la rama.
5. Adjuntar / enlazar video o capturas del flujo demo (sección 1.3 del README) si el formulario lo solicita.

## Notas

- **NOM-024:** ningún plan se auto-activa; siempre `pending_review` + aprobación explícita.
- Datos de pacientes en demos/tests son **sintéticos**.
- Esta rama documenta el estado del producto en `main` más el paquete académico LIDR; el deploy Render completo vive en `feature-entrega2-AVW`.
