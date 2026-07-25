"""
SYNTH-01 dataset generator — pure functions, no DB / no LLM.

Produces a reproducible package: intakes, plans (governance statuses),
care sessions, diary journeys, and memory-bank snapshots.
"""

from __future__ import annotations

import hashlib
import random
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any

from app.schemas.diary_v0 import PatientDiaryCheckinV0
from app.schemas.intake_v0 import GenericHolisticIntakeV0
from app.schemas.session_v0 import ClinicalSessionLogV0
from app.synthetic.archetypes import ARCHETYPES, Archetype
from app.synthetic.memory import extract_therapy_types, sanitize_plan_for_memory_bank
from app.synthetic.trajectories import TRAJECTORIES, TrajectoryId, build_diary_series

DEFAULT_SEED = 42
DEFAULT_VARIANTS_PER_ARCHETYPE = 4
DATASET_VERSION = "v1"

# Stable namespace so patient/plan IDs are deterministic across runs.
SYNTH_NAMESPACE = uuid.UUID("a0a0a0a0-a0a0-40a0-80a0-a0a0a0a0a0a0")
DEFAULT_PRACTITIONER_ID = uuid.UUID("b1b1b1b1-b1b1-41b1-81b1-b1b1b1b1b1b1")
DEFAULT_ANCHOR_DATE = date(2026, 5, 1)


@dataclass
class SyntheticDiaryEntry:
    id: uuid.UUID
    entry_date: date
    diary_json: dict[str, Any]


@dataclass
class SyntheticSession:
    id: uuid.UUID
    occurred_at: datetime
    session_json: dict[str, Any]


@dataclass
class SyntheticPatient:
    patient_id: uuid.UUID
    archetype_id: str
    clinician_role: str
    trajectory: TrajectoryId
    variant_index: int
    intake_json: dict[str, Any]
    plan: dict[str, Any]
    sessions: list[SyntheticSession] = field(default_factory=list)
    diary_entries: list[SyntheticDiaryEntry] = field(default_factory=list)


@dataclass
class SyntheticMemoryBankEntry:
    id: uuid.UUID
    source_plan_id: uuid.UUID
    title: str
    tags: list[str]
    therapy_types: list[str]
    language: str
    snapshot_json: dict[str, Any]
    created_by_sub: str


@dataclass
class SyntheticDataset:
    dataset_version: str
    seed: int
    generated_at: str
    practitioner_id: uuid.UUID
    patients: list[SyntheticPatient]
    memory_bank: list[SyntheticMemoryBankEntry]
    manifest: dict[str, Any]


def _stable_uuid(*parts: str) -> uuid.UUID:
    return uuid.uuid5(SYNTH_NAMESPACE, "|".join(parts))


def _build_intake(arch: Archetype, *, variant_index: int) -> dict[str, Any]:
    # Light variant flavor without breaking schema
    complaint = arch.chief_complaint
    if variant_index > 0:
        complaint = f"{arch.chief_complaint} Variante {variant_index + 1}."

    intake = {
        "profile_version": "generic_holistic_v0",
        "demographics": {
            "age_range": arch.age_range,
            "sex_at_birth": arch.sex_at_birth,
        },
        "chief_complaint": complaint,
        "conditions": list(arch.conditions),
        "goals": list(arch.goals),
        "contraindications": list(arch.contraindications),
        "current_medications": list(arch.medications),
        "allergies": list(arch.allergies),
        "baseline_outcomes": {"pain_nrs_0_10": arch.baseline_pain},
        "psychosocial_summary": arch.psychosocial_summary or None,
        "prior_interventions_tried": list(arch.prior_interventions),
    }
    return GenericHolisticIntakeV0.model_validate(intake).model_dump(mode="json")


def _plan_status_for(
    trajectory: TrajectoryId,
    variant_index: int,
    archetype_index: int,
) -> tuple[str, bool]:
    """
    Return (status, insufficient_evidence).

    Mix governance states while keeping most longitudinal cases approved
    so diary/KPI demos have active plans. Short-series cohorts rotate
    pending / rejected / insufficient_evidence across archetypes (at the
    default 4-variant scale there is only one short_series row per archetype).
    """
    if trajectory == "short_series":
        bucket = (archetype_index + variant_index) % 3
        if bucket == 0:
            return "pending_review", True
        if bucket == 1:
            return "rejected", False
        return "pending_review", False
    if trajectory == "improving" and variant_index == 0:
        return "approved", False
    if variant_index == 3 and trajectory == "high_pain_plateau":
        return "pending_review", False
    return "approved", False


