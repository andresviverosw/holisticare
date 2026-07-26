import { describe, expect, it } from "vitest";
import {
  buildOutcomeChartModel,
  formatOutcomeSeries,
  formatPlateauPayload,
  OUTCOME_KPI_DEFS,
} from "./analyticsDisplay";

describe("formatOutcomeSeries", () => {
  it("returns chronological display rows from API series (date field)", () => {
    expect(
      formatOutcomeSeries([
        {
          date: "2026-07-15",
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

  it("accepts legacy entry_date alias", () => {
    expect(
      formatOutcomeSeries([{ entry_date: "2026-04-01", pain_nrs_0_10: 7 }])[0].date,
    ).toBe("2026-04-01");
  });

  it("handles missing series", () => {
    expect(formatOutcomeSeries(undefined)).toEqual([]);
  });
});

describe("buildOutcomeChartModel", () => {
  const rows = [
    { date: "2026-04-01", pain: 8, sleep: 4, mood: 5, functionScore: 3 },
    { date: "2026-04-08", pain: 6, sleep: 5, mood: 6, functionScore: 4 },
    { date: "2026-04-15", pain: 4, sleep: 6, mood: 7, functionScore: 6 },
  ];

  it("exposes four KPI series with SVG polylines on a 0–10 scale", () => {
    const model = buildOutcomeChartModel(rows, { width: 400, height: 200 });
    expect(OUTCOME_KPI_DEFS).toHaveLength(4);
    expect(model.series).toHaveLength(4);
    expect(model.pointCount).toBe(3);
    expect(model.yTicks.map((t) => t.value)).toEqual([0, 5, 10]);
    for (const s of model.series) {
      expect(s.segments.length).toBeGreaterThan(0);
      expect(s.segments[0].split(" ").length).toBe(3);
    }
    const pain = model.series.find((s) => s.key === "pain");
    expect(pain.label).toBe("Dolor");
    // Higher pain (8) should render above lower pain (4) in SVG coords (smaller y).
    const firstY = Number(pain.segments[0].split(" ")[0].split(",")[1]);
    const lastY = Number(pain.segments[0].split(" ")[2].split(",")[1]);
    expect(firstY).toBeLessThan(lastY);
  });

  it("breaks polyline segments across missing KPI values", () => {
    const sparse = [
      { date: "2026-04-01", pain: 8, sleep: null, mood: 5, functionScore: 3 },
      { date: "2026-04-08", pain: null, sleep: 5, mood: 6, functionScore: 4 },
      { date: "2026-04-15", pain: 4, sleep: 6, mood: 7, functionScore: 6 },
    ];
    const model = buildOutcomeChartModel(sparse);
    const pain = model.series.find((s) => s.key === "pain");
    expect(pain.segments).toHaveLength(2);
    expect(pain.dots).toHaveLength(2);
  });

  it("returns empty series when there are no dated rows", () => {
    const model = buildOutcomeChartModel([]);
    expect(model.pointCount).toBe(0);
    expect(model.series.every((s) => s.segments.length === 0)).toBe(true);
  });

  it("overlays a 4-week pain projection when trajectory is available", () => {
    const model = buildOutcomeChartModel(rows, {
      trajectory: {
        label: "improving",
        latest_pain_nrs: 4,
        projected_pain_nrs_in_4_weeks: 2.5,
        baseline_pain_nrs: 8,
      },
    });
    expect(model.projection).not.toBeNull();
    expect(model.projection.to.date).toBe("2026-05-13"); // 2026-04-15 + 28d
    expect(model.projection.to.value).toBe(2.5);
    expect(model.projection.from.value).toBe(4);
    expect(model.projection.polyline.split(" ")).toHaveLength(2);
    expect(model.xLabels.some((l) => l.date === "2026-05-13")).toBe(true);
    // Projection endpoint should sit to the right of the last observed point.
    const pain = model.series.find((s) => s.key === "pain");
    const lastObservedX = pain.dots[pain.dots.length - 1].x;
    expect(model.projection.to.x).toBeGreaterThan(lastObservedX);
  });

  it("skips projection overlay when trajectory is incomplete", () => {
    const model = buildOutcomeChartModel(rows, {
      trajectory: { label: "improving", latest_pain_nrs: 4 },
    });
    expect(model.projection).toBeNull();
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

  it("filters blank flag messages on ok status", () => {
    const result = formatPlateauPayload({
      analysis_status: "ok",
      flags: [{ code: "X", message: "   " }, { code: "Y", message: "Ok" }],
    });
    expect(result.flags).toEqual([
      { code: "Y", severity: "", metric: "", message: "Ok", detail: "" },
    ]);
  });
});
