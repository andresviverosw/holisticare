/**
 * US-OPS-SPA-HOST — resolve SPA API origin for local Vite proxy vs Render Static Site.
 * @param {string | undefined} envValue import.meta.env.VITE_API_BASE_URL
 * @returns {string}
 */
export function resolveApiBaseUrl(envValue) {
  const raw = typeof envValue === "string" ? envValue.trim() : "";
  if (!raw) return "/api";
  return raw.replace(/\/+$/, "");
}
