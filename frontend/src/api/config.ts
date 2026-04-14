import apiClient from "./client";

export interface ModuleConfigResponse {
  module: string;
  industry: string;
  config: Record<string, unknown>;
  terminology: Record<string, string>;
}

export interface ModuleInfo {
  id: number;
  name: string;
  display_name: string;
  icon: string;
  is_installed: boolean;
  is_visible: boolean;
  sequence: number;
  color: string;
}

export async function fetchModuleConfigApi(
  moduleId: number,
): Promise<ModuleConfigResponse> {
  const { data } = await apiClient.get<ModuleConfigResponse>(
    `/v1/core/modules/${moduleId}/config/`,
  );
  return data;
}

export async function patchModuleConfigApi(
  moduleId: number,
  overrides: Record<string, unknown>,
): Promise<ModuleConfigResponse> {
  const { data } = await apiClient.patch<ModuleConfigResponse>(
    `/v1/core/modules/${moduleId}/config/`,
    { overrides },
  );
  return data;
}

export async function fetchModulesApi(): Promise<ModuleInfo[]> {
  const { data } = await apiClient.get<ModuleInfo[]>("/v1/core/modules/");
  return data;
}
