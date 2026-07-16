/**
 * US-INT-002-UI — normalize intake risk-flag API payload for Dashboard display.
 */

export function normalizeRiskFlags(payload) {
  const raw = Array.isArray(payload?.risk_flags) ? payload.risk_flags : [];
  return raw
    .map((flag) => ({
      code: String(flag?.code || ""),
      severity: String(flag?.severity || ""),
      message: String(flag?.message || "").trim(),
    }))
    .filter((flag) => flag.message.length > 0);
}

export function riskFlagsEmptyLabel() {
  return "Sin banderas de riesgo";
}
