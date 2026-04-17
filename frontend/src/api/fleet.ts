import apiClient from "./client";

export interface Driver {
  id: number;
  name: string;
  license_number: string;
  license_expiry: string | null;
  phone: string;
  status: string;
  employee: number | null;
  created_at: string;
  updated_at: string;
}

export interface Vehicle {
  id: number;
  make: string;
  model: string;
  year: number;
  license_plate: string;
  vin: string;
  status: string;
  driver: number | null;
  driver_name: string | null;
  mileage: number;
  created_at: string;
  updated_at: string;
}

export interface MaintenanceLog {
  id: number;
  vehicle: number;
  vehicle_plate: string;
  date: string | null;
  description: string;
  cost: string;
  mechanic: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface FuelLog {
  id: number;
  vehicle: number;
  vehicle_plate: string;
  date: string | null;
  liters: string;
  cost_per_liter: string;
  total_cost: string;
  mileage_at_fill: number;
  created_at: string;
  updated_at: string;
}

export interface VehicleService {
  id: number;
  vehicle: number;
  vehicle_plate: string;
  service_type: string;
  scheduled_date: string | null;
  completed_date: string | null;
  cost: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

// ── Drivers ─────────────────────────────────────────────────────────
export async function fetchDriversApi(
  params?: Record<string, string>,
): Promise<Driver[]> {
  const { data } = await apiClient.get<Driver[]>("/v1/fleet/drivers/", { params });
  return data;
}

export async function fetchDriverApi(id: number): Promise<Driver> {
  const { data } = await apiClient.get<Driver>(`/v1/fleet/drivers/${id}/`);
  return data;
}

export async function createDriverApi(payload: Partial<Driver>): Promise<Driver> {
  const { data } = await apiClient.post<Driver>("/v1/fleet/drivers/", payload);
  return data;
}

export async function updateDriverApi(
  id: number,
  payload: Partial<Driver>,
): Promise<Driver> {
  const { data } = await apiClient.patch<Driver>(`/v1/fleet/drivers/${id}/`, payload);
  return data;
}

// ── Vehicles ────────────────────────────────────────────────────────
export async function fetchVehiclesApi(
  params?: Record<string, string>,
): Promise<Vehicle[]> {
  const { data } = await apiClient.get<Vehicle[]>("/v1/fleet/vehicles/", { params });
  return data;
}

export async function fetchVehicleApi(id: number): Promise<Vehicle> {
  const { data } = await apiClient.get<Vehicle>(`/v1/fleet/vehicles/${id}/`);
  return data;
}

export async function createVehicleApi(
  payload: Partial<Vehicle>,
): Promise<Vehicle> {
  const { data } = await apiClient.post<Vehicle>("/v1/fleet/vehicles/", payload);
  return data;
}

export async function updateVehicleApi(
  id: number,
  payload: Partial<Vehicle>,
): Promise<Vehicle> {
  const { data } = await apiClient.patch<Vehicle>(
    `/v1/fleet/vehicles/${id}/`,
    payload,
  );
  return data;
}

// ── Maintenance / fuel ─────────────────────────────────────────────
export async function fetchMaintenanceLogsApi(
  params?: Record<string, string>,
): Promise<MaintenanceLog[]> {
  const { data } = await apiClient.get<MaintenanceLog[]>(
    "/v1/fleet/maintenance-logs/",
    { params },
  );
  return data;
}

export async function fetchFuelLogsApi(
  params?: Record<string, string>,
): Promise<FuelLog[]> {
  const { data } = await apiClient.get<FuelLog[]>("/v1/fleet/fuel-logs/", {
    params,
  });
  return data;
}

export async function fetchVehicleServicesApi(
  params?: Record<string, string>,
): Promise<VehicleService[]> {
  const { data } = await apiClient.get<VehicleService[]>("/v1/fleet/services/", {
    params,
  });
  return data;
}
