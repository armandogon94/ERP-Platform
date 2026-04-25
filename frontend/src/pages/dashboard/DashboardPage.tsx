import { useEffect, useState } from "react";
import {
  type ChartRow,
  type Dashboard,
  type KpiData,
  type TableRow,
  type WidgetData,
  fetchDashboardDataApi,
  fetchDefaultDashboardApi,
} from "../../api/dashboards";
import ChartWidget from "../../components/widgets/ChartWidget";
import KpiWidget from "../../components/widgets/KpiWidget";
import TableWidget from "../../components/widgets/TableWidget";
import Skeleton from "../../components/Skeleton";

/**
 * Per-industry dashboard.
 *
 * On mount: GET /dashboards/default/ to pick up the company's default
 * dashboard (lazily seeded from its industry YAML preset on first access),
 * then GET /<id>/data/ to fetch all widget payloads in one request.
 */
export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [widgetData, setWidgetData] = useState<Record<number, WidgetData> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const d = await fetchDefaultDashboardApi();
        if (cancelled) return;
        setDashboard(d);
        const data = await fetchDashboardDataApi(d.id);
        if (!cancelled) setWidgetData(data);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load dashboard");
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return (
      <div className="dashboard-page">
        <h1>Dashboard</h1>
        <div role="alert">Error: {error}</div>
      </div>
    );
  }

  if (!dashboard || !widgetData) {
    return (
      <div className="dashboard-page">
        <h1>Dashboard</h1>
        <Skeleton lines={6} />
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <h1>{dashboard.name}</h1>

      <div className="dashboard-grid">
        {dashboard.widgets
          .slice()
          .sort((a, b) => a.position - b.position)
          .map((widget) => {
            const data = widgetData[widget.id];
            // Error envelope from backend: show a minimal fallback tile.
            if (data && typeof data === "object" && "error" in data) {
              return (
                <div key={widget.id} className="widget widget-error">
                  <div className="widget-title">{widget.title}</div>
                  <div role="alert">{data.error}</div>
                </div>
              );
            }

            if (widget.widget_type === "kpi") {
              return (
                <KpiWidget
                  key={widget.id}
                  title={widget.title}
                  subtitle={widget.subtitle}
                  data={data as KpiData}
                />
              );
            }
            if (widget.widget_type === "table") {
              return (
                <TableWidget
                  key={widget.id}
                  title={widget.title}
                  subtitle={widget.subtitle}
                  data={data as TableRow[]}
                />
              );
            }
            return (
              <ChartWidget
                key={widget.id}
                title={widget.title}
                subtitle={widget.subtitle}
                widgetType={widget.widget_type}
                data={data as ChartRow[]}
              />
            );
          })}
      </div>
    </div>
  );
}
