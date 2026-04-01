from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api import auth, rag
import app.models  # noqa: F401 — register ORM metadata

settings = get_settings()

app = FastAPI(
    title="HolistiCare API",
    description="AI-powered holistic rehabilitation clinical decision support",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────
app.include_router(auth.router, tags=["Auth"])
app.include_router(rag.router, prefix="/rag", tags=["RAG"])


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
