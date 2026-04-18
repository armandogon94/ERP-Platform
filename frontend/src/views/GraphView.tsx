import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { AggregateRow } from "../api/reports";

export type ChartType = "bar" | "line" | "pie" | "area";

interface GraphViewProps {
  rows: AggregateRow[];
  chartType: ChartType;
  height?: number;
}

// REVIEW S-6: sourced via CSS var fallback + referencing the industry
// palette indirectly. The palette is the same 10 brand colors from
// CLAUDE.md — if it ever needs to change, the tokens file is the single
// source of truth. Pie slices still need concrete values because SVG
// `fill` doesn't resolve CSS vars in all browsers (Recharts sets inline).
const PIE_COLORS = [
  "var(--accent, #714B67)",
  "#2563EB", // novapay
  "#059669", // medvista
  "#D97706", // urbannest
  "#7C3AED", // swiftroute
  "#06B6D4", // dentaflow
  "#9F1239", // tablesync
  "#EA580C", // cranestack
  "#6D28D9", // edupulse
  "#166534", // jurispath
];

const ACCENT = "var(--accent, #714B67)";
const ACCENT_SOFT = "var(--accent-soft, #efe8ec)";
const GRID_STROKE = "#eee";

// REVIEW S-7: each chart type renders into the same cartesian (or pie)
// wrapper. Routing via a lookup map is shorter and easier to extend than
// a 4-branch nested ternary.
const CARTESIAN_RENDERERS: Record<
  Exclude<ChartType, "pie">,
  (data: { group: string; value: number }[]) => JSX.Element
> = {
  bar: (data) => (
    <BarChart data={data}>
      <CartesianGrid stroke={GRID_STROKE} strokeDasharray="3 3" />
      <XAxis dataKey="group" />
      <YAxis />
      <Tooltip />
      <Bar dataKey="value" fill={ACCENT} />
    </BarChart>
  ),
  line: (data) => (
    <LineChart data={data}>
      <CartesianGrid stroke={GRID_STROKE} strokeDasharray="3 3" />
      <XAxis dataKey="group" />
      <YAxis />
      <Tooltip />
      <Line
        type="monotone"
        dataKey="value"
        stroke={ACCENT}
        strokeWidth={2}
      />
    </LineChart>
  ),
  area: (data) => (
    <AreaChart data={data}>
      <CartesianGrid stroke={GRID_STROKE} strokeDasharray="3 3" />
      <XAxis dataKey="group" />
      <YAxis />
      <Tooltip />
      <Area type="monotone" dataKey="value" stroke={ACCENT} fill={ACCENT_SOFT} />
    </AreaChart>
  ),
};

export default function GraphView({
  rows,
  chartType,
  height = 320,
}: GraphViewProps) {
  if (rows.length === 0) {
    return <div>No data</div>;
  }

  const data = rows.map((r) => ({
    group: r.group === null ? "—" : String(r.group),
    value: r.value,
  }));

  const chart =
    chartType === "pie" ? (
      <PieChart>
        <Tooltip />
        <Legend />
        <Pie
          data={data}
          dataKey="value"
          nameKey="group"
          cx="50%"
          cy="50%"
          outerRadius={110}
          label
        >
          {data.map((_, i) => (
            <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
          ))}
        </Pie>
      </PieChart>
    ) : (
      CARTESIAN_RENDERERS[chartType](data)
    );

  return (
    <div style={{ width: "100%", height }}>
      <ResponsiveContainer>{chart}</ResponsiveContainer>
    </div>
  );
}