def _build_plan(
    *,
    plan_id: uuid.UUID,
    patient_id: uuid.UUID,
    arch: Archetype,
    status: str,
    insufficient_evidence: bool,
    generated_at: datetime,
) -> dict[str, Any]:
    digest = hashlib.sha256(arch.id.encode("utf-8")).hexdigest()[:8].upper()
    citations = [f"REF-{digest}"]
    if insufficient_evidence:
        plan = {
            "plan_id": str(plan_id),
            "patient_id": str(patient_id),
            "generated_at": generated_at.isoformat(),
            "requires_practitioner_review": True,
            "status": "pending_review",
            "insufficient_evidence": True,
            "citations_used": [],
            "weeks": [],
            "confidence_note": (
                "Evidencia insuficiente en corpus sintético; completar plan manualmente."
            ),
            "diet_recommendations": {"eat": [], "avoid": []},
            "nutrition_safety_flags": [],
        }
        return plan

    weeks = []
    for week_n in range(1, 5):
        therapies = []
        for t in arch.therapies[:2]:
            therapies.append(
                {
                    "type": t,
                    "frequency": "2x/semana" if week_n < 3 else "1x/semana",
                    "duration_minutes": 45,
                    "rationale": (
                        f"Intervención alineada a {arch.conditions[0]} "
                        f"[{citations[0]}]"
                    ),
                    "citations": list(citations),
                }
            )
        weeks.append(
            {
                "week": week_n,
                "goals": list(arch.goals[:2]),
                "therapies": therapies,
                "contraindications_flagged": list(arch.contraindications),
                "outcome_checkpoints": ["pain_nrs_0_10", "function_0_10"],
            }
        )

    avoid = []
    if arch.diet_avoid_hint:
        avoid.append(
            {
                "item": arch.diet_avoid_hint,
                "rationale": "Contraindicación/alergia reportada en intake sintético.",
                "citations": list(citations),
            }
        )

    plan = {
        "plan_id": str(plan_id),
        "patient_id": str(patient_id),
        "generated_at": generated_at.isoformat(),
        "requires_practitioner_review": True,
        "status": status,
        "insufficient_evidence": False,
        "citations_used": list(citations),
        "weeks": weeks,
        "confidence_note": (
            f"Plan sintético para arquetipo {arch.id}; requiere revisión NOM-024."
        ),
        "diet_recommendations": {
            "eat": [
                {
                    "item": "Verduras de hoja verde",
                    "rationale": "Patron antiinflamatorio de apoyo.",
                    "citations": list(citations),
                }
            ],
            "avoid": avoid,
        },
        "nutrition_safety_flags": [],
        "retrieval_metadata": {
            "queries_used": [arch.chief_complaint],
            "candidates_retrieved": 8,
            "chunks_passed_to_llm": 4,
            "reranker_backend": "synthetic",
            "synthetic": True,
        },
    }
    if status == "approved":
        plan["approved_at"] = (generated_at + timedelta(hours=2)).isoformat()
    if status == "rejected":
        plan["practitioner_notes"] = "Rechazado en dataset sintético para cobertura de estados."
    return plan


def _build_sessions(
    *,
    patient_id: uuid.UUID,
    arch: Archetype,
    start_date: date,
    trajectory: TrajectoryId,
    rng_seed: int,
) -> list[SyntheticSession]:
    # Seeded synthetic clinical text only — not a security boundary.
    rng = random.Random(rng_seed)  # nosec B311
    if trajectory == "short_series":
        n = 1
    else:
        n = 8
    sessions: list[SyntheticSession] = []
    for i in range(n):
        occurred = datetime(
            start_date.year,
            start_date.month,
            start_date.day,
            16,
            0,
            tzinfo=timezone.utc,
        ) + timedelta(days=7 * i)
        therapy = arch.therapies[i % len(arch.therapies)]
        log = {
            "profile_version": "clinical_session_v0",
            "session_at": occurred.isoformat(),
            "interventions": [
                {
                    "therapy_type": therapy,
                    "description": (
                        f"Sesión {i + 1}: trabajo dirigido a {arch.conditions[0]}."
                    ),
                    "duration_minutes": 45,
                }
            ],
            "observations": (
                f"Observaciones clínicas sintéticas ({arch.clinician_role}): "
                f"respuesta {'favorable' if trajectory == 'improving' else 'variable'}."
            ),
            "patient_reported_response": rng.choice(
                [
                    "Tolera bien la sesión.",
                    "Refiere dolor residual leve.",
                    "Mejora subjetiva de movilidad.",
                    None,
                ]
            ),
        }
        validated = ClinicalSessionLogV0.model_validate(log).model_dump(mode="json")
        sid = _stable_uuid("session", str(patient_id), str(i))
        sessions.append(
            SyntheticSession(id=sid, occurred_at=occurred, session_json=validated)
        )
    return sessions


