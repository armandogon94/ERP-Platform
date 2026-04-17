import apiClient from "./client";

export interface HomeKPITile {
  label: string;
  value: string;
  detail?: string;
  module?: string;
}

export interface HomeKPIs {
  tiles: HomeKPITile[];
}

export async function fetchHomeKPIsApi(): Promise<HomeKPIs> {
  const { data } = await apiClient.get<HomeKPIs>("/v1/core/home-kpis/");
  return data;
}
