import apiClient from "./client";

export type WidgetType = "kpi" | "bar" | "line" | "pie" | "area" | "table";

export interface DashboardWidget {
  id: number;
  dashboard: number;
  position: number;
  widget_type: WidgetType;
  title: string;
  subtitle: string;
  data_source: string;
  config_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Dashboard {
  id: number;
  name: string;
  slug: string;
  is_default: boolean;
  industry_preset: string;
  layout_json: Record<string, unknown>;
  widgets: DashboardWidget[];
  created_at: string;
  updated_at: string;
}

/** KPI widget shape — single number + optional detail. */
export interface KpiData {
  value: string;
  detail?: string;
}

/** Chart widgets (bar/line/pie/area) — a list of (group, value) rows. */
export interface ChartRow {
  group: string;
  value: number;
}

/** Table widget — list of arbitrary row dicts. */
export type TableRow = Record<string, string | number | null>;

/** Either shape OR an error envelope from the backend. */
export type WidgetData =
  | KpiData
  | ChartRow[]
  | TableRow[]
  | { error: string };

export async function fetchDefaultDashboardApi(): Promise<Dashboard> {
  const { data } = await apiClient.get<Dashboard>(
    "/v1/dashboards/dashboards/default/",
  );
  return data;
}

export async function fetchDashboardDataApi(
  dashboardId: number,
): Promise<Record<number, WidgetData>> {
  const { data } = await apiClient.get<Record<number, WidgetData>>(
    `/v1/dashboards/dashboards/${dashboardId}/data/`,
  );
  return data;
}

export async function reseedDashboardApi(
  dashboardId: number,
): Promise<Dashboard> {
  const { data } = await apiClient.post<Dashboard>(
    `/v1/dashboards/dashboards/${dashboardId}/reseed/`,
  );
  return data;
}
