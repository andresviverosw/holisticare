import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ragApi } from "../services/api";
import { formatApiError } from "../utils/apiErrors";

// Must be RFC-4122 UUID **version 4** (backend validates with Pydantic UUID4).
const DEFAULT_PATIENT_ID = "a1111111-1111-4111-8111-111111111111";

const SAMPLE_INTAKE_JSON = {
  profile_version: "generic_holistic_v0",
  demographics: { age_range: "40-50", sex_at_birth: "F" },
  chief_complaint: "Dolor lumbar crónico con irradiación a pierna izquierda.",
  conditions: ["lumbalgia crónica"],
  goals: ["Reducir dolor", "Mejorar movilidad"],
  contraindications: [],
  current_medications: ["ibuprofeno 400 mg"],
  allergies: [],
  baseline_outcomes: { pain_nrs_0_10: 7, notes: "FUNC afectada para cargas" },
  psychosocial_summary: null,
  prior_interventions_tried: ["fisioterapia convencional"],
};

export default function Dashboard() {
  const navigate = useNavigate();
  const [patientId, setPatientId] = useState(DEFAULT_PATIENT_ID);
  const [intakeJson, setIntakeJson] = useState(JSON.stringify(SAMPLE_INTAKE_JSON, null, 2));
  const [therapies, setTherapies] = useState("acupuntura, fisioterapia, hidroterapia");
  const [language, setLanguage] = useState("es");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    try {
      const intake_json = JSON.parse(intakeJson);
      if (intake_json.profile_version !== "generic_holistic_v0") {
        throw new Error("El intake debe usar profile_version generic_holistic_v0");
      }
      const res = await ragApi.generatePlan({
        patient_id: patientId.trim(),
        intake_json,
        available_therapies: therapies.split(",").map((t) => t.trim()).filter(Boolean),
        preferred_language: language,
      });
      navigate(`/plan/${res.data.plan_id}`);
    } catch (err) {
      if (err instanceof SyntaxError) {
        setError("JSON inválido en el intake.");
        return;
      }
      if (err.message?.includes("profile_version")) {
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

        <div>
          <label className="label">Intake JSON (generic_holistic_v0)</label>
          <textarea
            rows={14}
            value={intakeJson}
            onChange={(e) => setIntakeJson(e.target.value)}
            className="input font-mono text-xs"
            spellCheck={false}
          />
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
