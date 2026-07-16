import { describe, expect, it } from "vitest";
import { normalizeRiskFlags, riskFlagsEmptyLabel } from "./riskFlags";

describe("normalizeRiskFlags", () => {
  it("maps API risk_flags to display rows", () => {
    const rows = normalizeRiskFlags({
      patient_id: "550e8400-e29b-41d4-a716-446655440000",
      risk_flags: [
        {
          code: "CONTRAINDICATION_DECLARED",
          severity: "high",
          message: "Se detectaron contraindicaciones declaradas en la historia clínica.",
        },
      ],
    });
    expect(rows).toEqual([
      {
        code: "CONTRAINDICATION_DECLARED",
        severity: "high",
        message: "Se detectaron contraindicaciones declaradas en la historia clínica.",
      },
    ]);
  });

  it("returns empty array when risk_flags is empty or missing", () => {
    expect(normalizeRiskFlags({ risk_flags: [] })).toEqual([]);
    expect(normalizeRiskFlags({})).toEqual([]);
    expect(normalizeRiskFlags(null)).toEqual([]);
  });

  it("drops entries without a message", () => {
    expect(
      normalizeRiskFlags({
        risk_flags: [{ code: "X", severity: "low", message: "  " }, { code: "Y", message: "ok" }],
      }),
    ).toEqual([{ code: "Y", severity: "", message: "ok" }]);
  });
});

describe("riskFlagsEmptyLabel", () => {
  it("returns the Spanish empty-state copy", () => {
    expect(riskFlagsEmptyLabel()).toBe("Sin banderas de riesgo");
  });
});
