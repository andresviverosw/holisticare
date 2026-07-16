/**
 * US-ANLY-UI — display helpers for outcomes-trend and plateau-flags payloads.
 */

export function formatOutcomeSeries(series) {
  if (!Array.isArray(series)) return [];
  return series.map((row) => ({
    date: String(row?.entry_date || ""),
    pain: row?.pain_nrs_0_10 ?? null,
    sleep: row?.sleep_quality_0_10 ?? null,
    mood: row?.mood_0_10 ?? null,
    functionScore: row?.function_0_10 ?? null,
  }));
}

export function formatPlateauPayload(payload) {
  const analysisStatus = String(payload?.analysis_status || "");
  if (analysisStatus === "insufficient_data") {
    return {
      analysisStatus,
      flags: [],
      statusLabel: "datos insuficientes",
    };
  }
  const flags = Array.isArray(payload?.flags)
    ? payload.flags.map((f) => ({
        code: String(f?.code || ""),
        severity: String(f?.severity || ""),
        metric: String(f?.metric || ""),
        message: String(f?.message || "").trim(),
        detail: String(f?.detail || "").trim(),
      }))
    : [];
  return {
    analysisStatus: analysisStatus || "ok",
    flags: flags.filter((f) => f.message),
    statusLabel: "análisis disponible",
  };
}
