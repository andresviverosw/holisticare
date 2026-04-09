import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ragApi } from "../services/api";
import { formatApiError } from "../utils/apiErrors";
import { buildIntakePayload, parseCsvList, validateIntakeForm } from "../utils/intakeBuilder";

// Must be RFC-4122 UUID **version 4** (backend validates with Pydantic UUID4).
const DEFAULT_PATIENT_ID = "a1111111-1111-4111-8111-111111111111";

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
  const [patientId, setPatientId] = useState(DEFAULT_PATIENT_ID);
  const [intakeForm, setIntakeForm] = useState(SAMPLE_INTAKE_FORM);
  const [therapies, setTherapies] = useState("acupuntura, fisioterapia, hidroterapia");
  const [language, setLanguage] = useState("es");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showDerivedJson, setShowDerivedJson] = useState(false);

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    try {
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
        patient_id: patientId.trim(),
        intake_json,
        available_therapies: availableTherapies,
        preferred_language: language,
      });
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

  function updateIntakeField(name, value) {
    setIntakeForm((prev) => ({ ...prev, [name]: value }));
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-neutral-900">Generador de planes de tratamiento</h1>
        <p className="text-sm text-neutral-500 mt-1">
          El plan es generado por IA y requiere revisión y aprobación del practicante.
        </p>
      </div>

      <div className="card space-y-6">
        <div>
          <label className="label">ID del paciente (UUID v4)</label>
          <input
            type="text"
            value={patientId}
            onChange={(e) => setPatientId(e.target.value)}
            className="input font-mono text-sm"
            spellCheck={false}
          />
        </div>

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

          <div>
            <button
              type="button"
              className="text-xs text-neutral-500 underline"
              onClick={() => setShowDerivedJson((prev) => !prev)}
            >
              {showDerivedJson ? "Ocultar JSON derivado" : "Ver JSON derivado"}
            </button>
            {showDerivedJson && (
              <pre className="mt-2 rounded border bg-neutral-50 p-3 text-xs overflow-x-auto">
                {JSON.stringify(buildIntakePayload(intakeForm), null, 2)}
              </pre>
            )}
          </div>
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
            disabled={loading}
            className="btn-primary min-w-[160px]"
          >
            {loading ? "Generando…" : "Generar plan IA"}
          </button>
        </div>
      </div>
    </div>
  );
}
