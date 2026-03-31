from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, UUID4, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_rag_pipeline
from app.core.database import get_db
from app.rag.pipeline import RAGPipeline
from app.schemas.intake_v0 import GenericHolisticIntakeV0
from app.services.plan_persistence import persist_generated_plan

router = APIRouter()


# ─── Request / Response schemas ───────────────────────────────

class IngestRequest(BaseModel):
    source_dir: str = "data/mock"  # or "data/raw" for real PDFs
    force_reindex: bool = False


class IngestResponse(BaseModel):
    files_processed: int
    chunks_created: int
    status: str


class PlanGenerateRequest(BaseModel):
    """Draft plan generation — intake must match generic_holistic_v0 (see docs/sprint-01.md)."""

    patient_id: UUID4
    practitioner_id: Optional[UUID4] = None
    intake_json: GenericHolisticIntakeV0
    available_therapies: list[str] = Field(..., min_length=1)
    preferred_language: str = Field(default="es", pattern="^(es|en)$")

    @field_validator("available_therapies", mode="after")
    @classmethod
    def strip_nonempty_therapies(cls, v: list[str]) -> list[str]:
        out = [s.strip() for s in v if isinstance(s, str) and s.strip()]
        if not out:
            raise ValueError("Indique al menos una terapia disponible en la clínica.")
        return out


class PlanApprovalRequest(BaseModel):
    action: str  # "approve" | "reject"
    practitioner_notes: Optional[str] = None
    edited_plan_json: Optional[dict] = None  # if practitioner edits before approving


# ─── Endpoints ────────────────────────────────────────────────

@router.post("/ingest", response_model=IngestResponse)
async def trigger_ingestion(
    request: IngestRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Admin endpoint — ingests PDFs from source_dir into pgvector.
    Idempotent: already-indexed chunks are skipped unless force_reindex=True.
    """
    # TODO: wire to app.rag.ingestion.pipeline.run_ingestion()
    raise HTTPException(status_code=501, detail="Ingestion pipeline not yet implemented")


@router.get("/chunks")
async def list_chunks(
    therapy_type: Optional[str] = None,
    language: Optional[str] = None,
    has_contraindication: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Browse indexed clinical chunks with optional metadata filters."""
    # TODO: wire to db query on clinical_chunks table
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/plan/generate")
async def generate_plan(
    request: PlanGenerateRequest,
    db: AsyncSession = Depends(get_db),
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
) -> dict[str, Any]:
    """
    Core endpoint — runs the full RAG pipeline:
    profile summary → multi-query → retrieval → rerank → generation.
    Returns a treatment plan with status='pending_review'.
    If no chunks are retrieved, returns a plan-shaped response with insufficient_evidence=true.
    """
    plan = pipeline.generate_plan(
        patient_id=str(request.patient_id),
        intake_json=request.intake_json.model_dump(mode="json"),
        available_therapies=request.available_therapies,
        preferred_language=request.preferred_language,
    )
    if "insufficient_evidence" not in plan:
        plan["insufficient_evidence"] = False
    await persist_generated_plan(
        db,
        patient_id=request.patient_id,
        practitioner_id=request.practitioner_id,
        plan=plan,
    )
    return plan


@router.patch("/plan/{plan_id}/approve")
async def approve_plan(
    plan_id: UUID4,
    request: PlanApprovalRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Practitioner approval gate. Plans must be approved before
    being linked to patient's active record. Required for NOM-024 compliance.
    """
    # TODO: update treatment_plans.status, log approval, link to patient record
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.get("/plan/{plan_id}")
async def get_plan(
    plan_id: UUID4,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a treatment plan including its citations."""
    # TODO: fetch from treatment_plans table
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.get("/plan/{plan_id}/sources")
async def get_plan_sources(
    plan_id: UUID4,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve the source clinical chunks that were used to generate a plan.
    Supports practitioner transparency and audit trail.
    """
    # TODO: join treatment_plans.citations_used → clinical_chunks
    raise HTTPException(status_code=501, detail="Not yet implemented")
