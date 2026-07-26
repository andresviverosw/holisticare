import { buildOutcomeChartModel, OUTCOME_KPI_DEFS, TRAJECTORY_OVERLAY } from "../utils/analyticsDisplay";

/**
 * US-ANLY-UI — multi-KPI SVG trend chart with optional US-PRED-001 pain projection.
 */
export default function OutcomeTrendChart({ rows, trajectory = null }) {
  const model = buildOutcomeChartModel(rows, { trajectory });
  if (!model.pointCount) return null;

  const { width, height, padding, series, yTicks, xLabels, gridY, projection } = model;
  const aria = projection
    ? "Tendencia de dolor, sueño, ánimo y función con proyección de dolor a 4 semanas"
    : "Tendencia de dolor, sueño, ánimo y función (escala 0 a 10)";

  return (
    <div className="space-y-3" data-testid="outcome-trend-chart">
      <ul className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-neutral-600">
        {OUTCOME_KPI_DEFS.map((kpi) => (
          <li key={kpi.key} className="inline-flex items-center gap-1.5">
            <span
              className="inline-block h-2 w-2 rounded-full"
              style={{ backgroundColor: kpi.color }}
              aria-hidden="true"
            />
            {kpi.label}
          </li>
        ))}
        {projection && (
          <li className="inline-flex items-center gap-1.5">
            <span
              className="inline-block h-0.5 w-4 border-t-2 border-dashed"
              style={{ borderColor: TRAJECTORY_OVERLAY.color }}
              aria-hidden="true"
            />
            {TRAJECTORY_OVERLAY.label}
            {projection.labelEs ? ` · ${projection.labelEs}` : ""}
          </li>
        )}
      </ul>

      <div className="w-full overflow-x-auto">
        <svg
          role="img"
          aria-label={aria}
          viewBox={`0 0 ${width} ${height}`}
          className="w-full min-w-[320px] h-auto"
        >
          {gridY.map((y) => (
            <line
              key={`grid-${y}`}
              x1={padding.left}
              x2={width - padding.right}
              y1={y}
              y2={y}
              stroke="#e9ecef"
              strokeWidth="1"
            />
          ))}

          {yTicks.map((tick) => (
            <text
              key={`ytick-${tick.value}`}
              x={padding.left - 8}
              y={tick.y + 3}
              textAnchor="end"
              className="fill-neutral-500"
              fontSize="10"
            >
              {tick.value}
            </text>
          ))}

          {xLabels.map((label) => (
            <text
              key={`xlabel-${label.date}-${label.x}`}
              x={label.x}
              y={height - 8}
              textAnchor="middle"
              className="fill-neutral-500"
              fontSize="10"
            >
              {label.date}
            </text>
          ))}

          {series.map((s) =>
            s.segments.map((points, idx) => (
              <polyline
                key={`${s.key}-seg-${idx}`}
                fill="none"
                stroke={s.color}
                strokeWidth="2"
                strokeLinejoin="round"
                strokeLinecap="round"
                points={points}
              />
            )),
          )}

          {projection && (
            <>
              <polyline
                fill="none"
                stroke={projection.color}
                strokeWidth="2"
                strokeDasharray="6 4"
                strokeLinecap="round"
                points={projection.polyline}
              />
              <circle
                cx={projection.to.x}
                cy={projection.to.y}
                r="4"
                fill="#fff"
                stroke={projection.color}
                strokeWidth="2"
              >
                <title>
                  Proyección dolor: {projection.to.value} ({projection.to.date})
                </title>
              </circle>
            </>
          )}

          {series.map((s) =>
            s.dots.map((dot) => (
              <circle
                key={`${s.key}-${dot.date}`}
                cx={dot.x}
                cy={dot.y}
                r="3"
                fill={s.color}
              >
                <title>
                  {s.label}: {dot.value} ({dot.date})
                </title>
              </circle>
            )),
          )}
        </svg>
      </div>

      <p className="text-[11px] text-neutral-500">
        Escala 0–10 · {model.pointCount} registro{model.pointCount === 1 ? "" : "s"} del diario
        {projection
          ? ` · proyección a ${projection.to.date}: dolor ${projection.to.value}`
          : ""}
      </p>
    </div>
  );
}
