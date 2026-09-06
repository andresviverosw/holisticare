/** US-UX-COLDSTART-001 — when to explain Render free-tier API wake during login. */

export const COLD_START_HINT_MS = 2500;

export const COLD_START_HINT_TEXT =
  "Despertando el API… En el plan gratuito de Render el primer request puede tardar ~1 min.";

/**
 * @param {number} elapsedMs
 * @param {number} [thresholdMs]
 * @returns {boolean}
 */
export function shouldShowColdStartHint(elapsedMs, thresholdMs = COLD_START_HINT_MS) {
  const elapsed = Number(elapsedMs);
  const threshold = Number(thresholdMs);
  if (!Number.isFinite(elapsed) || !Number.isFinite(threshold)) return false;
  return elapsed >= threshold;
}
