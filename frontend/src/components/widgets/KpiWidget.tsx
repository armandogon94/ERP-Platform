import type { KpiData } from "../../api/dashboards";

interface KpiWidgetProps {
  title: string;
  subtitle?: string;
  data: KpiData | undefined;
}

/** Single-number widget for top-of-dashboard KPI tiles. */
export default function KpiWidget({ title, subtitle, data }: KpiWidgetProps) {
  return (
    <div className="widget widget-kpi">
      <div className="widget-title">{title}</div>
      {subtitle && <div className="widget-subtitle">{subtitle}</div>}
      <div className="widget-kpi-value">{data?.value ?? "—"}</div>
      {data?.detail && <div className="widget-kpi-detail">{data.detail}</div>}
    </div>
  );
}
