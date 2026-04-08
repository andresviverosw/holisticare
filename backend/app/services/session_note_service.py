from __future__ import annotations

from app.schemas.session_v0 import SessionNoteAssistV0


def suggest_session_note(input_data: SessionNoteAssistV0) -> dict[str, str]:
    """
    Build a clinician-facing draft note from structured session inputs.
    This is deterministic and fast for MVP backend use.
    """
    interventions = []
    for item in input_data.interventions:
        if item.duration_minutes is not None:
            interventions.append(
                f"{item.therapy_type}: {item.description} ({item.duration_minutes} min)"
            )
        else:
            interventions.append(f"{item.therapy_type}: {item.description}")

    interventions_text = "; ".join(interventions)
    observations_seed = input_data.observations_draft or "Sin observaciones iniciales."
    patient_response_seed = input_data.patient_reported_response or (
        "Paciente refiere tolerancia adecuada sin eventos adversos reportados."
    )

    suggested_observations = (
        "Se realizó la sesión con las siguientes intervenciones: "
        f"{interventions_text}. "
        f"Observaciones clínicas preliminares: {observations_seed}"
    )

    return {
        "suggested_observations": suggested_observations,
        "suggested_patient_reported_response": patient_response_seed,
    }

