/** US-MOB-003 — Plan Review mobile decision-gate helpers (CSS-first). */

/**
 * Stacked full-width action row on mobile; side-by-side from `sm` up.
 * @returns {string}
 */
export function decisionActionsRowClassName() {
  return "flex flex-col gap-3 sm:flex-row w-full";
}

/**
 * Thumb-friendly primary/danger buttons on narrow screens.
 * @param {string} baseClass
 * @returns {string}
 */
export function decisionActionButtonClassName(baseClass) {
  return `${baseClass} w-full sm:w-auto min-h-11 py-3 sm:py-2 justify-center`;
}

/**
 * Sticky dock on small screens so approve/reject stay reachable while scrolling.
 * From `md` up, gate sits in normal document flow as a card.
 * @returns {string}
 */
export function decisionGateShellClassName() {
  return (
    "fixed inset-x-0 bottom-0 z-30 border-t border-yellow-200 bg-yellow-50 " +
    "p-4 pb-[max(1rem,env(safe-area-inset-bottom))] shadow-[0_-4px_12px_rgba(0,0,0,0.08)] space-y-3 " +
    "md:static md:inset-auto md:z-auto md:mt-0 md:rounded-xl md:border md:shadow-sm md:p-6 md:space-y-4"
  );
}

/**
 * Extra bottom padding so content is not hidden under the sticky dock on mobile.
 * @param {boolean} gateVisible
 * @returns {string}
 */
export function planReviewPagePaddingClassName(gateVisible) {
  const base = "p-4 sm:p-8 max-w-4xl mx-auto space-y-6";
  if (gateVisible) {
    return `${base} pb-48 md:pb-8`;
  }
  return base;
}
