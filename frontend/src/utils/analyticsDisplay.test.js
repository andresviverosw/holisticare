import { describe, expect, it } from "vitest";
import { formatOutcomeSeries, formatPlateauPayload } from "./analyticsDisplay";

describe("formatOutcomeSeries", () => {
  it("returns chronological display rows from API series", () => {
    expect(
      formatOutcomeSeries([
        {
          entry_date: "2026-07-15",
          pain_nrs_0_10: 6,
          sleep_quality_0_10: 5,
          mood_0_10: 4,
          function_0_10: 3,
        },
      ]),
    ).toEqual([
      {
        date: "2026-07-15",
        pain: 6,
        sleep: 5,
        mood: 4,
        functionScore: 3,
      },
    ]);
  });

  it("handles missing series", () => {
    expect(formatOutcomeSeries(undefined)).toEqual([]);
  });
});

describe("formatPlateauPayload", () => {
  it("surfaces insufficient_data without flags", () => {
    expect(
      formatPlateauPayload({
        analysis_status: "insufficient_data",
        flags: [{ code: "X", message: "should ignore" }],
      }),
    ).toEqual({
      analysisStatus: "insufficient_data",
      flags: [],
      statusLabel: "datos insuficientes",
    });
  });

  it("maps ok flags with Spanish message/detail", () => {
    const result = formatPlateauPayload({
      analysis_status: "ok",
      flags: [
        {
          code: "PAIN_WORSENING",
          severity: "high",
          metric: "pain_nrs_0_10",
          message: "Dolor en empeoramiento",
          detail: "Comparación de mitades del periodo.",
        },
      ],
    });
    expect(result.analysisStatus).toBe("ok");
    expect(result.statusLabel).toBe("análisis disponible");
    expect(result.flags).toHaveLength(1);
    expect(result.flags[0].message).toBe("Dolor en empeoramiento");
  });
});
