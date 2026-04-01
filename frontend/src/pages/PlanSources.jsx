import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ragApi } from "../services/api";
import { formatApiError } from "../utils/apiErrors";

export default function PlanSources() {
  const { planId } = useParams();
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setError(null);
    ragApi.getPlanSources(planId)
      .then((res) => setSources(res.data?.sources || []))
      .catch((err) =>
        setError(formatApiError(err, { fallback: "No se pudieron cargar las fuentes del plan." })),
      )
      .finally(() => setLoading(false));
  }, [planId]);

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      <div>
        <Link to={`/plan/${planId}`} className="text-sm text-brand-600 hover:underline">
          ← Volver al plan
        </Link>
        <h1 className="text-2xl font-bold text-neutral-900 mt-2">Fuentes clínicas del plan</h1>
        <p className="text-sm text-neutral-500 mt-1">
          Estos son los fragmentos de la base de conocimiento que el modelo utilizó para generar el plan.
        </p>
      </div>

      {loading && <p className="text-neutral-500">Cargando fuentes…</p>}

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {!loading && !error && sources.length === 0 && (
        <p className="text-neutral-400 text-sm">No se encontraron fuentes para este plan.</p>
      )}

      {sources.map((chunk) => (
        <div key={chunk.ref_id} className="card space-y-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="badge badge-green font-mono text-xs">{chunk.ref_id}</span>
            {chunk.language && (
              <span className="badge badge-gray">{chunk.language.toUpperCase()}</span>
            )}
            {chunk.evidence_level && (
              <span className="badge badge-yellow">Evidencia {chunk.evidence_level}</span>
            )}
            {chunk.has_contraindication && (
              <span className="badge badge-red">⚠️ Contraindicación</span>
            )}
            {chunk.therapy_type?.map((t) => (
              <span key={t} className="badge badge-gray capitalize">{t}</span>
            ))}
          </div>

          <p className="text-sm text-neutral-700 leading-relaxed">{chunk.content}</p>

          <p className="text-xs text-neutral-400">
            {chunk.source_file} — página {chunk.page_number}
          </p>
        </div>
      ))}
    </div>
  );
}
