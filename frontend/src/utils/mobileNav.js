/** US-MOB-001 — clinician shell mobile nav helpers (Tailwind `md` = 768px). */

export const MOBILE_NAV_BREAKPOINT_PX = 768;

/**
 * @param {number} widthPx
 * @returns {boolean}
 */
export function isMobileNavViewport(widthPx) {
  const w = Number(widthPx);
  if (!Number.isFinite(w)) return false;
  return w < MOBILE_NAV_BREAKPOINT_PX;
}

/**
 * @param {{ currentlyOpen: boolean, toggle?: boolean, forceClosed?: boolean }} opts
 * @returns {boolean}
 */
export function nextMobileNavOpen({ currentlyOpen, toggle = false, forceClosed = false }) {
  if (forceClosed) return false;
  if (toggle) return !currentlyOpen;
  return Boolean(currentlyOpen);
}
