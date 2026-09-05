from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401 — register ORM metadata
from app.api import auth, rag
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db


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

    app.include_router(auth.auth_router, tags=["Auth"])
    if settings.allow_dev_auth:
        app.include_router(auth.dev_auth_router, tags=["Auth"])
    app.include_router(rag.router, prefix="/rag", tags=["RAG"])

    @app.get("/health")
    async def health():
        return {"status": "ok", "version": "0.1.0"}

    @app.get("/ready")
    async def ready(db: AsyncSession = Depends(get_db)):
        """US-OPS-HEALTH-001 — fails when Postgres cannot serve SELECT 1."""
        from fastapi import HTTPException
        from app.ops.readiness import ping_database

        try:
            await ping_database(db)
        except Exception as exc:
            raise HTTPException(status_code=503, detail="database_unavailable") from exc
        return {"status": "ready", "db": "ok"}

    return app


app = create_app()
