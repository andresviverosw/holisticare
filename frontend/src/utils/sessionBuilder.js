/**
 * US-SESS-UI — session form ↔ clinical_session_v0 / note-assist payloads.
 */

function normalizeSessionAt(raw) {
  const s = String(raw || "").trim();
  if (!s) return null;
  // datetime-local → add seconds if missing for backend datetime parsing
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(s)) return `${s}:00`;
  return s;
}

function mapInterventions(list) {
  if (!Array.isArray(list)) return [];
  return list
    .map((item) => {
      const therapy_type = String(item?.therapyType || "").trim();
      const description = String(item?.description || "").trim();
      const durationRaw = String(item?.durationMinutes ?? "").trim();
      let duration_minutes = null;
      if (durationRaw !== "") {
        const n = Number.parseInt(durationRaw, 10);
        duration_minutes = Number.isNaN(n) ? null : n;
      }
      return { therapy_type, description, duration_minutes };
    })
    .filter((item) => item.therapy_type && item.description);
}

export function validateSessionForm(form) {
  if (!normalizeSessionAt(form?.sessionAt)) {
    return "La fecha y hora de la sesión son obligatorias.";
  }
  const interventions = mapInterventions(form?.interventions);
  if (interventions.length === 0) {
    return "Agrega al menos una intervención (tipo y descripción).";
  }
  if (!String(form?.observations || "").trim()) {
    return "Las observaciones no pueden quedar vacías.";
  }
  return null;
}

export function buildSessionLog(form) {
  const patientResponse = String(form.patientReportedResponse || "").trim();
  return {
    profile_version: "clinical_session_v0",
    session_at: normalizeSessionAt(form.sessionAt),
    interventions: mapInterventions(form.interventions),
    observations: String(form.observations).trim(),
    patient_reported_response: patientResponse || null,
  };
}

export function buildNoteAssistPayload(form) {
  const observationsDraft = String(form.observations || "").trim();
  const patientResponse = String(form.patientReportedResponse || "").trim();
  return {
    profile_version: "clinical_session_note_assist_v0",
    interventions: mapInterventions(form.interventions),
    observations_draft: observationsDraft || null,
    patient_reported_response: patientResponse || null,
  };
}
