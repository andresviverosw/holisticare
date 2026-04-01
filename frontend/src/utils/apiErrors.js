/**
 * Turn an axios-style error into a user-visible string (Spanish).
 * @param {unknown} err
 * @param {{ fallback?: string }} [options]
 */
export function formatApiError(err, options = {}) {
  const fallback = options.fallback ?? "Ha ocurrido un error. Intente de nuevo.";
  const status = err?.response?.status;
  const detail = err?.response?.data?.detail;

  if (Array.isArray(detail)) {
    return detail.map((x) => x.msg || JSON.stringify(x)).join("; ");
  }

  if (typeof detail === "string" && detail.trim()) {
    if (status === 403) return `Acceso denegado (403): ${detail}`;
    if (status === 404) return `No encontrado (404): ${detail}`;
    if (status === 503) return `Servicio externo no disponible temporalmente (503): ${detail}`;
    if (status === 502) return `Respuesta inválida del servidor (502): ${detail}`;
    return detail;
  }

  if (status === 401) return "No autenticado (401). Inicie sesión de nuevo.";
  if (status === 403) return "Acceso denegado (403).";
  if (status === 404) return "Recurso no encontrado (404).";
  if (status === 503) {
    return "Servicio de IA temporalmente no disponible (503). Reintente en 1-2 minutos.";
  }
  if (status === 502) return "El servidor devolvió una respuesta no válida (502). Reintente.";
  if (typeof status === "number" && status >= 500) {
    return `Error interno del servidor (${status}). ${fallback}`;
  }

  return err?.message || fallback;
}
