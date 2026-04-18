import apiClient from "./client";

export interface AuditLogEntry {
  id: number;
  model_name: string;
  model_id: number;
  action: "create" | "update" | "delete";
  user_name: string;
  old_values: Record<string, unknown>;
  new_values: Record<string, unknown>;
  timestamp: string;
}

export async function fetchAuditLogApi(): Promise<AuditLogEntry[]> {
  const { data } = await apiClient.get<AuditLogEntry[]>("/v1/core/audit-logs/");
  return data;
}
