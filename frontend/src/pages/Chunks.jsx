import { useCallback, useEffect, useState } from "react";
import { ragApi } from "../services/api";
import { formatApiError } from "../utils/apiErrors";

const THERAPY_OPTIONS = ["", "acupunctura", "fisioterapia", "hidroterapia", "herbolaria", "psicoemocional"];
const LANG_OPTIONS = [{ value: "", label: "Todos" }, { value: "es", label: "Español" }, { value: "en", label: "English" }];

export default function Chunks() {
  const [chunks, setChunks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({ therapy_type: "", language: "", has_contraindication: "" });

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    const params = {};
    if (filters.therapy_type) params.therapy_type = filters.therapy_type;
    if (filters.language) params.language = filters.language;
    if (filters.has_contraindication !== "") params.has_contraindication = filters.has_contraindication === "true";

    ragApi.listChunks(params)
      .then((res) => setChunks(res.data?.items || []))
      .catch((err) =>
        setError(formatApiError(err, { fallback: "No se pudieron cargar los fragmentos clínicos." })),
      )
      .finally(() => setLoading(false));
  }, [filters]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900">Base de conocimiento clínico</h1>
        <p className="text-sm text-neutral-500 mt-1">
          Fragmentos indexados en pgvector que alimentan el motor RAG.
        </p>
      </div>

      {/* Filters */}
      <div className="card flex gap-4 flex-wrap">
        <div className="flex-1 min-w-[140px]">
          <label className="label">Terapia</label>
          <select
            value={filters.therapy_type}
            onChange={(e) => setFilters((f) => ({ ...f, therapy_type: e.target.value }))}
            className="input"
          >
            {THERAPY_OPTIONS.map((o) => (
              <option key={o} value={o}>{o || "Todas"}</option>
            ))}
          </select>
        </div>

        <div className="flex-1 min-w-[120px]">
          <label className="label">Idioma</label>
          <select
            value={filters.language}
            onChange={(e) => setFilters((f) => ({ ...f, language: e.target.value }))}
            className="input"
          >
            {LANG_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>

        <div className="flex-1 min-w-[160px]">
          <label className="label">Contraindicaciones</label>
          <select
            value={filters.has_contraindication}
            onChange={(e) => setFilters((f) => ({ ...f, has_contraindication: e.target.value }))}
            className="input"
          >
            <option value="">Todos</option>
            <option value="true">Solo contraindicaciones</option>
            <option value="false">Sin contraindicaciones</option>
          </select>
        </div>

        <div className="flex items-end">
          <button onClick={load} className="btn-primary">Filtrar</button>
        </div>
      </div>

      {/* Results */}
      {loading && <p className="text-neutral-500 text-sm">Cargando…</p>}

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {!loading && !error && chunks.length === 0 && (
        <p className="text-neutral-400 text-sm">
          No hay chunks indexados. Ejecuta el pipeline de ingesta primero.
        </p>
      )}

      <div className="space-y-3">
        {chunks.map((chunk) => (
          <div key={chunk.ref_id} className="card space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="badge badge-green font-mono text-xs">{chunk.ref_id}</span>
              {chunk.language && <span className="badge badge-gray">{chunk.language.toUpperCase()}</span>}
              {chunk.evidence_level && <span className="badge badge-yellow">Evidencia {chunk.evidence_level}</span>}
              {chunk.has_contraindication && <span className="badge badge-red">⚠️ Contraindicación</span>}
              {chunk.therapy_type?.map((t) => (
                <span key={t} className="badge badge-gray capitalize">{t}</span>
              ))}
            </div>
            <p className="text-sm text-neutral-700 leading-relaxed line-clamp-3">{chunk.content}</p>
            <p className="text-xs text-neutral-400">{chunk.source_file} — p. {chunk.page_number}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
