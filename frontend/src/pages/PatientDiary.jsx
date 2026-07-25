import { useCallback, useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { ragApi } from "../services/api";
import { formatApiError } from "../utils/apiErrors";
import { buildDiaryCheckin, validateDiaryForm } from "../utils/diaryBuilder";

function todayIsoDate() {
  return new Date().toISOString().slice(0, 10);
}

function defaultDiaryForm() {
  return {
    checkinDate: todayIsoDate(),
    pain: "5",
    sleep: "5",
    mood: "5",
    functionScore: "5",
    notesEs: "",
  };
}

/**
 * US-DIARY-UI-PATIENT — patient self-serve daily diary (`/diario`).
 * `patient_id` is always the JWT `sub` (never free-typed).
 */
export default function PatientDiary() {
  const { sub } = useAuth();
  const patientId = String(sub || "").trim();

  const [diaryForm, setDiaryForm] = useState(() => defaultDiaryForm());
  const [diaryItems, setDiaryItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);
  const [copied, setCopied] = useState(false);

  const loadHistory = useCallback(async () => {
    if (!patientId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await ragApi.listDiary(patientId, { limit: 14 });
      setDiaryItems(res.data?.items || []);
    } catch (err) {
      setError(formatApiError(err, { fallback: "No se pudo cargar el historial del diario." }));
      setDiaryItems([]);
    } finally {
      setLoading(false);
    }
  }, [patientId]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  function updateField(field, value) {
    setDiaryForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSave(e) {
    e.preventDefault();
    setNotice(null);
    const validationError = validateDiaryForm(diaryForm);
    if (validationError) {
      setError(validationError);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await ragApi.saveDiary({
        patient_id: patientId,
        checkin: buildDiaryCheckin(diaryForm),
      });
      setNotice("Check-in guardado.");
      await loadHistory();
    } catch (err) {
      setError(formatApiError(err, { fallback: "No se pudo guardar el check-in." }));
    } finally {
      setLoading(false);
    }
  }

  async function handleCopyId() {
    try {
      await navigator.clipboard.writeText(patientId);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div className="max-w-lg mx-auto p-4 sm:p-6 space-y-6">
      <div>
        <h1 className="text-xl font-bold text-neutral-900">Mi diario</h1>
        <p className="text-sm text-neutral-500 mt-1">
          Registre cómo se siente hoy (dolor, sueño, ánimo y función). Su clínico verá estos datos
          en el panel de progreso.
        </p>
      </div>

      <div className="rounded-lg border border-neutral-200 bg-white p-3 space-y-2">
        <p className="text-xs font-medium text-neutral-600">Su ID de paciente</p>
        <div className="flex items-center gap-2">
          <code
            className="flex-1 text-xs font-mono text-neutral-800 bg-neutral-50 border border-neutral-100 rounded px-2 py-1.5 truncate"
            title={patientId}
          >
            {patientId}
          </code>
          <button type="button" className="btn-secondary text-xs px-2 py-1.5 shrink-0" onClick={handleCopyId}>
            {copied ? "Copiado" : "Copiar"}
          </button>
        </div>
      </div>

      <form onSubmit={handleSave} className="rounded-lg border border-neutral-200 bg-white p-4 space-y-3">
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <label htmlFor="patient-diary-date" className="label">
              Fecha
            </label>
            <input
              id="patient-diary-date"
              type="date"
              className="input"
              value={diaryForm.checkinDate}
              onChange={(e) => updateField("checkinDate", e.target.value)}
            />
          </div>
          <div>
            <label htmlFor="patient-diary-pain" className="label">
              Dolor 0–10
            </label>
            <input
              id="patient-diary-pain"
              type="number"
              min={0}
              max={10}
              className="input"
              value={diaryForm.pain}
              onChange={(e) => updateField("pain", e.target.value)}
            />
          </div>
          <div>
            <label htmlFor="patient-diary-sleep" className="label">
              Sueño 0–10
            </label>
            <input
              id="patient-diary-sleep"
              type="number"
              min={0}
              max={10}
              className="input"
              value={diaryForm.sleep}
              onChange={(e) => updateField("sleep", e.target.value)}
            />
          </div>
          <div>
            <label htmlFor="patient-diary-mood" className="label">
              Ánimo 0–10
            </label>
            <input
              id="patient-diary-mood"
              type="number"
              min={0}
              max={10}
              className="input"
              value={diaryForm.mood}
              onChange={(e) => updateField("mood", e.target.value)}
            />
          </div>
          <div>
            <label htmlFor="patient-diary-function" className="label">
              Función 0–10
            </label>
            <input
              id="patient-diary-function"
              type="number"
              min={0}
              max={10}
              className="input"
              value={diaryForm.functionScore}
              onChange={(e) => updateField("functionScore", e.target.value)}
            />
          </div>
          <div className="sm:col-span-2">
            <label htmlFor="patient-diary-notes" className="label">
              Notas (opcional)
            </label>
            <input
              id="patient-diary-notes"
              type="text"
              className="input"
              value={diaryForm.notesEs}
              onChange={(e) => updateField("notesEs", e.target.value)}
              maxLength={1500}
            />
          </div>
        </div>

        {notice && (
          <div className="rounded-lg bg-emerald-50 border border-emerald-200 px-3 py-2 text-xs text-emerald-800">
            {notice}
          </div>
        )}
        {error && (
          <div className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700" role="alert">
            {error}
          </div>
        )}

        <button type="submit" className="btn-primary w-full" disabled={loading || !patientId}>
          {loading ? "Guardando…" : "Guardar check-in"}
        </button>
      </form>

      <section className="space-y-2">
        <div className="flex items-center justify-between gap-2">
          <h2 className="text-sm font-semibold text-neutral-800">Historial reciente</h2>
          <button
            type="button"
            className="btn-secondary text-xs px-2 py-1"
            onClick={loadHistory}
            disabled={loading || !patientId}
          >
            Actualizar
          </button>
        </div>
        {diaryItems.length === 0 ? (
          <p className="text-xs text-neutral-500">Aún no hay entradas registradas.</p>
        ) : (
          <ul className="text-xs text-neutral-700 space-y-1 rounded-lg border border-neutral-200 bg-white p-3 max-h-56 overflow-y-auto">
            {diaryItems.map((item) => (
              <li key={item.entry_id || item.entry_date} className="border-b border-neutral-100 py-1 last:border-0">
                <span className="font-medium">{item.entry_date}</span>
                {": "}
                dolor {item.checkin?.pain_nrs_0_10 ?? "—"} · sueño {item.checkin?.sleep_quality_0_10 ?? "—"} ·
                ánimo {item.checkin?.mood_0_10 ?? "—"} · función {item.checkin?.function_0_10 ?? "—"}
                {item.checkin?.notes_es ? ` — ${item.checkin.notes_es}` : ""}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
