import apiClient from "./client";

export interface AggregateRow {
  group: string | number | null;
  value: number;
}

export interface AggregateParams {
  model: string; // path fragment, e.g. "invoicing/invoices"
  group_by: string;
  measure?: string;
  op?: "sum" | "count" | "avg" | "min" | "max";
  filters?: Record<string, string>;
}

/**
 * Call /api/v1/{model}/aggregate/?group_by=&measure=&op=
 * where `model` is the path fragment of the target ViewSet.
 */
export async function fetchAggregateApi(
  params: AggregateParams,
): Promise<AggregateRow[]> {
  const url = `/v1/${params.model.replace(/^\/+|\/+$/g, "")}/aggregate/`;
  const query: Record<string, string> = {
    group_by: params.group_by,
  };
  if (params.measure) query.measure = params.measure;
  if (params.op) query.op = params.op;
  if (params.filters) {
    for (const [k, v] of Object.entries(params.filters)) {
      query[k] = v;
    }
  }
  const { data } = await apiClient.get<AggregateRow[]>(url, { params: query });
  return data;
}

export interface ReportTemplate {
  id: number;
  name: string;
  model_name: string;
  default_filters: Record<string, unknown>;
  default_group_by: string[];
  default_measures: string[];
  industry_tag: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export async function fetchReportTemplatesApi(): Promise<ReportTemplate[]> {
  const { data } = await apiClient.get<ReportTemplate[]>("/v1/reports/templates/");
  return data;
}

export interface PivotDefinition {
  id: number;
  name: string;
  model_name: string;
  rows: string[];
  cols: string[];
  measure: string;
  aggregator: string;
  created_at: string;
  updated_at: string;
}

export async function fetchPivotDefinitionsApi(): Promise<PivotDefinition[]> {
  const { data } = await apiClient.get<PivotDefinition[]>("/v1/reports/pivots/");
  return data;
}
