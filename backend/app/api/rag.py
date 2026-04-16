import json
from datetime import date
from typing import Any, Optional

import anthropic
import openai
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, UUID4, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    AuthUser,
    ensure_diary_subject_access,
    get_ingestion_service,
    get_rag_pipeline,
    require_roles,
)
from app.core.database import get_db
from app.rag.pipeline import RAGPipeline
from app.schemas.intake_v0 import GenericHolisticIntakeV0
from app.schemas.diary_v0 import PatientDiaryCheckinV0
from app.schemas.session_v0 import ClinicalSessionLogV0, SessionNoteAssistV0
from app.services.plan_persistence import (
    apply_plan_approval_action,
    get_persisted_plan,
    get_plan_sources_payload,
    persist_generated_plan,
)
from app.services.chunk_query import list_clinical_chunks
from app.services.ingestion_service import IngestionService
from app.services.intake_service import (
    get_intake_profile,
    list_intake_audit_entries,
    save_intake_profile,
    update_intake_profile_with_audit,
)
from app.services.intake_risk_service import analyze_intake_risk_flags
from app.services.analytics_service import (
    get_patient_outcomes_trend_payload,
    get_patient_plateau_flags_payload,
)
from app.services.diary_service import list_diary_entries_for_patient, upsert_diary_entry
from app.services.session_service import create_care_session, list_care_sessions_for_patient
from app.services.session_note_service import suggest_session_note

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


class IntakeSaveRequest(BaseModel):
    patient_id: UUID4
    practitioner_id: Optional[UUID4] = None
    intake_json: GenericHolisticIntakeV0


class IntakeUpdateRequest(BaseModel):
    practitioner_id: Optional[UUID4] = None
    intake_json: GenericHolisticIntakeV0


class SessionCreateRequest(BaseModel):
    patient_id: UUID4
    practitioner_id: Optional[UUID4] = None
    session_log: ClinicalSessionLogV0


class DiarySaveRequest(BaseModel):
    patient_id: UUID4
    checkin: PatientDiaryCheckinV0


class SessionNoteAssistRequest(BaseModel):
    session_note_input: SessionNoteAssistV0


# ─── Endpoints ────────────────────────────────────────────────

