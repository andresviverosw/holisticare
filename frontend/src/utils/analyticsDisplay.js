/**
 * US-ANLY-UI — display helpers for outcomes-trend and plateau-flags payloads.
 */

/** @typedef {{ key: string, label: string, color: string }} OutcomeKpiDef */

/** @type {OutcomeKpiDef[]} */
export const OUTCOME_KPI_DEFS = [
  { key: "pain", label: "Dolor", color: "#c2410c" },
  { key: "sleep", label: "Sueño", color: "#0369a1" },
  { key: "mood", label: "Ánimo", color: "#0f766e" },
  { key: "functionScore", label: "Función", color: "#1f7d4b" },
];

/** Matches backend recovery projection horizon (US-PRED-001). */
export const TRAJECTORY_PROJECTION_DAYS = 28;

export const TRAJECTORY_OVERLAY = {
  key: "pain_projection",
  label: "Proyección dolor (4 sem)",
  color: "#9a3412",
};

export const TRAJECTORY_LABEL_ES = {
  improving: "mejorando",
  stable: "estable",
  worsening: "empeorando",
};

export function formatOutcomeSeries(series) {
  if (!Array.isArray(series)) return [];
  return series.map((row) => ({
    date: String(row?.date || row?.entry_date || ""),
    pain: row?.pain_nrs_0_10 ?? null,
    sleep: row?.sleep_quality_0_10 ?? null,
    mood: row?.mood_0_10 ?? null,
    functionScore: row?.function_0_10 ?? null,
  }));
}

function isNumericScore(value) {
  return typeof value === "number" && !Number.isNaN(value);
}

function parseIsoDateMs(iso) {
  const ms = Date.parse(`${String(iso).slice(0, 10)}T00:00:00Z`);
  return Number.isFinite(ms) ? ms : null;
}

function addDaysIso(iso, days) {
  const ms = parseIsoDateMs(iso);
  if (ms == null) return null;
  const d = new Date(ms);
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}

/**
 * @param {object | null | undefined} trajectory — US-PRED-001 trajectory object
 * @returns {{ label: string, latestPain: number, projectedPain: number, baselinePain: number | null } | null}
 */
export function normalizeTrajectoryForChart(trajectory) {
  if (!trajectory || typeof trajectory !== "object") return null;
  const latestPain = trajectory.latest_pain_nrs;
  const projectedPain = trajectory.projected_pain_nrs_in_4_weeks;
  if (!isNumericScore(latestPain) || !isNumericScore(projectedPain)) return null;
  return {
    label: String(trajectory.label || ""),
    latestPain,
    projectedPain,
    baselinePain: isNumericScore(trajectory.baseline_pain_nrs) ? trajectory.baseline_pain_nrs : null,
  };
}

/**
 * Build SVG geometry for a multi-KPI outcome trend chart (fixed Y scale 0–10).
 * Optional US-PRED-001 trajectory overlays a dashed 4-week pain projection.
 */