def _build_diary_entries(
    *,
    patient_id: uuid.UUID,
    trajectory: TrajectoryId,
    start_date: date,
    baseline_pain: int,
    rng_seed: int,
) -> list[SyntheticDiaryEntry]:
    # Seeded synthetic diary noise only — not a security boundary.
    rng = random.Random(rng_seed)  # nosec B311
    points = build_diary_series(
        trajectory=trajectory,
        start_date=start_date,
        baseline_pain=baseline_pain,
        rng=rng,
    )
    entries: list[SyntheticDiaryEntry] = []
    for p in points:
        payload = {
            "profile_version": "patient_diary_v0",
            "checkin_date": p.entry_date.isoformat(),
            "pain_nrs_0_10": p.pain,
            "sleep_quality_0_10": p.sleep,
            "mood_0_10": p.mood,
            "function_0_10": p.function,
            "notes_es": p.notes_es,
        }
        validated = PatientDiaryCheckinV0.model_validate(payload).model_dump(mode="json")
        eid = _stable_uuid("diary", str(patient_id), p.entry_date.isoformat())
        entries.append(
            SyntheticDiaryEntry(
                id=eid,
                entry_date=p.entry_date,
                diary_json=validated,
            )
        )
    return entries


def generate_synthetic_dataset(
    *,
    seed: int = DEFAULT_SEED,
    variants_per_archetype: int = DEFAULT_VARIANTS_PER_ARCHETYPE,
    anchor_date: date | None = None,
    practitioner_id: uuid.UUID | None = None,
) -> SyntheticDataset:
    if variants_per_archetype < 1:
        raise ValueError("variants_per_archetype must be >= 1")

    anchor = anchor_date or DEFAULT_ANCHOR_DATE
    practitioner = practitioner_id or DEFAULT_PRACTITIONER_ID
    generated_at = datetime(2026, 4, 15, 12, 0, tzinfo=timezone.utc)

    patients: list[SyntheticPatient] = []
    memory_bank: list[SyntheticMemoryBankEntry] = []
    banked_archetypes: set[str] = set()

    for a_idx, arch in enumerate(ARCHETYPES):
        for v_idx in range(variants_per_archetype):
            trajectory = TRAJECTORIES[v_idx % len(TRAJECTORIES)]
            patient_id = _stable_uuid("patient", arch.id, str(v_idx))
            plan_id = _stable_uuid("plan", arch.id, str(v_idx))
            status, insufficient = _plan_status_for(trajectory, v_idx, a_idx)

            intake = _build_intake(arch, variant_index=v_idx)
            plan = _build_plan(
                plan_id=plan_id,
                patient_id=patient_id,
                arch=arch,
                status=status,
                insufficient_evidence=insufficient,
                generated_at=generated_at + timedelta(minutes=a_idx * 10 + v_idx),
            )
            # Case start staggered per variant for demo windows
            start = anchor - timedelta(days=70) + timedelta(days=v_idx * 3)
            rng_seed = seed * 1_000_003 + a_idx * 97 + v_idx * 13

            sessions = _build_sessions(
                patient_id=patient_id,
                arch=arch,
                start_date=start,
                trajectory=trajectory,
                rng_seed=rng_seed + 17,
            )
            diary = _build_diary_entries(
                patient_id=patient_id,
                trajectory=trajectory,
                start_date=start,
                baseline_pain=arch.baseline_pain,
                rng_seed=rng_seed + 31,
            )

            patient = SyntheticPatient(
                patient_id=patient_id,
                archetype_id=arch.id,
                clinician_role=arch.clinician_role,
                trajectory=trajectory,
                variant_index=v_idx,
                intake_json=intake,
                plan=plan,
                sessions=sessions,
                diary_entries=diary,
            )
            patients.append(patient)

            if (
                status == "approved"
                and not insufficient
                and arch.id not in banked_archetypes
            ):
                snap = sanitize_plan_for_memory_bank(plan)
                mid = _stable_uuid("memory", str(plan_id))
                memory_bank.append(
                    SyntheticMemoryBankEntry(
                        id=mid,
                        source_plan_id=plan_id,
                        title=f"Plantilla sintética: {arch.label_es}"[:200],
                        tags=[arch.clinician_role, arch.id, "synthetic"],
                        therapy_types=extract_therapy_types(snap),
                        language="es",
                        snapshot_json=snap,
                        created_by_sub=str(practitioner),
                    )
                )
                banked_archetypes.add(arch.id)

    statuses = {p.plan["status"] for p in patients}
    trajectories = {p.trajectory for p in patients}
    manifest = {
        "dataset_version": DATASET_VERSION,
        "seed": seed,
        "variants_per_archetype": variants_per_archetype,
        "archetype_count": len(ARCHETYPES),
        "patient_count": len(patients),
        "diary_entry_count": sum(len(p.diary_entries) for p in patients),
        "session_count": sum(len(p.sessions) for p in patients),
        "memory_bank_count": len(memory_bank),
        "trajectories_covered": sorted(trajectories),
        "plan_statuses_covered": sorted(statuses),
        "features_exercised": [
            "US-INT-001 intake profiles",
            "US-PLAN-001/002/003 plan generation governance statuses",
            "US-SESS-001 care sessions",
            "US-DIARY-001 daily diary check-ins",
            "US-ANLY-001 outcomes trend series",
            "US-ANLY-002 plateau / worsening flags",
            "US-PRED-001 recovery trajectory labels",
            "US-PLAN-004 memory bank snapshots",
        ],
        "anchor_date": anchor.isoformat(),
        "notes": (
            "All records are synthetic. No real patient data. "
            "NOM-024: plans keep requires_practitioner_review=true."
        ),
    }

    return SyntheticDataset(
        dataset_version=DATASET_VERSION,
        seed=seed,
        generated_at=generated_at.isoformat(),
        practitioner_id=practitioner,
        patients=patients,
        memory_bank=memory_bank,
        manifest=manifest,
    )


