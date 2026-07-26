/**
 * Patient-scoped dashboard UI reset helpers (US-ANLY / clinician UX).
 * Keeps derived panels from leaking across patient ID changes.
 */

export const DEFAULT_INTAKE_FORM = {
  ageRange: "40-50",
  sexAtBirth: "F",
  chiefComplaint: "Dolor lumbar crónico con irradiación a pierna izquierda.",
  conditions: "lumbalgia crónica",
  goals: "Reducir dolor, Mejorar movilidad",
  contraindications: "",
  currentMedications: "ibuprofeno 400 mg",
  allergies: "",
  baselinePain: "7",
  baselineNotes: "FUNC afectada para trabajo",
  psychosocialSummary: "",
  priorInterventions: "fisioterapia convencional",
};

export function todayIsoDate(now = new Date()) {
  return now.toISOString().slice(0, 10);
}

export function defaultDiaryForm(now = new Date()) {
  return {
    checkinDate: todayIsoDate(now),
    pain: "5",
    sleep: "5",
    mood: "5",
    functionScore: "5",
    notesEs: "",
  };
}

export function defaultSessionForm(now = new Date()) {
  const pad = (n) => String(n).padStart(2, "0");
  const local = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`;
  return {
    sessionAt: local,
    interventions: [{ therapyType: "fisioterapia", description: "", durationMinutes: "" }],
    observations: "",
    patientReportedResponse: "",
  };
}

/**
 * Patient-bound panel values to clear when switching patients
 * (or when the patient ID becomes empty/invalid).
 * Clinic prefs (therapies/language) are intentionally excluded.
 */
export function createClearedPatientDerivedState(now = new Date()) {
  return {
    intakeForm: { ...DEFAULT_INTAKE_FORM },
    error: null,
    intakeNotice: null,
    predictionError: null,
    predictionResult: null,
    recommendationError: null,
    recommendationResult: null,
    riskFlags: null,
    riskFlagsError: null,
    diaryForm: defaultDiaryForm(now),
    diaryItems: [],
    diaryError: null,
    diaryNotice: null,
    inviteError: null,
    inviteLink: null,
    inviteCopied: false,
    outcomeRows: [],
    plateauView: null,
    analyticsError: null,
    sessionForm: defaultSessionForm(now),
    sessionItems: [],
    sessionError: null,
    sessionNotice: null,
  };
}

/** Lists/results only — used while the ID field is incomplete so prior patient panels do not linger. */
export function createClearedPatientResultPanels(now = new Date()) {
  const { intakeForm, diaryForm, sessionForm, ...panels } = createClearedPatientDerivedState(now);
  void intakeForm;
  void diaryForm;
  void sessionForm;
  return panels;
}
