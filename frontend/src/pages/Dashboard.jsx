import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ragApi } from "../services/api";
import { formatApiError } from "../utils/apiErrors";
import {
  buildIntakePayload,
  formStateFromIntakeJson,
  parseCsvList,
  validateIntakeForm,
} from "../utils/intakeBuilder";
import { addRecentPatient, listRecentPatients } from "../utils/recentPatients";
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
            <label className="label">ID del paciente (UUID v4)</label>
            <input
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
          </div>
        </div>

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

        <div className="space-y-4">
          <h2 className="text-sm font-semibold text-neutral-700">Intake clínico (formulario)</h2>

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
