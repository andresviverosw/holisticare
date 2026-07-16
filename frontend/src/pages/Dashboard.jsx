import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ragApi } from "../services/api";
import { formatApiError } from "../utils/apiErrors";
import { formatOutcomeSeries, formatPlateauPayload } from "../utils/analyticsDisplay";
import { buildDiaryCheckin, validateDiaryForm } from "../utils/diaryBuilder";
import {
  buildIntakePayload,
  formStateFromIntakeJson,
  parseCsvList,
  validateIntakeForm,
} from "../utils/intakeBuilder";
import { addRecentPatient, listRecentPatients } from "../utils/recentPatients";
import { normalizeRiskFlags, riskFlagsEmptyLabel } from "../utils/riskFlags";
import {
  buildNoteAssistPayload,
  buildSessionLog,
  validateSessionForm,
} from "../utils/sessionBuilder";
import { isValidUuidV4, newPatientUuid } from "../utils/uuidV4";

const SAMPLE_INTAKE_FORM = {
  ageRange: "40-50",
  sexAtBirth: "F",
  chiefComplaint: "Dolor lumbar crónico con irradiación a pierna izquierda.",
  conditions: "lumbalgia crónica",
  goals: "Reducir dolor, Mejorar movilidad",
  contraindications: "",
  currentMedications: "ibuprofeno 400 mg",
  allergies: "",
  baselinePain: "7",
  baselineNotes: "FUNC afectada para cargas",
  psychosocialSummary: "",
  priorInterventions: "fisioterapia convencional",
};

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