@router.post("/ingest", response_model=IngestResponse)
async def trigger_ingestion(
    request: IngestRequest,
    db: AsyncSession = Depends(get_db),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
    _current_user: AuthUser = Depends(require_roles("admin")),
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
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result


@router.post("/intake")
async def save_intake(
    request: IntakeSaveRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: AuthUser = Depends(require_roles("clinician", "admin")),
) -> dict[str, Any]:
    row = await save_intake_profile(
        db,
        patient_id=request.patient_id,
        practitioner_id=request.practitioner_id,
        intake_json=request.intake_json.model_dump(mode="json"),
    )
    return {
        "patient_id": str(row.patient_id),
        "practitioner_id": str(row.practitioner_id) if row.practitioner_id else None,
        "intake_json": row.intake_json,
    }


@router.get("/intake/{patient_id}")
async def get_intake(
    patient_id: UUID4,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    row = await get_intake_profile(db, patient_id=patient_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Intake not found")
    return {
        "patient_id": str(row.patient_id),
        "practitioner_id": str(row.practitioner_id) if row.practitioner_id else None,
        "intake_json": row.intake_json,
    }


@router.patch("/intake/{patient_id}")
async def update_intake(
    patient_id: UUID4,
    request: IntakeUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(require_roles("admin")),
) -> dict[str, Any]:
    row = await update_intake_profile_with_audit(
        db,
        patient_id=patient_id,
        actor_sub=current_user.sub,
        practitioner_id=request.practitioner_id,
        intake_json=request.intake_json.model_dump(mode="json"),
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Intake not found")
    return {
        "patient_id": str(row.patient_id),
        "practitioner_id": str(row.practitioner_id) if row.practitioner_id else None,
        "intake_json": row.intake_json,
    }


@router.get("/intake/{patient_id}/risk-flags")
async def get_intake_risk_flags(
    patient_id: UUID4,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    row = await get_intake_profile(db, patient_id=patient_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Intake not found")
    try:
        flags = analyze_intake_risk_flags(row.intake_json)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="No fue posible analizar riesgos en este momento. Continúe con revisión manual.",
        ) from exc
    return {
        "patient_id": str(row.patient_id),
        "risk_flags": flags,
    }


@router.get("/intake/{patient_id}/audit")
async def get_intake_audit(
    patient_id: UUID4,
    db: AsyncSession = Depends(get_db),
    _current_user: AuthUser = Depends(require_roles("admin")),
) -> dict[str, Any]:
    row = await get_intake_profile(db, patient_id=patient_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Intake not found")
    audit = await list_intake_audit_entries(db, patient_id=patient_id)
    return {
        "patient_id": str(patient_id),
        "audit": audit,
    }


@router.post("/sessions")
async def create_session(
    request: SessionCreateRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: AuthUser = Depends(require_roles("clinician", "admin")),
) -> dict[str, Any]:
    """Registro estructurado de sesión clínica (intervenciones y observaciones)."""
    row = await create_care_session(
        db,
        patient_id=request.patient_id,
        practitioner_id=request.practitioner_id,
        session_log=request.session_log,
    )
    return {
        "session_id": str(row.id),
        "patient_id": str(row.patient_id),
        "practitioner_id": str(row.practitioner_id) if row.practitioner_id else None,
        "occurred_at": row.occurred_at.isoformat(),
        "session_log": row.session_json,
    }


@router.get("/sessions/patient/{patient_id}")
async def list_patient_sessions(
    patient_id: UUID4,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _current_user: AuthUser = Depends(require_roles("clinician", "admin")),
) -> dict[str, Any]:
    rows = await list_care_sessions_for_patient(
        db,
        patient_id=patient_id,
        limit=limit,
        offset=offset,
    )
    return {
        "patient_id": str(patient_id),
        "items": [
            {
                "session_id": str(r.id),
                "patient_id": str(r.patient_id),
                "practitioner_id": str(r.practitioner_id) if r.practitioner_id else None,
                "occurred_at": r.occurred_at.isoformat(),
                "session_log": r.session_json,
            }
            for r in rows
        ],
        "limit": limit,
        "offset": offset,
    }


@router.post("/sessions/suggest-note")
async def suggest_session_note_completion(
    request: SessionNoteAssistRequest,
    _current_user: AuthUser = Depends(require_roles("clinician", "admin")),
) -> dict[str, Any]:
    """
    Suggest completion text for session notes from structured interventions.
    """
    suggestion = suggest_session_note(request.session_note_input)
    return {
        "profile_version": "clinical_session_note_assist_v0",
        **suggestion,
    }


@router.post("/diary")
async def save_diary_checkin(
    request: DiarySaveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(require_roles("patient", "clinician", "admin")),
) -> dict[str, Any]:
    """Registro diario de dolor, sueño, ánimo y función (un registro por día y paciente)."""
    ensure_diary_subject_access(current_user, request.patient_id)
    row = await upsert_diary_entry(
        db,
        patient_id=request.patient_id,
        checkin=request.checkin,
    )
    return {
        "entry_id": str(row.id),
        "patient_id": str(row.patient_id),
        "entry_date": row.entry_date.isoformat(),
        "checkin": row.diary_json,
    }


@router.get("/diary/patient/{patient_id}")
async def list_patient_diary(
    patient_id: UUID4,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(require_roles("patient", "clinician", "admin")),
) -> dict[str, Any]:
    ensure_diary_subject_access(current_user, patient_id)
    rows = await list_diary_entries_for_patient(
        db,
        patient_id=patient_id,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
    return {
        "patient_id": str(patient_id),
        "items": [
            {
                "entry_id": str(r.id),
                "patient_id": str(r.patient_id),
                "entry_date": r.entry_date.isoformat(),
                "checkin": r.diary_json,
            }
            for r in rows
        ],
        "limit": limit,
        "offset": offset,
    }


@router.get("/analytics/patient/{patient_id}/outcomes-trend")
async def get_outcomes_trend(
    patient_id: UUID4,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    _current_user: AuthUser = Depends(require_roles("clinician", "admin")),
) -> dict[str, Any]:
    """Tendencias de dolor, sueño, ánimo y función desde el diario (eje temporal para gráficas)."""
    try:
        return await get_patient_outcomes_trend_payload(
            db,
            patient_id=patient_id,
            date_from=date_from,
            date_to=date_to,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/analytics/patient/{patient_id}/plateau-flags")
async def get_plateau_flags(
    patient_id: UUID4,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    _current_user: AuthUser = Depends(require_roles("clinician", "admin")),
) -> dict[str, Any]:
    """Detección heurística de empeoramiento o dolor alto estable (diario del paciente)."""
    try:
        return await get_patient_plateau_flags_payload(
            db,
            patient_id=patient_id,
            date_from=date_from,
            date_to=date_to,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/chunks")
async def list_chunks(
    therapy_type: Optional[str] = None,
    topic: Optional[str] = None,
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
        topic=topic,
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
    _current_user: AuthUser = Depends(require_roles("clinician", "admin")),
) -> dict[str, Any]:
    """
    Core endpoint — runs the full RAG pipeline:
    profile summary → multi-query → retrieval → rerank → generation.
    Returns a treatment plan with status='pending_review'.
    If no chunks are retrieved, returns a plan-shaped response with insufficient_evidence=true.
    """
    try:
        plan = pipeline.generate_plan(
            patient_id=str(request.patient_id),
            intake_json=request.intake_json.model_dump(mode="json"),
            available_therapies=request.available_therapies,
            preferred_language=request.preferred_language,
        )
    except anthropic.AuthenticationError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Clave de API de Anthropic inválida o no configurada. "
                "Configure ANTHROPIC_API_KEY en .env del backend (o variables del contenedor) y reinicie."
            ),
        ) from exc
    except anthropic.AnthropicError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "El servicio Claude (Anthropic) no pudo completar la solicitud. "
                f"Detalle técnico: {exc!s}. "
                "Revise facturación, límites de tasa y el estado del servicio en console.anthropic.com."
            ),
        ) from exc
    except openai.AuthenticationError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Clave de API de OpenAI inválida o no configurada. "
                "Configure OPENAI_API_KEY en .env (embeddings / búsqueda vectorial) y reinicie el backend."
            ),
        ) from exc
    except openai.RateLimitError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "OpenAI: límite de uso o cuota insuficiente (embeddings). "
                "Revise facturación y límites en https://platform.openai.com/account/billing"
            ),
        ) from exc
    except openai.OpenAIError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "OpenAI no pudo completar la solicitud (p. ej. embeddings). "
                f"Detalle técnico: {exc!s}. "
                "Revise OPENAI_API_KEY, red y estado en https://status.openai.com"
            ),
        ) from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "El modelo devolvió una respuesta que no es JSON válido al generar el plan. "
                "Intente de nuevo; si persiste, revise el registro del backend."
            ),
        ) from exc
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
    _current_user: AuthUser = Depends(require_roles("clinician", "admin")),
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
