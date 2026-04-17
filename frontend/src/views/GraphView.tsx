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

const COLORS = [
  "var(--accent, #714B67)",
  "#2563EB",
  "#059669",
  "#D97706",
  "#7C3AED",
  "#06B6D4",
  "#9F1239",
  "#EA580C",
  "#6D28D9",
  "#166534",
];

export default function GraphView({ rows, chartType, height = 320 }: GraphViewProps) {
  if (rows.length === 0) {
    return <div>No data</div>;
  }

  const data = rows.map((r) => ({
    group: r.group === null ? "—" : String(r.group),
    value: r.value,
  }));

  return (
    <div style={{ width: "100%", height }}>
      <ResponsiveContainer>
        {chartType === "bar" ? (
          <BarChart data={data}>
            <CartesianGrid stroke="#eee" strokeDasharray="3 3" />
            <XAxis dataKey="group" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" fill="var(--accent, #714B67)" />
          </BarChart>
        ) : chartType === "line" ? (
          <LineChart data={data}>
            <CartesianGrid stroke="#eee" strokeDasharray="3 3" />
            <XAxis dataKey="group" />
            <YAxis />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="value"
              stroke="var(--accent, #714B67)"
              strokeWidth={2}
            />
          </LineChart>
        ) : chartType === "area" ? (
          <AreaChart data={data}>
            <CartesianGrid stroke="#eee" strokeDasharray="3 3" />
            <XAxis dataKey="group" />
            <YAxis />
            <Tooltip />
            <Area
              type="monotone"
              dataKey="value"
              stroke="var(--accent, #714B67)"
              fill="var(--accent-soft, #efe8ec)"
            />
          </AreaChart>
        ) : (
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
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
          </PieChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}
