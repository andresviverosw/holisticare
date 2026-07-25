/**
 * US-OPS-SPA-HOST — resolve axios base URL for local Vite proxy vs Render Static Site.
 */
export function resolveApiBaseUrl(envValue) {
  const raw = typeof envValue === "string" ? envValue.trim() : "";
  if (!raw) return "/api";
  return raw.replace(/\/+$/, "");
}
