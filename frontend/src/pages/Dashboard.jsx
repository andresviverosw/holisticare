import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ragApi } from "../services/api";

const SAMPLE_INTAKE = {
  patient_id: "00000000-0000-0000-0000-000000000001",
  age: 45,
  sex: "F",
  chief_complaint: "Dolor lumbar crónico con irradiación a pierna izquierda",
  duration_weeks: 8,
  prior_treatments: ["fisioterapia convencional", "AINES"],
  medications: ["ibuprofeno 400mg", "omeprazol"],
  contraindications: [],
  baseline_scores: { NRS_pain: 7, ODI: 45, PSQI: 14 },
};

export default function Dashboard() {
  const navigate = useNavigate();
  const [intakeJson, setIntakeJson] = useState(JSON.stringify(SAMPLE_INTAKE, null, 2));
  const [therapies, setTherapies] = useState("acupunctura, fisioterapia, hidroterapia");
  const [language, setLanguage] = useState("es");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    try {
      const intake = JSON.parse(intakeJson);
      const res = await ragApi.generatePlan({
        patient_id: intake.patient_id,
        intake_json: intake,
        available_therapies: therapies.split(",").map((t) => t.trim()),
        preferred_language: language,
      });
      navigate(`/plan/${res.data.plan_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Error al generar el plan. Intenta de nuevo.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-neutral-900">Generador de planes de tratamiento</h1>
        <p className="text-sm text-neutral-500 mt-1">
          El plan es generado por IA y requiere revisión y aprobación del practicante.
        </p>
      </div>

      {/* Form */}
      <div className="card space-y-6">
        {/* Intake JSON */}
        <div>
          <label className="label">Perfil del paciente (JSON de intake)</label>
          <textarea
            rows={14}
            value={intakeJson}
            onChange={(e) => setIntakeJson(e.target.value)}
            className="input font-mono text-xs"
            spellCheck={false}
          />
        </div>

        {/* Therapies */}
        <div>
          <label className="label">Modalidades disponibles (separadas por coma)</label>
          <input
            type="text"
            value={therapies}
            onChange={(e) => setTherapies(e.target.value)}
            className="input"
            placeholder="acupunctura, fisioterapia, hidroterapia"
          />
        </div>

        {/* Language */}
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

        {/* Error */}
        {error && (
          <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Submit */}
        <div className="flex items-center justify-between pt-2">
          <p className="text-xs text-neutral-400">
            ⚠️ El plan generado siempre requiere aprobación antes de activarse.
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