def dataset_to_dict(ds: SyntheticDataset) -> dict[str, Any]:
    patients_out: list[dict[str, Any]] = []
    for p in ds.patients:
        patients_out.append(
            {
                "patient_id": str(p.patient_id),
                "archetype_id": p.archetype_id,
                "clinician_role": p.clinician_role,
                "trajectory": p.trajectory,
                "variant_index": p.variant_index,
                "intake_json": p.intake_json,
                "plan": p.plan,
                "sessions": [
                    {
                        "id": str(s.id),
                        "occurred_at": s.occurred_at.isoformat(),
                        "session_json": s.session_json,
                    }
                    for s in p.sessions
                ],
                "diary_entries": [
                    {
                        "id": str(e.id),
                        "entry_date": e.entry_date.isoformat(),
                        "diary_json": e.diary_json,
                    }
                    for e in p.diary_entries
                ],
            }
        )

    bank_out = []
    for m in ds.memory_bank:
        bank_out.append(
            {
                "id": str(m.id),
                "source_plan_id": str(m.source_plan_id),
                "title": m.title,
                "tags": m.tags,
                "therapy_types": m.therapy_types,
                "language": m.language,
                "snapshot_json": m.snapshot_json,
                "created_by_sub": m.created_by_sub,
            }
        )

    return {
        "dataset_version": ds.dataset_version,
        "seed": ds.seed,
        "generated_at": ds.generated_at,
        "practitioner_id": str(ds.practitioner_id),
        "manifest": ds.manifest,
        "patients": patients_out,
        "memory_bank": bank_out,
    }


def dataset_from_dict(payload: dict[str, Any]) -> SyntheticDataset:
    """Rehydrate a previously serialized dataset (for seed script)."""
    patients: list[SyntheticPatient] = []
    for p in payload["patients"]:
        patients.append(
            SyntheticPatient(
                patient_id=uuid.UUID(p["patient_id"]),
                archetype_id=p["archetype_id"],
                clinician_role=p["clinician_role"],
                trajectory=p["trajectory"],
                variant_index=int(p["variant_index"]),
                intake_json=p["intake_json"],
                plan=p["plan"],
                sessions=[
                    SyntheticSession(
                        id=uuid.UUID(s["id"]),
                        occurred_at=datetime.fromisoformat(s["occurred_at"]),
                        session_json=s["session_json"],
                    )
                    for s in p.get("sessions", [])
                ],
                diary_entries=[
                    SyntheticDiaryEntry(
                        id=uuid.UUID(e["id"]),
                        entry_date=date.fromisoformat(e["entry_date"]),
                        diary_json=e["diary_json"],
                    )
                    for e in p.get("diary_entries", [])
                ],
            )
        )
    memory_bank = [
        SyntheticMemoryBankEntry(
            id=uuid.UUID(m["id"]),
            source_plan_id=uuid.UUID(m["source_plan_id"]),
            title=m["title"],
            tags=list(m.get("tags") or []),
            therapy_types=list(m.get("therapy_types") or []),
            language=m.get("language") or "es",
            snapshot_json=m["snapshot_json"],
            created_by_sub=m["created_by_sub"],
        )
        for m in payload.get("memory_bank", [])
    ]
    return SyntheticDataset(
        dataset_version=payload["dataset_version"],
        seed=int(payload["seed"]),
        generated_at=payload["generated_at"],
        practitioner_id=uuid.UUID(payload["practitioner_id"]),
        patients=patients,
        memory_bank=memory_bank,
        manifest=dict(payload.get("manifest") or {}),
    )
