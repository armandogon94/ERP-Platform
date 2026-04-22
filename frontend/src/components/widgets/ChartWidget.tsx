import { lazy, Suspense } from "react";
import type { ChartRow, WidgetType } from "../../api/dashboards";

// Reuse the GraphView that already handles bar/line/pie/area rendering.
// Lazy-load so Recharts only enters the bundle when a dashboard actually
// renders a chart widget.
const GraphView = lazy(() => import("../../views/GraphView"));

interface ChartWidgetProps {
  title: string;
  subtitle?: string;
  widgetType: Exclude<WidgetType, "kpi" | "table">;
  data: ChartRow[] | undefined;
}

/**
 * Bar / line / pie / area widget. Delegates to GraphView for the chart
 * itself; owns only the title + container chrome.
 */
export default function ChartWidget({
  title,
  subtitle,
  widgetType,
  data,
}: ChartWidgetProps) {
  const rows: ChartRow[] = Array.isArray(data) ? data : [];

  return (
    <div className="widget widget-chart">
      <div className="widget-title">{title}</div>
      {subtitle && <div className="widget-subtitle">{subtitle}</div>}
      <Suspense fallback={<div role="status">Loading chart…</div>}>
        {rows.length === 0 ? (
          <div className="widget-empty">No data</div>
        ) : (
          <GraphView
            rows={rows.map((r) => ({ group: r.group, value: r.value }))}
            chartType={widgetType}
            height={240}
          />
        )}
      </Suspense>
    </div>
  );
}
