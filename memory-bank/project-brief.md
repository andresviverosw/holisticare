# Project Brief

## Name

HolistiCare

## One-liner

AI-powered clinical decision support for holistic rehabilitation, with practitioner-controlled treatment planning.

## Current stack

- Backend: FastAPI, SQLAlchemy, asyncpg
- Frontend: React, Vite, Tailwind
- Data: PostgreSQL + pgvector
- LLM: Anthropic
- Embeddings: OpenAI

## Core flows in production-like local setup

1. Clinician login (dev token or manual JWT)
2. Plan generation via RAG pipeline
3. Plan review and approve/reject
4. Plan source inspection
5. Chunk browsing and filtering

## Guardrails

- AI output must be practitioner-reviewed (`pending_review`).
- Errors from providers should surface as explicit `502/503`.
- TDD/SOLID/DRY enforced per project rules.
