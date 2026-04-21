import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ragApi } from "../services/api";
import { formatApiError } from "../utils/apiErrors";

function TherapyCard({ therapy }) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-neutral-50 p-4 space-y-2">
      <div className="flex items-center gap-2">
        <span className="font-semibold text-sm capitalize text-neutral-800">{therapy.type}</span>
        <span className="badge-gray badge">{therapy.frequency}</span>
        {therapy.duration_minutes && (
          <span className="badge-gray badge">{therapy.duration_minutes} min</span>
        )}
      </div>
      <p className="text-sm text-neutral-600">{therapy.rationale}</p>
      {therapy.citations?.length > 0 && (
        <div className="flex flex-wrap gap-1 pt-1">
          {therapy.citations.map((ref) => (
            <span key={ref} className="badge badge-green text-xs font-mono">{ref}</span>
          ))}
        </div>
      )}
    </div>
  );
}

function WeekPanel({ week }) {
  return (
    <div className="card space-y-4">
      <h3 className="font-semibold text-neutral-800">Semana {week.week}</h3>

      {/* Goals */}
      <div>
        <p className="text-xs font-medium text-neutral-500 uppercase tracking-wide mb-1">Objetivos</p>
        <ul className="list-disc list-inside space-y-1">
          {week.goals?.map((g, i) => (
            <li key={i} className="text-sm text-neutral-700">{g}</li>
          ))}
        </ul>
      </div>

      {/* Therapies */}
      <div>
        <p className="text-xs font-medium text-neutral-500 uppercase tracking-wide mb-2">Terapias</p>
        <div className="space-y-2">
          {week.therapies?.map((t, i) => <TherapyCard key={i} therapy={t} />)}
        </div>
      </div>

      {/* Contraindications */}
      {week.contraindications_flagged?.length > 0 && (
        <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3">
          <p className="text-xs font-semibold text-red-700 uppercase tracking-wide mb-1">
            ⚠️ Contraindicaciones detectadas
          </p>
          <ul className="list-disc list-inside space-y-1">
            {week.contraindications_flagged.map((c, i) => (
              <li key={i} className="text-sm text-red-700">{c}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Outcome checkpoints */}
      <div>
        <p className="text-xs font-medium text-neutral-500 uppercase tracking-wide mb-1">
          Puntos de evaluación
        </p>
        <ul className="list-disc list-inside space-y-1">
          {week.outcome_checkpoints?.map((o, i) => (
            <li key={i} className="text-sm text-neutral-600">{o}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function DietEntry({ entry }) {
  return (
    <li className="rounded-lg border border-neutral-200 bg-neutral-50 p-3 text-sm text-neutral-700">
      <p className="font-medium text-neutral-800">{entry.item}</p>
      {entry.rationale && <p className="mt-1">{entry.rationale}</p>}
      {entry.citations?.length > 0 && (
        <div className="flex flex-wrap gap-1 pt-2">
          {entry.citations.map((ref) => (
            <span key={ref} className="badge badge-green text-xs font-mono">{ref}</span>
          ))}
        </div>
      )}
    </li>
  );
}

export default function PlanReview() {
  const { planId } = useParams();
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [approving, setApproving] = useState(false);
  const [notes, setNotes] = useState("");
  const [actionDone, setActionDone] = useState(null);
  const [error, setError] = useState(null);
  const [bankTitle, setBankTitle] = useState("");
  const [bankTags, setBankTags] = useState("");
  const [bankSaving, setBankSaving] = useState(false);
  const [bankMsg, setBankMsg] = useState(null);
  const [bankError, setBankError] = useState(null);
  const [pdfLoading, setPdfLoading] = useState(false);

  useEffect(() => {
    ragApi.getPlan(planId)
      .then((res) => setPlan(res.data))
      .catch((err) => setError(formatApiError(err, { fallback: "No se pudo cargar el plan." })))
      .finally(() => setLoading(false));
  }, [planId]);

  async function handleAddToMemoryBank() {
    setBankSaving(true);
    setBankMsg(null);
    setBankError(null);
    try {
      const tags = bankTags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);
      await ragApi.addPlanToMemoryBank({
        source_plan_id: planId,
        title: bankTitle.trim(),
        tags,
      });
      setBankMsg("Plantilla guardada. En el tablero puedes usar «Usar como borrador» para otro paciente.");
      setBankTitle("");
      setBankTags("");
    } catch (err) {
      setBankError(
        formatApiError(err, {
          fallback: "No se pudo guardar la plantilla.",
        }),
      );
    } finally {
      setBankSaving(false);
    }
  }

  async function handleDecision(action) {
    setApproving(true);
    setError(null);
    try {
      await ragApi.approvePlan(planId, action, notes || null);
      setActionDone(action);
      setPlan((p) => ({ ...p, status: action === "approve" ? "approved" : "rejected" }));
    } catch (err) {
      setError(
        formatApiError(err, { fallback: "Error al procesar la decisión." }),
      );
    } finally {
      setApproving(false);
    }
  }

  async function handleDownloadApprovedPdf() {
    setError(null);
    setPdfLoading(true);
    try {
      const res = await ragApi.downloadPlanPdf(planId);
      const blob = new Blob([res.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `plan-${planId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(
        formatApiError(err, {
          fallback: "No se pudo descargar el PDF del plan aprobado.",
        }),
      );
    } finally {
      setPdfLoading(false);
    }
  }

  if (loading) return <div className="p-8 text-neutral-500">Cargando plan…</div>;
  if (error && !plan) return <div className="p-8 text-red-600">{error}</div>;

  const statusColors = {
    pending_review: "badge-yellow",
    approved: "badge-green",
    rejected: "badge-red",
    active: "badge-green",
  };
  const blockedNutritionCount = plan?.nutrition_safety_flags?.length || 0;

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Link to="/dashboard" className="text-sm text-brand-600 hover:underline">
            ← Volver
          </Link>
          <h1 className="text-2xl font-bold text-neutral-900 mt-2">Revisión del plan</h1>
          <p className="text-xs text-neutral-400 font-mono mt-1">{planId}</p>
        </div>
        <span className={`badge text-sm ${statusColors[plan?.status] || "badge-gray"}`}>
          {plan?.status?.replace("_", " ")}
        </span>
      </div>

      {/* Confidence note */}
      {plan?.confidence_note && (
        <div className="rounded-lg bg-blue-50 border border-blue-200 px-4 py-3 text-sm text-blue-800">
          <span className="font-semibold">Nota del modelo: </span>{plan.confidence_note}
        </div>
      )}

      {blockedNutritionCount > 0 && (
        <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          <span className="font-semibold">Resumen de seguridad nutricional: </span>
          {blockedNutritionCount} recomendación(es) bloqueada(s) por alergias o contraindicaciones.
        </div>
      )}

      {/* Retrieval metadata */}
      {plan?.retrieval_metadata && (
        <div className="card text-xs text-neutral-500 space-y-1">
          <p className="font-semibold text-neutral-700 text-sm mb-2">Metadatos de recuperación</p>
          <p>Consultas generadas: {plan.retrieval_metadata.queries_used?.length}</p>
          <p>Candidatos recuperados: {plan.retrieval_metadata.candidates_retrieved}</p>
          <p>Chunks enviados al LLM: {plan.retrieval_metadata.chunks_passed_to_llm}</p>
          <p>Reranker: {plan.retrieval_metadata.reranker_backend}</p>
        </div>
      )}

      {/* Weekly plan */}
      <div className="space-y-4">
        {plan?.weeks?.map((week) => <WeekPanel key={week.week} week={week} />)}
      </div>

      {/* Nutrition recommendations */}
      {plan?.diet_recommendations && (
        <div className="card space-y-4">
          <p className="text-sm font-semibold text-neutral-700">Recomendaciones nutricionales</p>
          <div>
            <p className="text-xs font-medium text-neutral-500 uppercase tracking-wide mb-2">Qué comer</p>
            {plan?.diet_recommendations?.eat?.length > 0 ? (
              <ul className="space-y-2">
                {plan.diet_recommendations.eat.map((entry, index) => (
                  <DietEntry key={`eat-${index}`} entry={entry} />
                ))}
              </ul>
            ) : (
              <p className="text-sm text-neutral-500">Sin recomendaciones de alimentación en este borrador.</p>
            )}
          </div>
          <div>
            <p className="text-xs font-medium text-neutral-500 uppercase tracking-wide mb-2">Qué evitar</p>
            {plan?.diet_recommendations?.avoid?.length > 0 ? (
              <ul className="space-y-2">
                {plan.diet_recommendations.avoid.map((entry, index) => (
                  <DietEntry key={`avoid-${index}`} entry={entry} />
                ))}
              </ul>
            ) : (
              <p className="text-sm text-neutral-500">Sin restricciones nutricionales adicionales en este borrador.</p>
            )}
          </div>
        </div>
      )}

      {/* Nutrition safety flags */}
      {plan?.nutrition_safety_flags?.length > 0 && (
        <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3">
          <p className="text-xs font-semibold text-red-700 uppercase tracking-wide mb-2">
            ⚠️ Alertas de seguridad nutricional
          </p>
          <ul className="list-disc list-inside space-y-1">
            {plan.nutrition_safety_flags.map((flag, index) => (
              <li key={index} className="text-sm text-red-700">
                {flag.item || "Recomendación nutricional"} bloqueada en sección {flag.section}
                {flag.matched_terms?.length > 0 ? ` (coincidencias: ${flag.matched_terms.join(", ")})` : ""}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Citations */}
      {plan?.citations_used?.length > 0 && (
        <div className="card">
          <p className="text-sm font-semibold text-neutral-700 mb-2">Fuentes utilizadas</p>
          <div className="flex flex-wrap gap-2">
            {plan.citations_used.map((ref) => (
              <span key={ref} className="badge badge-green font-mono">{ref}</span>
            ))}
          </div>
          <Link
            to={`/plan/${planId}/sources`}
            className="text-xs text-brand-600 hover:underline mt-3 block"
          >
            Ver contenido completo de las fuentes →
          </Link>
        </div>
      )}

      {/* Approval gate — only shown when pending */}
      {plan?.status === "pending_review" && !actionDone && (
        <div className="card border-yellow-200 bg-yellow-50 space-y-4">
          <p className="text-sm font-semibold text-yellow-800">
            ⚠️ Este plan requiere revisión y aprobación antes de activarse (NOM-024-SSA3-2012)
          </p>
          <div>
            <label className="label">Notas del practicante (opcional)</label>
            <textarea
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="input"
              placeholder="Ajustes realizados, observaciones clínicas…"
            />
          </div>
          {error && (
            <p className="text-sm text-red-600">{error}</p>
          )}
          <div className="flex gap-3">
            <button
              onClick={() => handleDecision("approve")}
              disabled={approving}
              className="btn-primary"
            >
              {approving ? "Procesando…" : "✓ Aprobar plan"}
            </button>
            <button
              onClick={() => handleDecision("reject")}
              disabled={approving}
              className="btn-danger"
            >
              ✕ Rechazar
            </button>
          </div>
        </div>
      )}

      {/* Action confirmation */}
      {actionDone && (
        <div className={`rounded-lg px-4 py-3 text-sm font-medium ${
          actionDone === "approve"
            ? "bg-brand-50 border border-brand-200 text-brand-700"
            : "bg-red-50 border border-red-200 text-red-700"
        }`}>
          {actionDone === "approve"
            ? "✓ Plan aprobado y vinculado al expediente del paciente."
            : "✕ Plan rechazado. No será activado."}
        </div>
      )}

      {(plan?.status === "approved" || actionDone === "approve") && (
        <div className="card space-y-2">
          <p className="text-sm font-semibold text-neutral-800">Exportar plan aprobado</p>
          <p className="text-xs text-neutral-600">
            Descarga una copia PDF para compartir o archivar en el expediente clínico.
          </p>
          <button
            type="button"
            className="btn-secondary"
            onClick={handleDownloadApprovedPdf}
            disabled={pdfLoading}
          >
            {pdfLoading ? "Generando PDF…" : "Descargar PDF del plan"}
          </button>
        </div>
      )}

      {(plan?.status === "approved" || actionDone === "approve") && (
        <div className="card border-brand-200 bg-brand-50/40 space-y-3">
          <p className="text-sm font-semibold text-neutral-800">Biblioteca de plantillas</p>
          <p className="text-xs text-neutral-600">
            Guarda una copia <strong>sin identificadores de paciente</strong> de este plan aprobado para reutilizarla
            como <strong>borrador</strong> (nuevo plan en revisión) desde el tablero.
          </p>
          <div>
            <label className="label">Título de la plantilla *</label>
            <input
              type="text"
              className="input"
              value={bankTitle}
              onChange={(e) => {
                setBankTitle(e.target.value);
                setBankError(null);
              }}
              placeholder="Ej. Programa lumbalgia 4 semanas"
              aria-required="true"
            />
          </div>
          <div>
            <label className="label">Etiquetas (opcional, separadas por coma)</label>
            <input
              type="text"
              className="input"
              value={bankTags}
              onChange={(e) => {
                setBankTags(e.target.value);
                setBankError(null);
              }}
              placeholder="lumbalgia, evidencia B"
            />
          </div>
          <button
            type="button"
            className="btn-secondary"
            disabled={bankSaving || !bankTitle.trim()}
            onClick={handleAddToMemoryBank}
          >
            {bankSaving ? "Guardando…" : "Guardar en biblioteca"}
          </button>
          {bankError && (
            <p className="text-sm text-red-700" role="alert">
              {bankError}
            </p>
          )}
          {bankMsg && <p className="text-sm text-emerald-800">{bankMsg}</p>}
        </div>
      )}
    </div>
  );
}