export function buildOutcomeChartModel(rows, options = {}) {
  const width = options.width ?? 640;
  const height = options.height ?? 220;
  const padding = {
    top: options.padding?.top ?? 16,
    right: options.padding?.right ?? 16,
    bottom: options.padding?.bottom ?? 28,
    left: options.padding?.left ?? 32,
  };
  const yMin = 0;
  const yMax = 10;
  const points = (Array.isArray(rows) ? rows : [])
    .filter((row) => row && String(row.date || "").trim() && parseIsoDateMs(row.date) != null)
    .map((row) => ({ ...row, _ms: parseIsoDateMs(row.date) }))
    .sort((a, b) => a._ms - b._ms);

  const n = points.length;
  const innerW = Math.max(width - padding.left - padding.right, 1);
  const innerH = Math.max(height - padding.top - padding.bottom, 1);

  const traj = normalizeTrajectoryForChart(options.trajectory);
  let lastPainPoint = null;
  for (let i = points.length - 1; i >= 0; i -= 1) {
    if (isNumericScore(points[i].pain)) {
      lastPainPoint = points[i];
      break;
    }
  }

  let projectionEndMs = null;
  let projectionEndDate = null;
  if (traj && lastPainPoint) {
    projectionEndDate = addDaysIso(lastPainPoint.date, TRAJECTORY_PROJECTION_DAYS);
    projectionEndMs = parseIsoDateMs(projectionEndDate);
  }

  const domainStart = n > 0 ? points[0]._ms : 0;
  let domainEnd = n > 0 ? points[n - 1]._ms : 1;
  if (projectionEndMs != null && projectionEndMs > domainEnd) {
    domainEnd = projectionEndMs;
  }
  const domainSpan = Math.max(domainEnd - domainStart, 1);

  const xAtMs = (ms) => {
    if (n <= 1 && projectionEndMs == null) return padding.left + innerW / 2;
    return padding.left + ((ms - domainStart) / domainSpan) * innerW;
  };
  const yAt = (value) => {
    const t = (Number(value) - yMin) / (yMax - yMin);
    return padding.top + innerH * (1 - t);
  };

  const series = OUTCOME_KPI_DEFS.map((def) => {
    const segments = [];
    const dots = [];
    let current = [];
    points.forEach((row) => {
      const value = row[def.key];
      if (!isNumericScore(value)) {
        if (current.length) {
          segments.push(current.join(" "));
          current = [];
        }
        return;
      }
      const x = xAtMs(row._ms);
      const y = yAt(value);
      current.push(`${x},${y}`);
      dots.push({ x, y, value, date: row.date });
    });
    if (current.length) segments.push(current.join(" "));
    return { ...def, segments, dots };
  });

  let projection = null;
  if (traj && lastPainPoint && projectionEndDate && projectionEndMs != null) {
    const from = {
      x: xAtMs(lastPainPoint._ms),
      y: yAt(traj.latestPain),
      value: traj.latestPain,
      date: lastPainPoint.date,
    };
    const to = {
      x: xAtMs(projectionEndMs),
      y: yAt(traj.projectedPain),
      value: traj.projectedPain,
      date: projectionEndDate,
    };
    projection = {
      ...TRAJECTORY_OVERLAY,
      labelEs: TRAJECTORY_LABEL_ES[traj.label] || traj.label || "proyección",
      trajectoryLabel: traj.label,
      from,
      to,
      polyline: `${from.x},${from.y} ${to.x},${to.y}`,
    };
  }

  const yTicks = [0, 5, 10].map((value) => ({ value, y: yAt(value) }));
  const xLabels = [];
  if (n > 0) {
    xLabels.push({ date: points[0].date, x: xAtMs(points[0]._ms) });
    if (n > 2) {
      const mid = Math.floor((n - 1) / 2);
      xLabels.push({ date: points[mid].date, x: xAtMs(points[mid]._ms) });
    }
    if (n > 1) {
      xLabels.push({ date: points[n - 1].date, x: xAtMs(points[n - 1]._ms) });
    }
    if (projectionEndDate && !xLabels.some((l) => l.date === projectionEndDate)) {
      xLabels.push({ date: projectionEndDate, x: xAtMs(projectionEndMs) });
    }
  }

  return {
    width,
    height,
    padding,
    series,
    yTicks,
    xLabels,
    pointCount: n,
    gridY: yTicks.map((t) => t.y),
    projection,
  };
}

export function formatPlateauPayload(payload) {
  const analysisStatus = String(payload?.analysis_status || "");
  if (analysisStatus === "insufficient_data") {
    return {
      analysisStatus,
      flags: [],
      statusLabel: "datos insuficientes",
    };
  }
  const flags = Array.isArray(payload?.flags)
    ? payload.flags.map((f) => ({
        code: String(f?.code || ""),
        severity: String(f?.severity || ""),
        metric: String(f?.metric || ""),
        message: String(f?.message || "").trim(),
        detail: String(f?.detail || "").trim(),
      }))
    : [];
  return {
    analysisStatus: analysisStatus || "ok",
    flags: flags.filter((f) => f.message),
    statusLabel: "análisis disponible",
  };
}