function defaultSessionForm() {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  const local = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`;
  return {
    sessionAt: local,
    interventions: [{ therapyType: "fisioterapia", description: "", durationMinutes: "" }],
    observations: "",
    patientReportedResponse: "",
  };
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [patientId, setPatientId] = useState("");
  const [intakeForm, setIntakeForm] = useState(SAMPLE_INTAKE_FORM);
  const [therapies, setTherapies] = useState("acupuntura, fisioterapia, hidroterapia");
  const [language, setLanguage] = useState("es");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [intakeNotice, setIntakeNotice] = useState(null);
  const [recentPatients, setRecentPatients] = useState(() => listRecentPatients());
  const [memoryBankItems, setMemoryBankItems] = useState([]);
  const [memoryBankQuery, setMemoryBankQuery] = useState("");
  const [memoryBankLoading, setMemoryBankLoading] = useState(false);
  const [memoryBankError, setMemoryBankError] = useState(null);
  const [predictionLoading, setPredictionLoading] = useState(false);
  const [predictionError, setPredictionError] = useState(null);
  const [predictionResult, setPredictionResult] = useState(null);
  const [recommendationLoading, setRecommendationLoading] = useState(false);
  const [recommendationError, setRecommendationError] = useState(null);
  const [recommendationResult, setRecommendationResult] = useState(null);
  const [riskFlags, setRiskFlags] = useState(null);
  const [riskFlagsLoading, setRiskFlagsLoading] = useState(false);
  const [riskFlagsError, setRiskFlagsError] = useState(null);
  const [diaryForm, setDiaryForm] = useState(() => defaultDiaryForm());
  const [diaryItems, setDiaryItems] = useState([]);
  const [diaryLoading, setDiaryLoading] = useState(false);
  const [diaryError, setDiaryError] = useState(null);
  const [diaryNotice, setDiaryNotice] = useState(null);
  const [inviteLoading, setInviteLoading] = useState(false);
  const [inviteError, setInviteError] = useState(null);
  const [inviteLink, setInviteLink] = useState(null);
  const [inviteCopied, setInviteCopied] = useState(false);
  const [outcomeRows, setOutcomeRows] = useState([]);
  const [plateauView, setPlateauView] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [analyticsError, setAnalyticsError] = useState(null);
  const [sessionForm, setSessionForm] = useState(() => defaultSessionForm());
  const [sessionItems, setSessionItems] = useState([]);
  const [sessionLoading, setSessionLoading] = useState(false);
  const [sessionError, setSessionError] = useState(null);
  const [sessionNotice, setSessionNotice] = useState(null);
  const memoryBankQueryRef = useRef(memoryBankQuery);
  memoryBankQueryRef.current = memoryBankQuery;

  const trimmedPatientId = patientId.trim();
  const patientIdReady = trimmedPatientId !== "" && isValidUuidV4(trimmedPatientId);

  const patientIdHint = useMemo(() => {
    if (trimmedPatientId === "") {
      return "Usa «Nuevo paciente» para generar un UUID, pega uno existente, o elige en «Pacientes recientes».";
    }
    if (!isValidUuidV4(trimmedPatientId)) {
      return "El ID debe ser un UUID versión 4 válido (formato 8-4-4-4-12).";
    }
    return null;
  }, [trimmedPatientId]);

  function refreshRecentPatients() {
    setRecentPatients(listRecentPatients());
  }

  const loadMemoryBank = useCallback(async () => {
    setMemoryBankLoading(true);
    setMemoryBankError(null);
    try {
      const res = await ragApi.listPlanMemoryBank({
        q: memoryBankQueryRef.current.trim() || undefined,
        limit: 20,
      });
      setMemoryBankItems(res.data.items || []);
    } catch (err) {
      setMemoryBankError(
        formatApiError(err, { fallback: "No se pudo cargar la biblioteca de plantillas." }),
      );
    } finally {
      setMemoryBankLoading(false);
    }
  }, []);

  useEffect(() => {
    loadMemoryBank();
  }, [loadMemoryBank]);

  async function handleUseTemplate(templateId) {
    setMemoryBankError(null);
    setIntakeNotice(null);
    if (!requirePatientUuidForAction()) return;
    setMemoryBankLoading(true);
    try {
      const res = await ragApi.instantiatePlanMemoryBank(templateId, {
        patient_id: trimmedPatientId,
      });
      navigate(`/plan/${res.data.plan_id}`);
    } catch (err) {
      setMemoryBankError(
        formatApiError(err, { fallback: "No se pudo crear el borrador desde la plantilla." }),
      );
    } finally {
      setMemoryBankLoading(false);
    }
  }

  function requirePatientUuidForAction() {
    if (trimmedPatientId === "") {
      setError("Indica un ID de paciente: genera uno nuevo o pega un UUID v4.");
      return false;
    }
    if (!isValidUuidV4(trimmedPatientId)) {
      setError(
        "El ID de paciente no es un UUID versión 4 válido. Corrige el formato o usa «Nuevo paciente».",
      );
      return false;
    }
    return true;
  }

  function handleNewPatient() {
    setError(null);
    setIntakeNotice(null);
    try {
      setPatientId(newPatientUuid());
      setIntakeNotice("Nuevo ID de paciente generado. Puedes copiarlo o guardar el intake.");
    } catch (e) {
      setError(e?.message || "No se pudo generar el UUID.");
    }
  }

  async function handleCopyPatientId() {
    if (!patientIdReady) return;
    setError(null);
    try {
      await navigator.clipboard.writeText(trimmedPatientId);
      setIntakeNotice("ID copiado al portapapeles.");
    } catch {
      setError("No se pudo copiar al portapapeles. Copia el texto del campo manualmente.");
    }
  }

  async function handleCreateDiaryInvite() {
    setInviteError(null);
    setInviteCopied(false);
    setInviteLink(null);
    if (!requirePatientUuidForAction()) return;
    setInviteLoading(true);
    try {
      const res = await ragApi.createDiaryInvite({ patient_id: trimmedPatientId });
      const path = res.data?.redeem_path || `/login?invite=${res.data?.token || ""}`;
      const absolute =
        res.data?.redeem_url ||
        `${window.location.origin}${path.startsWith("/") ? path : `/${path}`}`;
      setInviteLink(absolute);
      setIntakeNotice("Invitación al diario creada. Copie el enlace y compártalo con el paciente.");
    } catch (err) {
      setInviteError(
        formatApiError(err, { fallback: "No se pudo crear la invitación al diario." }),
      );
    } finally {
      setInviteLoading(false);
    }
  }

  async function handleCopyInviteLink() {
    if (!inviteLink) return;
    try {
      await navigator.clipboard.writeText(inviteLink);
      setInviteCopied(true);
      setTimeout(() => setInviteCopied(false), 2000);
    } catch {
      setInviteError("No se pudo copiar el enlace. Selecciónelo y cópielo manualmente.");
    }
  }

  async function loadRiskFlagsForPatient() {
    setRiskFlagsError(null);
    if (!requirePatientUuidForAction()) return;
    setRiskFlagsLoading(true);
    try {
      const res = await ragApi.getIntakeRiskFlags(trimmedPatientId);
      setRiskFlags(normalizeRiskFlags(res.data));
    } catch (err) {
      setRiskFlags(null);
      setRiskFlagsError(
        formatApiError(err, {
          fallback: "No se pudieron cargar las banderas de riesgo. Continúe con revisión manual.",
        }),
      );
    } finally {
      setRiskFlagsLoading(false);
    }
  }

  async function handleSaveIntake() {
    setIntakeNotice(null);
    setError(null);
    if (!requirePatientUuidForAction()) return;
    const validationError = validateIntakeForm(intakeForm);
    if (validationError) {
      setError(validationError);
      return;
    }
    try {
      const intake_json = buildIntakePayload(intakeForm);
      await ragApi.saveIntake({
        patient_id: trimmedPatientId,
        intake_json,
      });
      addRecentPatient({
        id: trimmedPatientId,
        label: intakeForm.chiefComplaint?.trim().slice(0, 120) || "",
      });
      refreshRecentPatients();
      setIntakeNotice("Intake guardado en el servidor.");
      await loadRiskFlagsForPatient();
    } catch (err) {
      setError(
        formatApiError(err, {
          fallback: "No se pudo guardar el intake.",
        }),
      );
    }
  }

  async function handleLoadIntake() {
    setIntakeNotice(null);
    setError(null);
    if (!requirePatientUuidForAction()) return;
    try {
      const res = await ragApi.getIntake(trimmedPatientId);
      const next = formStateFromIntakeJson(res.data.intake_json);
      if (!next) {
        setError("El intake guardado no es compatible (generic_holistic_v0).");
        return;
      }
      setIntakeForm(next);
      addRecentPatient({
        id: trimmedPatientId,
        label: next.chiefComplaint?.trim().slice(0, 120) || "",
      });
      refreshRecentPatients();
      setIntakeNotice("Intake cargado desde el servidor.");
      await loadRiskFlagsForPatient();
    } catch (err) {
      if (err.response?.status === 404) {
        setError("No hay intake guardado para este paciente.");
        return;
      }
      setError(
        formatApiError(err, {
          fallback: "No se pudo cargar el intake.",
        }),
      );
    }
  }

  async function handleLoadDiaryHistory() {
    setDiaryError(null);
    if (!requirePatientUuidForAction()) return;
    setDiaryLoading(true);
    try {
      const res = await ragApi.listDiary(trimmedPatientId, { limit: 14 });
      setDiaryItems(res.data.items || []);
    } catch (err) {
      setDiaryError(formatApiError(err, { fallback: "No se pudo cargar el diario." }));
    } finally {
      setDiaryLoading(false);
    }
  }

  async function handleSaveDiary() {
    setDiaryError(null);
    setDiaryNotice(null);
    if (!requirePatientUuidForAction()) return;
    const validationError = validateDiaryForm(diaryForm);
    if (validationError) {
      setDiaryError(validationError);
      return;
    }
    setDiaryLoading(true);
    try {
      await ragApi.saveDiary({
        patient_id: trimmedPatientId,
        checkin: buildDiaryCheckin(diaryForm),
      });
      setDiaryNotice("Check-in de diario guardado (registro practicante).");
      await handleLoadDiaryHistory();
    } catch (err) {
      setDiaryError(formatApiError(err, { fallback: "No se pudo guardar el diario." }));
    } finally {
      setDiaryLoading(false);
    }
  }

  async function handleLoadAnalytics() {
    setAnalyticsError(null);
    if (!requirePatientUuidForAction()) return;
    setAnalyticsLoading(true);
    try {
      const [trendRes, plateauRes] = await Promise.all([
        ragApi.getOutcomesTrend(trimmedPatientId),
        ragApi.getPlateauFlags(trimmedPatientId),
      ]);
      setOutcomeRows(formatOutcomeSeries(trendRes.data.series));
      setPlateauView(formatPlateauPayload(plateauRes.data));
    } catch (err) {
      setAnalyticsError(formatApiError(err, { fallback: "No se pudo cargar el progreso." }));
    } finally {
      setAnalyticsLoading(false);
    }
  }

  async function handleLoadSessions() {
    setSessionError(null);
    if (!requirePatientUuidForAction()) return;
    setSessionLoading(true);
    try {
      const res = await ragApi.listSessions(trimmedPatientId, { limit: 20 });
      setSessionItems(res.data.items || []);
    } catch (err) {
      setSessionError(formatApiError(err, { fallback: "No se pudo cargar el historial de sesiones." }));
    } finally {
      setSessionLoading(false);
    }
  }

  async function handleSaveSession() {
    setSessionError(null);
    setSessionNotice(null);
    if (!requirePatientUuidForAction()) return;
    const validationError = validateSessionForm(sessionForm);
    if (validationError) {
      setSessionError(validationError);
      return;
    }
    setSessionLoading(true);
    try {
      await ragApi.createSession({
        patient_id: trimmedPatientId,
        session_log: buildSessionLog(sessionForm),
      });
      setSessionNotice("Sesión registrada.");
      setSessionForm(defaultSessionForm());
      await handleLoadSessions();
    } catch (err) {
      setSessionError(formatApiError(err, { fallback: "No se pudo guardar la sesión." }));
    } finally {
      setSessionLoading(false);
    }
  }

  async function handleSuggestSessionNote() {
    setSessionError(null);
    setSessionNotice(null);
    const interventions = sessionForm.interventions || [];
    if (
      interventions.every(
        (item) => !String(item.therapyType || "").trim() || !String(item.description || "").trim(),
      )
    ) {
      setSessionError("Agrega al menos una intervención antes de sugerir la nota.");
      return;
    }
    setSessionLoading(true);
    try {
      const res = await ragApi.suggestSessionNote({
        session_note_input: buildNoteAssistPayload(sessionForm),
      });
      setSessionForm((prev) => ({
        ...prev,
        observations: res.data.suggested_observations || prev.observations,
        patientReportedResponse:
          res.data.suggested_patient_reported_response || prev.patientReportedResponse,
      }));
      setSessionNotice("Sugerencia de nota aplicada — revise y edite antes de guardar.");
    } catch (err) {
      setSessionError(formatApiError(err, { fallback: "No se pudo sugerir la nota." }));
    } finally {
      setSessionLoading(false);
    }
  }

  function updateDiaryField(field, value) {
    setDiaryForm((prev) => ({ ...prev, [field]: value }));
  }

  function updateSessionIntervention(index, field, value) {
    setSessionForm((prev) => {
      const interventions = [...(prev.interventions || [])];
      interventions[index] = { ...interventions[index], [field]: value };
      return { ...prev, interventions };
    });
  }

  function addSessionIntervention() {
    setSessionForm((prev) => ({
      ...prev,
      interventions: [
        ...(prev.interventions || []),
        { therapyType: "", description: "", durationMinutes: "" },
      ],
    }));
  }

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    setIntakeNotice(null);
    try {
      if (!requirePatientUuidForAction()) {
        return;
      }
      const validationError = validateIntakeForm(intakeForm);
      if (validationError) {
        throw new Error(validationError);
      }
      const intake_json = buildIntakePayload(intakeForm);
      const availableTherapies = parseCsvList(therapies);
      if (availableTherapies.length === 0) {
        throw new Error("Agrega al menos una modalidad disponible.");
      }
      const res = await ragApi.generatePlan({
        patient_id: trimmedPatientId,
        intake_json,
        available_therapies: availableTherapies,
        preferred_language: language,
      });
      addRecentPatient({
        id: trimmedPatientId,
        label: intakeForm.chiefComplaint?.trim().slice(0, 120) || "",
      });
      refreshRecentPatients();
      navigate(`/plan/${res.data.plan_id}`);
    } catch (err) {
      if (typeof err.message === "string") {
        setError(err.message);
        return;
      }
      setError(
        formatApiError(err, {
          fallback: "Error al generar el plan. Intenta de nuevo.",
        }),
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleLoadRecoveryPrediction() {
    setPredictionError(null);
    setPredictionResult(null);
    setRecommendationError(null);
    setRecommendationResult(null);
    setError(null);
    if (!requirePatientUuidForAction()) return;
    setPredictionLoading(true);
    try {
      const res = await ragApi.getRecoveryTrajectory(trimmedPatientId);
      setPredictionResult(res.data);
    } catch (err) {
      setPredictionError(
        formatApiError(err, {
          fallback: "No se pudo estimar la trayectoria de recuperación.",
        }),
      );
    } finally {
      setPredictionLoading(false);
    }
  }

  async function handleLoadRecoveryRecommendations() {
    setRecommendationError(null);
    setRecommendationResult(null);
    setError(null);
    if (!requirePatientUuidForAction()) return;
    setRecommendationLoading(true);
    try {
      const res = await ragApi.getRecoveryRecommendations(trimmedPatientId);
      setRecommendationResult(res.data);
      if (!predictionResult && res.data?.prediction) {
        setPredictionResult(res.data.prediction);
      }
    } catch (err) {
      setRecommendationError(
        formatApiError(err, {
          fallback: "No se pudieron cargar recomendaciones de recuperación.",
        }),
      );
    } finally {
      setRecommendationLoading(false);
    }
  }

  function updateIntakeField(name, value) {
    setIntakeForm((prev) => ({ ...prev, [name]: value }));
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-neutral-900">Generador de planes de tratamiento</h1>
        <p className="text-sm text-neutral-500 mt-1">
          Completa el formulario (no hace falta editar JSON). El plan es generado por IA y requiere revisión
          del practicante.
        </p>
      </div>

      <div className="card space-y-6">
        <div className="flex flex-col gap-3 md:flex-row md:items-end">
          <div className="flex-1 min-w-0">
            <label className="label" htmlFor="patient-id-input">ID del paciente (UUID v4)</label>
            <input
              id="patient-id-input"
              type="text"
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
              className="input font-mono text-sm"
              spellCheck={false}
              autoComplete="off"
              aria-invalid={trimmedPatientId !== "" && !isValidUuidV4(trimmedPatientId)}
              placeholder="Genera un ID nuevo o pega un UUID existente"
            />
            {patientIdHint && (
              <p className="mt-1 text-xs text-neutral-500">{patientIdHint}</p>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            <button type="button" className="btn-secondary text-sm px-3 py-2" onClick={handleNewPatient}>
              Nuevo paciente
            </button>
            <button
              type="button"
              className="btn-secondary text-sm px-3 py-2"
              onClick={handleCopyPatientId}
              disabled={!patientIdReady}
              title={!patientIdReady ? "Necesitas un UUID v4 válido para copiar" : "Copiar al portapapeles"}
            >
              Copiar ID
            </button>
            <button
              type="button"
              className="btn-secondary text-sm px-3 py-2"
              onClick={handleCreateDiaryInvite}
              disabled={!patientIdReady || inviteLoading}
              title={
                !patientIdReady
                  ? "Indica un UUID v4 de paciente válido"
                  : "Crear enlace de invitación de un solo uso para el diario"
              }
            >
              {inviteLoading ? "Creando invitación…" : "Invitar al diario"}
            </button>
            <button
              type="button"
              className="btn-secondary text-sm px-3 py-2"
              onClick={handleLoadIntake}
              disabled={!patientIdReady}
            >
              Cargar intake guardado
            </button>
            <button
              type="button"
              className="btn-secondary text-sm px-3 py-2"
              onClick={handleSaveIntake}
              disabled={!patientIdReady}
            >
              Guardar intake
            </button>
            <button
              type="button"
              className="btn-secondary text-sm px-3 py-2"
              onClick={loadRiskFlagsForPatient}
              disabled={!patientIdReady || riskFlagsLoading}
              title={!patientIdReady ? "Indica un UUID v4 de paciente válido" : undefined}
            >
              {riskFlagsLoading ? "Cargando riesgos…" : "Ver riesgos"}
            </button>
          </div>
        </div>

        {inviteLink && (
          <div className="rounded-lg border border-emerald-200 bg-emerald-50/80 px-3 py-2 space-y-2">
            <p className="text-xs font-medium text-emerald-900">Enlace de invitación (un solo uso)</p>
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
              <code className="flex-1 text-xs font-mono text-neutral-800 break-all bg-white border border-emerald-100 rounded px-2 py-1.5">
                {inviteLink}
              </code>
              <button
                type="button"
                className="btn-secondary text-xs px-2 py-1.5 shrink-0"
                onClick={handleCopyInviteLink}
              >
                {inviteCopied ? "Copiado" : "Copiar enlace"}
              </button>
            </div>
          </div>
        )}
        {inviteError && (
          <div className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700" role="alert">
            {inviteError}
          </div>
        )}

        {recentPatients.length > 0 && (
          <div>
            <p className="text-xs font-medium text-neutral-600 mb-2">Pacientes recientes</p>
            <div className="flex flex-wrap gap-2">
              {recentPatients.map((p) => (
                <button
                  key={p.id}
                  type="button"
                  className="btn-secondary text-xs px-2 py-1 max-w-full truncate"
                  title={p.id}
                  onClick={() => {
                    setPatientId(p.id);
                    setError(null);
                    setIntakeNotice(null);
                  }}
                >
                  {(p.label || "").trim() ? `${p.label.trim().slice(0, 40)}` : p.id.slice(0, 13) + "…"}
                </button>
              ))}
            </div>
            <p className="mt-1 text-xs text-neutral-400">
              Solo en este navegador. Tras elegir, usa «Cargar intake guardado» si el intake está en el servidor.
            </p>
          </div>
        )}

        <section
          className="rounded-lg border border-neutral-200 bg-neutral-50/80 p-4 space-y-3"
          aria-busy={memoryBankLoading}
          aria-labelledby="memory-bank-heading"
        >
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p id="memory-bank-heading" className="text-sm font-semibold text-neutral-800">
                Biblioteca de plantillas
              </p>
              <p className="text-xs text-neutral-500 mt-0.5">
                Planes aprobados guardados como plantilla. Crea un <strong>borrador nuevo</strong> para el paciente
                actual (requiere revisión otra vez).
              </p>
            </div>
            <div className="flex flex-wrap gap-2 w-full sm:w-auto">
              <input
                type="search"
                className="input text-sm flex-1 min-w-[140px]"
                placeholder="Buscar por título, etiqueta o terapia…"
                value={memoryBankQuery}
                onChange={(e) => setMemoryBankQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && loadMemoryBank()}
                aria-label="Buscar plantillas por título, etiqueta o terapia"
              />
              <button
                type="button"
                className="btn-secondary text-sm px-3 py-2"
                onClick={() => loadMemoryBank()}
                disabled={memoryBankLoading}
              >
                {memoryBankLoading ? "Cargando…" : "Buscar"}
              </button>
            </div>
          </div>
          {memoryBankError && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700" role="alert">
              {memoryBankError}
            </div>
          )}
          {memoryBankLoading && memoryBankItems.length === 0 && !memoryBankError && (
            <p className="text-xs text-neutral-500">Cargando plantillas…</p>
          )}
          {memoryBankItems.length === 0 && !memoryBankLoading && !memoryBankError && (
            <p className="text-xs text-neutral-500">No hay plantillas. Aprueba un plan y guárdalo desde la revisión.</p>
          )}
          {memoryBankItems.length > 0 && (
            <ul className="space-y-2">
              {memoryBankItems.map((item) => (
                <li
                  key={item.id}
                  className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between rounded border border-neutral-200 bg-white px-3 py-2"
                >
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-neutral-800 truncate">{item.title}</p>
                    <p className="text-xs text-neutral-500 font-mono truncate">{item.id}</p>
                    {(item.tags?.length > 0 || item.therapy_types?.length > 0) && (
                      <p className="text-xs text-neutral-600 mt-1">
                        {item.tags?.length > 0 && <span>Etiquetas: {item.tags.join(", ")}. </span>}
                        {item.therapy_types?.length > 0 && (
                          <span>Terapias: {item.therapy_types.join(", ")}</span>
                        )}
                      </p>
                    )}
                  </div>
                  <button
                    type="button"
                    className="btn-primary text-sm px-3 py-2 shrink-0"
                    onClick={() => handleUseTemplate(item.id)}
                    disabled={memoryBankLoading || !patientIdReady}
                    title={!patientIdReady ? "Indica un UUID v4 de paciente arriba" : "Crear borrador para este paciente"}
                    aria-label={`Usar plantilla «${item.title}» como borrador para el paciente actual`}
                  >
                    Usar como borrador
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="rounded-lg border border-neutral-200 bg-neutral-50/80 p-4 space-y-3">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-neutral-800">
                Registro de diario (practicante) — US-DIARY-UI
              </p>
              <p className="text-xs text-neutral-500 mt-0.5">
                Check-in proxy para el piloto: el practicante registra dolor, sueño, ánimo y función.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                className="btn-secondary text-sm px-3 py-2"
                onClick={handleLoadDiaryHistory}
                disabled={diaryLoading || !patientIdReady}
              >
                {diaryLoading ? "Cargando…" : "Cargar historial"}
              </button>
              <button
                type="button"
                className="btn-secondary text-sm px-3 py-2"
                onClick={handleSaveDiary}
                disabled={diaryLoading || !patientIdReady}
              >
                Guardar check-in
              </button>
            </div>
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            <div>
              <label className="label">Fecha</label>
              <input
                type="date"
                className="input"
                value={diaryForm.checkinDate}
                onChange={(e) => updateDiaryField("checkinDate", e.target.value)}
              />
            </div>
            <div>
              <label className="label">Dolor 0–10</label>
              <input
                type="number"
                min={0}
                max={10}
                className="input"
                value={diaryForm.pain}
                onChange={(e) => updateDiaryField("pain", e.target.value)}
              />
            </div>
            <div>
              <label className="label">Sueño 0–10</label>
              <input
                type="number"
                min={0}
                max={10}
                className="input"
                value={diaryForm.sleep}
                onChange={(e) => updateDiaryField("sleep", e.target.value)}
              />
            </div>
            <div>
              <label className="label">Ánimo 0–10</label>
              <input
                type="number"
                min={0}
                max={10}
                className="input"
                value={diaryForm.mood}
                onChange={(e) => updateDiaryField("mood", e.target.value)}
              />
            </div>
            <div>
              <label className="label">Función 0–10</label>
              <input
                type="number"
                min={0}
                max={10}
                className="input"
                value={diaryForm.functionScore}
                onChange={(e) => updateDiaryField("functionScore", e.target.value)}
              />
            </div>
            <div className="md:col-span-3">
              <label className="label">Notas (opcional, ES)</label>
              <input
                type="text"
                className="input"
                value={diaryForm.notesEs}
                onChange={(e) => updateDiaryField("notesEs", e.target.value)}
                maxLength={1500}
              />
            </div>
          </div>
          {diaryNotice && (
            <div className="rounded-lg bg-emerald-50 border border-emerald-200 px-3 py-2 text-xs text-emerald-800">
              {diaryNotice}
            </div>
          )}
          {diaryError && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700" role="alert">
              {diaryError}
            </div>
          )}
          {diaryItems.length > 0 && (
            <ul className="text-xs text-neutral-700 space-y-1 max-h-40 overflow-y-auto">
              {diaryItems.map((item) => (
                <li key={item.entry_id} className="border-b border-neutral-100 py-1">
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

        <section className="rounded-lg border border-neutral-200 bg-neutral-50/80 p-4 space-y-3">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-neutral-800">Progreso (US-ANLY-UI)</p>
              <p className="text-xs text-neutral-500 mt-0.5">
                Tendencias del diario y banderas de meseta/empeoramiento (ventana por defecto del API).
              </p>
            </div>
            <button
              type="button"
              className="btn-secondary text-sm px-3 py-2"
              onClick={handleLoadAnalytics}
              disabled={analyticsLoading || !patientIdReady}
            >
              {analyticsLoading ? "Cargando…" : "Cargar progreso"}
            </button>
          </div>
          {analyticsError && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700" role="alert">
              {analyticsError}
            </div>
          )}
          {outcomeRows.length > 0 && (
            <div className="overflow-x-auto">
              <table className="min-w-full text-xs text-left text-neutral-700">
                <thead>
                  <tr className="border-b border-neutral-200 text-neutral-500">
                    <th className="py-1 pr-3 font-medium">Fecha</th>
                    <th className="py-1 pr-3 font-medium">Dolor</th>
                    <th className="py-1 pr-3 font-medium">Sueño</th>
                    <th className="py-1 pr-3 font-medium">Ánimo</th>
                    <th className="py-1 font-medium">Función</th>
                  </tr>
                </thead>
                <tbody>
                  {outcomeRows.map((row) => (
                    <tr key={row.date} className="border-b border-neutral-100">
                      <td className="py-1 pr-3">{row.date}</td>
                      <td className="py-1 pr-3">{row.pain ?? "—"}</td>
                      <td className="py-1 pr-3">{row.sleep ?? "—"}</td>
                      <td className="py-1 pr-3">{row.mood ?? "—"}</td>
                      <td className="py-1">{row.functionScore ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {plateauView && (
            <div className="rounded-lg border border-neutral-200 bg-white p-3 text-sm text-neutral-700 space-y-1">
              <p>
                <span className="font-medium">Estado:</span> {plateauView.statusLabel}
              </p>
              {plateauView.flags.length === 0 ? (
                <p className="text-xs text-neutral-500">
                  {plateauView.analysisStatus === "insufficient_data"
                    ? "Datos insuficientes para alertas (mínimo de registros del diario)."
                    : "Sin banderas de meseta o empeoramiento en la ventana."}
                </p>
              ) : (
                <ul className="list-disc pl-5 space-y-1 text-xs">
                  {plateauView.flags.map((flag) => (
                    <li key={flag.code}>
                      <span className="font-medium">{flag.message}</span>
                      {flag.detail ? ` — ${flag.detail}` : ""}
                      {flag.severity ? ` (${flag.severity})` : ""}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </section>

        <section className="rounded-lg border border-neutral-200 bg-neutral-50/80 p-4 space-y-3">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-neutral-800">Sesión clínica (US-SESS-UI)</p>
              <p className="text-xs text-neutral-500 mt-0.5">
                Registro estructurado de intervenciones y observaciones; sugerencia de nota opcional.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                className="btn-secondary text-sm px-3 py-2"
                onClick={handleLoadSessions}
                disabled={sessionLoading || !patientIdReady}
              >
                Historial
              </button>
              <button
                type="button"
                className="btn-secondary text-sm px-3 py-2"
                onClick={handleSuggestSessionNote}
                disabled={sessionLoading || !patientIdReady}
              >
                Sugerir nota
              </button>
              <button
                type="button"
                className="btn-secondary text-sm px-3 py-2"
                onClick={handleSaveSession}
                disabled={sessionLoading || !patientIdReady}
              >
                Guardar sesión
              </button>
            </div>
          </div>
          <div>
            <label className="label" htmlFor="session-at-input">Fecha y hora</label>
            <input
              id="session-at-input"
              type="datetime-local"
              className="input"
              value={sessionForm.sessionAt}
              onChange={(e) => setSessionForm((prev) => ({ ...prev, sessionAt: e.target.value }))}
            />
          </div>
          {(sessionForm.interventions || []).map((item, index) => (
            <div key={`iv-${index}`} className="grid gap-2 md:grid-cols-3">
              <div>
                <label className="label" htmlFor={`session-therapy-${index}`}>Tipo de terapia</label>
                <input
                  id={`session-therapy-${index}`}
                  type="text"
                  className="input"
                  value={item.therapyType}
                  onChange={(e) => updateSessionIntervention(index, "therapyType", e.target.value)}
                />
              </div>
              <div>
                <label className="label" htmlFor={`session-desc-${index}`}>Descripción</label>
                <input
                  id={`session-desc-${index}`}
                  type="text"
                  className="input"
                  value={item.description}
                  onChange={(e) => updateSessionIntervention(index, "description", e.target.value)}
                />
              </div>
              <div>
                <label className="label" htmlFor={`session-duration-${index}`}>Duración (min)</label>
                <input
                  id={`session-duration-${index}`}
                  type="number"
                  min={1}
                  className="input"
                  value={item.durationMinutes}
                  onChange={(e) => updateSessionIntervention(index, "durationMinutes", e.target.value)}
                />
              </div>
            </div>
          ))}
          <button type="button" className="text-xs text-teal-700 underline" onClick={addSessionIntervention}>
            + Añadir intervención
          </button>
          <div>
            <label className="label" htmlFor="session-observations">Observaciones *</label>
            <textarea
              id="session-observations"
              rows={3}
              className="input"
              value={sessionForm.observations}
              onChange={(e) => setSessionForm((prev) => ({ ...prev, observations: e.target.value }))}
            />
          </div>
          <div>
            <label className="label" htmlFor="session-patient-response">Respuesta reportada por el paciente</label>
            <textarea
              id="session-patient-response"
              rows={2}
              className="input"
              value={sessionForm.patientReportedResponse}
              onChange={(e) =>
                setSessionForm((prev) => ({ ...prev, patientReportedResponse: e.target.value }))
              }
            />
          </div>
          {sessionNotice && (
            <div className="rounded-lg bg-emerald-50 border border-emerald-200 px-3 py-2 text-xs text-emerald-800">
              {sessionNotice}
            </div>
          )}
          {sessionError && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700" role="alert">
              {sessionError}
            </div>
          )}
          {sessionItems.length > 0 && (
            <ul className="text-xs text-neutral-700 space-y-1 max-h-40 overflow-y-auto">
              {sessionItems.map((item) => (
                <li key={item.session_id} className="border-b border-neutral-100 py-1">
                  <span className="font-medium">{item.occurred_at}</span>
                  {" — "}
                  {(item.session_log?.interventions || [])
                    .map((iv) => iv.therapy_type)
                    .filter(Boolean)
                    .join(", ") || "sin intervenciones"}
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="rounded-lg border border-neutral-200 bg-neutral-50/80 p-4 space-y-3">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-neutral-800">Predicción de recuperación (US-PRED-001)</p>
              <p className="text-xs text-neutral-500 mt-0.5">
                Estimación orientativa basada en tendencia de dolor del diario del paciente.
              </p>
            </div>
            <button
              type="button"
              className="btn-secondary text-sm px-3 py-2"
              onClick={handleLoadRecoveryPrediction}
              disabled={predictionLoading || !patientIdReady}
              title={!patientIdReady ? "Indica un UUID v4 de paciente válido" : undefined}
            >
              {predictionLoading ? "Calculando…" : "Calcular trayectoria"}
            </button>
          </div>
          {predictionError && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700" role="alert">
              {predictionError}
            </div>
          )}
          {predictionResult && (
            <div className="rounded-lg border border-neutral-200 bg-white p-3 text-sm text-neutral-700 space-y-1">
              <p>
                <span className="font-medium">Estado:</span>{" "}
                {predictionResult.analysis_status === "ok" ? "estimación disponible" : "datos insuficientes"}
              </p>
              {predictionResult.analysis_status === "ok" && predictionResult.trajectory ? (
                <>
                  <p>
                    <span className="font-medium">Trayectoria:</span> {predictionResult.trajectory.label}
                  </p>
                  <p>
                    <span className="font-medium">Proyección dolor en 4 semanas:</span>{" "}
                    {predictionResult.trajectory.projected_pain_nrs_in_4_weeks}
                  </p>
                  <p className="text-xs text-neutral-500">{predictionResult.trajectory.rationale}</p>
                </>
              ) : (
                <p className="text-xs text-neutral-500">
                  {predictionResult.reason || "No hay datos suficientes para estimar trayectoria."}
                </p>
              )}
            </div>
          )}
        </section>

        <section className="rounded-lg border border-neutral-200 bg-neutral-50/80 p-4 space-y-3">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-neutral-800">Recomendaciones clínicas (US-PRED-002)</p>
              <p className="text-xs text-neutral-500 mt-0.5">
                Sugerencias orientativas derivadas de la trayectoria para apoyar la siguiente decisión clínica.
              </p>
            </div>
            <button
              type="button"
              className="btn-secondary text-sm px-3 py-2"
              onClick={handleLoadRecoveryRecommendations}
              disabled={recommendationLoading || !patientIdReady}
              title={!patientIdReady ? "Indica un UUID v4 de paciente válido" : undefined}
            >
              {recommendationLoading ? "Cargando…" : "Cargar recomendaciones"}
            </button>
          </div>
          {recommendationError && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700" role="alert">
              {recommendationError}
            </div>
          )}
          {recommendationResult && (
            <div className="rounded-lg border border-neutral-200 bg-white p-3 text-sm text-neutral-700 space-y-2">
              <p>
                <span className="font-medium">Estado:</span>{" "}
                {recommendationResult.recommendation_status === "ok"
                  ? "recomendaciones disponibles"
                  : "datos insuficientes"}
              </p>
              {recommendationResult.recommendation_status === "ok" ? (
                <>
                  {Array.isArray(recommendationResult.recommendations) &&
                  recommendationResult.recommendations.length > 0 ? (
                    <ul className="list-disc pl-5 space-y-1">
                      {recommendationResult.recommendations.map((item) => (
                        <li key={item.code}>
                          <span className="font-medium">{item.title}:</span> {item.description}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-xs text-neutral-500">
                      No hay recomendaciones disponibles para esta estimación.
                    </p>
                  )}
                  {Array.isArray(recommendationResult.safety_notes) &&
                    recommendationResult.safety_notes.length > 0 && (
                      <div className="rounded-lg bg-amber-50 border border-amber-200 px-3 py-2 text-xs text-amber-800">
                        <p className="font-medium">Notas de seguridad</p>
                        <ul className="list-disc pl-5 mt-1 space-y-1">
                          {recommendationResult.safety_notes.map((note, idx) => (
                            <li key={`${idx}-${note}`}>{note}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                </>
              ) : (
                <p className="text-xs text-neutral-500">
                  {recommendationResult.reason || "No hay datos suficientes para sugerir ajustes del plan."}
                </p>
              )}
            </div>
          )}
        </section>

        <div className="space-y-4">
          <h2 className="text-sm font-semibold text-neutral-700">Intake clínico (formulario)</h2>

          <section
            className="rounded-lg border border-amber-200 bg-amber-50/60 p-3 space-y-2"
            aria-labelledby="risk-flags-heading"
          >
            <div className="flex items-center justify-between gap-2">
              <p id="risk-flags-heading" className="text-sm font-semibold text-neutral-800">
                Banderas de riesgo (US-INT-002)
              </p>
              {riskFlagsLoading && <span className="text-xs text-neutral-500">Analizando…</span>}
            </div>
            {riskFlagsError && (
              <div className="rounded bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700" role="alert">
                {riskFlagsError}
              </div>
            )}
            {riskFlags && riskFlags.length === 0 && !riskFlagsError && (
              <p className="text-xs text-neutral-600">{riskFlagsEmptyLabel()}</p>
            )}
            {riskFlags && riskFlags.length > 0 && (
              <ul className="list-disc pl-5 space-y-1 text-xs text-neutral-800">
                {riskFlags.map((flag) => (
                  <li key={`${flag.code}-${flag.message}`}>
                    {flag.severity ? (
                      <span className="font-medium uppercase tracking-wide mr-1">{flag.severity}</span>
                    ) : null}
                    {flag.message}
                  </li>
                ))}
              </ul>
            )}
            {!riskFlags && !riskFlagsError && !riskFlagsLoading && (
              <p className="text-xs text-neutral-500">
                Guarde o cargue el intake, o pulse «Ver riesgos», para analizar contraindicaciones.
              </p>
            )}
          </section>

          <div>
            <label className="label">Motivo principal de consulta *</label>
            <textarea
              rows={3}
              value={intakeForm.chiefComplaint}
              onChange={(e) => updateIntakeField("chiefComplaint", e.target.value)}
              className="input"
            />
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="label">Rango de edad</label>
              <input
                type="text"
                value={intakeForm.ageRange}
                onChange={(e) => updateIntakeField("ageRange", e.target.value)}
                className="input"
                placeholder="40-50"
              />
            </div>
            <div>
              <label className="label">Sexo al nacer</label>
              <input
                type="text"
                value={intakeForm.sexAtBirth}
                onChange={(e) => updateIntakeField("sexAtBirth", e.target.value)}
                className="input"
                placeholder="F / M / Otro"
              />
            </div>
          </div>

          <div>
            <label className="label">Condiciones clínicas * (separadas por coma)</label>
            <input
              type="text"
              value={intakeForm.conditions}
              onChange={(e) => updateIntakeField("conditions", e.target.value)}
              className="input"
              placeholder="lumbalgia crónica, ciática"
            />
          </div>

          <div>
            <label className="label">Objetivos terapéuticos * (separados por coma)</label>
            <input
              type="text"
              value={intakeForm.goals}
              onChange={(e) => updateIntakeField("goals", e.target.value)}
              className="input"
              placeholder="reducir dolor, mejorar movilidad"
            />
          </div>

          <div>
            <label className="label">Contraindicaciones (coma)</label>
            <input
              type="text"
              value={intakeForm.contraindications}
              onChange={(e) => updateIntakeField("contraindications", e.target.value)}
              className="input"
            />
          </div>

          <div>
            <label className="label">Medicamentos actuales (coma)</label>
            <input
              type="text"
              value={intakeForm.currentMedications}
              onChange={(e) => updateIntakeField("currentMedications", e.target.value)}
              className="input"
            />
          </div>

          <div>
            <label className="label">Alergias (coma)</label>
            <input
              type="text"
              value={intakeForm.allergies}
              onChange={(e) => updateIntakeField("allergies", e.target.value)}
              className="input"
            />
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="label">Dolor basal (0-10)</label>
              <input
                type="number"
                min={0}
                max={10}
                value={intakeForm.baselinePain}
                onChange={(e) => updateIntakeField("baselinePain", e.target.value)}
                className="input"
              />
            </div>
            <div>
              <label className="label">Notas de outcomes basales</label>
              <input
                type="text"
                value={intakeForm.baselineNotes}
                onChange={(e) => updateIntakeField("baselineNotes", e.target.value)}
                className="input"
              />
            </div>
          </div>

          <div>
            <label className="label">Resumen psicosocial</label>
            <textarea
              rows={2}
              value={intakeForm.psychosocialSummary}
              onChange={(e) => updateIntakeField("psychosocialSummary", e.target.value)}
              className="input"
            />
          </div>

          <div>
            <label className="label">Intervenciones previas (coma)</label>
            <input
              type="text"
              value={intakeForm.priorInterventions}
              onChange={(e) => updateIntakeField("priorInterventions", e.target.value)}
              className="input"
            />
          </div>

          <details className="rounded-lg border border-neutral-200 bg-neutral-50/80 px-3 py-2">
            <summary className="cursor-pointer text-xs font-medium text-neutral-600">
              Avanzado: vista JSON (solo depuración / integración)
            </summary>
            <p className="mt-2 text-xs text-neutral-500">
              El envío al servidor usa el mismo objeto; no necesitas copiar JSON manualmente.
            </p>
            <pre className="mt-2 rounded border bg-white p-3 text-xs overflow-x-auto">
              {JSON.stringify(buildIntakePayload(intakeForm), null, 2)}
            </pre>
          </details>
        </div>

        <div>
          <label className="label">Modalidades disponibles (separadas por coma)</label>
          <input
            type="text"
            value={therapies}
            onChange={(e) => setTherapies(e.target.value)}
            className="input"
            placeholder="acupuntura, fisioterapia, hidroterapia"
          />
        </div>

        <div>
          <label className="label">Idioma del plan</label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="input"
          >
            <option value="es">Español</option>
            <option value="en">English</option>
          </select>
        </div>

        {intakeNotice && (
          <div className="rounded-lg bg-emerald-50 border border-emerald-200 px-4 py-3 text-sm text-emerald-800">
            {intakeNotice}
          </div>
        )}

        {error && (
          <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="flex items-center justify-between pt-2">
          <p className="text-xs text-neutral-400">
            El plan generado requiere aprobación antes de activarse.
          </p>
          <button
            onClick={handleGenerate}
            disabled={loading || !patientIdReady}
            className="btn-primary min-w-[160px]"
            title={!patientIdReady ? "Indica un UUID v4 de paciente válido" : undefined}
          >
            {loading ? "Generando…" : "Generar plan IA"}
          </button>
        </div>
      </div>
    </div>
  );
}
