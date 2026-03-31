from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, UUID4, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_ingestion_service, get_rag_pipeline
from app.core.database import get_db
from app.rag.pipeline import RAGPipeline
from app.schemas.intake_v0 import GenericHolisticIntakeV0
from app.services.plan_persistence import (
    apply_plan_approval_action,
    get_persisted_plan,
    get_plan_sources_payload,
    persist_generated_plan,
)
from app.services.chunk_query import list_clinical_chunks
from app.services.ingestion_service import IngestionService

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

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        value = v.strip().lower()
        if value not in {"approve", "reject"}:
            raise ValueError("La accion debe ser 'approve' o 'reject'.")
        return value


# ─── Endpoints ────────────────────────────────────────────────

@router.post("/ingest", response_model=IngestResponse)
async def trigger_ingestion(
    request: IngestRequest,
    db: AsyncSession = Depends(get_db),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
):
    """
    Admin endpoint — ingests PDFs from source_dir into pgvector.
    Idempotent: already-indexed chunks are skipped unless force_reindex=True.
    """
    _ = db
    try:
        result = ingestion_service.ingest(
            source_dir=request.source_dir,
            force_reindex=request.force_reindex,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result


@router.get("/chunks")
async def list_chunks(
    therapy_type: Optional[str] = None,
    language: Optional[str] = None,
    has_contraindication: Optional[bool] = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Browse indexed clinical chunks with optional metadata filters."""
    return await list_clinical_chunks(
        db,
        therapy_type=therapy_type,
        language=language,
        has_contraindication=has_contraindication,
        limit=limit,
        offset=offset,
    )


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
    payload = await apply_plan_approval_action(
        db,
        plan_id=plan_id,
        action=request.action,
        practitioner_notes=request.practitioner_notes,
        edited_plan_json=request.edited_plan_json,
    )
    if payload is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return payload


@router.get("/plan/{plan_id}")
async def get_plan(
    plan_id: UUID4,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a treatment plan including its citations."""
    plan_row = await get_persisted_plan(db, plan_id=plan_id)
    if plan_row is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan_row.plan_json


@router.get("/plan/{plan_id}/sources")
async def get_plan_sources(
    plan_id: UUID4,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve the source clinical chunks that were used to generate a plan.
    Supports practitioner transparency and audit trail.
    """
    payload = await get_plan_sources_payload(db, plan_id=plan_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return payload
