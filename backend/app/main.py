from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401 — register ORM metadata
from app.api import auth, rag
from app.core.config import get_settings


@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Validate config that must be sound before serving RAG (US-RAG-004)."""
    from app.rag.nutrition_safety_config import get_nutrition_synonym_groups

    get_nutrition_synonym_groups()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="HolistiCare API",
        description="AI-powered holistic rehabilitation clinical decision support",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        lifespan=_lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.allow_dev_auth:
        app.include_router(auth.dev_auth_router, tags=["Auth"])
    app.include_router(rag.router, prefix="/rag", tags=["RAG"])

    @app.get("/health")
    async def health():
        return {"status": "ok", "version": "0.1.0"}

    return app


app = create_app()
