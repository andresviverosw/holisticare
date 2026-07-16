/**
 * US-DIARY-UI — clinician-proxy diary form ↔ patient_diary_v0.
 */

function parseScore(raw, label) {
  const n = Number.parseInt(String(raw ?? "").trim(), 10);
  if (Number.isNaN(n) || n < 0 || n > 10) {
    return { error: `El valor de ${label} debe ser un entero entre 0 y 10.` };
  }
  return { value: n };
}

export function validateDiaryForm(form) {
  const date = String(form?.checkinDate || "").trim();
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
    return "La fecha del check-in es obligatoria (AAAA-MM-DD).";
  }
  for (const [field, label] of [
    ["pain", "dolor"],
    ["sleep", "sueño"],
    ["mood", "ánimo"],
    ["functionScore", "función"],
  ]) {
    const parsed = parseScore(form?.[field], label);
    if (parsed.error) return parsed.error;
  }
  const notes = String(form?.notesEs || "");
  if (notes.length > 1500) {
    return "Las notas no pueden superar 1500 caracteres.";
  }
  return null;
}

export function buildDiaryCheckin(form) {
  const notesRaw = String(form.notesEs || "").trim();
  return {
    profile_version: "patient_diary_v0",
    checkin_date: String(form.checkinDate).trim(),
    pain_nrs_0_10: Number.parseInt(String(form.pain).trim(), 10),
    sleep_quality_0_10: Number.parseInt(String(form.sleep).trim(), 10),
    mood_0_10: Number.parseInt(String(form.mood).trim(), 10),
    function_0_10: Number.parseInt(String(form.functionScore).trim(), 10),
    notes_es: notesRaw ? notesRaw : null,
  };
}
