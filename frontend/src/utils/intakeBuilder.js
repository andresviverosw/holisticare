export function parseCsvList(value) {
  return String(value || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export function validateIntakeForm(form) {
  if (!form.chiefComplaint?.trim()) {
    return "El motivo principal de consulta es obligatorio.";
  }
  if (parseCsvList(form.conditions).length === 0) {
    return "Agrega al menos una condición clínica.";
  }
  if (parseCsvList(form.goals).length === 0) {
    return "Agrega al menos un objetivo terapéutico.";
  }
  return null;
}

/**
 * Maps a persisted `generic_holistic_v0` object back to flat Dashboard form fields.
 * Returns null if the payload is missing or not v0.
 */
export function formStateFromIntakeJson(intakeJson) {
  if (!intakeJson || intakeJson.profile_version !== "generic_holistic_v0") {
    return null;
  }
  const demo = intakeJson.demographics || {};
  const listsToCsv = (arr) => (Array.isArray(arr) ? arr.join(", ") : "");
  const bo = intakeJson.baseline_outcomes;
  let baselinePain = "";
  let baselineNotes = "";
  if (bo && typeof bo === "object") {
    if (bo.pain_nrs_0_10 != null && bo.pain_nrs_0_10 !== "") {
      baselinePain = String(bo.pain_nrs_0_10);
    }
    if (bo.notes != null) {
      baselineNotes = String(bo.notes);
    }
  }
  return {
    ageRange: demo.age_range ?? "",
    sexAtBirth: demo.sex_at_birth ?? "",
    chiefComplaint: intakeJson.chief_complaint ?? "",
    conditions: listsToCsv(intakeJson.conditions),
    goals: listsToCsv(intakeJson.goals),
    contraindications: listsToCsv(intakeJson.contraindications),
    currentMedications: listsToCsv(intakeJson.current_medications),
    allergies: listsToCsv(intakeJson.allergies),
    baselinePain,
    baselineNotes,
    psychosocialSummary: intakeJson.psychosocial_summary ?? "",
    priorInterventions: listsToCsv(intakeJson.prior_interventions_tried),
  };
}

export function buildIntakePayload(form) {
  const painRaw = String(form.baselinePain || "").trim();
  const pain = painRaw === "" ? null : Number.parseInt(painRaw, 10);
  const hasBaseline = pain !== null || form.baselineNotes?.trim();

  return {
    profile_version: "generic_holistic_v0",
    demographics: {
      age_range: form.ageRange?.trim() || null,
      sex_at_birth: form.sexAtBirth?.trim() || null,
    },
    chief_complaint: form.chiefComplaint.trim(),
    conditions: parseCsvList(form.conditions),
    goals: parseCsvList(form.goals),
    contraindications: parseCsvList(form.contraindications),
    current_medications: parseCsvList(form.currentMedications),
    allergies: parseCsvList(form.allergies),
    baseline_outcomes: hasBaseline
      ? {
          pain_nrs_0_10: Number.isNaN(pain) ? null : pain,
          notes: form.baselineNotes?.trim() || null,
        }
      : null,
    psychosocial_summary: form.psychosocialSummary?.trim() || null,
    prior_interventions_tried: parseCsvList(form.priorInterventions),
  };
}

