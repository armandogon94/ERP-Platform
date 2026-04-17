import apiClient from "./client";

export interface BillOfMaterials {
  id: number;
  product: number;
  product_name: string;
  version: string;
  active: boolean;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface BOMLine {
  id: number;
  bom: number;
  component: number;
  component_name: string;
  quantity: string;
  uom: string;
  created_at: string;
  updated_at: string;
}

export interface WorkOrder {
  id: number;
  product: number;
  product_name: string;
  bom: number | null;
  quantity_target: string;
  quantity_done: string;
  status: string;
  start_date: string | null;
  end_date: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface ProductionCost {
  id: number;
  work_order: number;
  cost_type: string;
  amount: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

// ── BOMs ────────────────────────────────────────────────────────────
export async function fetchBOMsApi(
  params?: Record<string, string>,
): Promise<BillOfMaterials[]> {
  const { data } = await apiClient.get<BillOfMaterials[]>(
    "/v1/manufacturing/boms/",
    { params },
  );
  return data;
}

export async function fetchBOMApi(id: number): Promise<BillOfMaterials> {
  const { data } = await apiClient.get<BillOfMaterials>(
    `/v1/manufacturing/boms/${id}/`,
  );
  return data;
}

export async function createBOMApi(
  payload: Partial<BillOfMaterials>,
): Promise<BillOfMaterials> {
  const { data } = await apiClient.post<BillOfMaterials>(
    "/v1/manufacturing/boms/",
    payload,
  );
  return data;
}

export async function updateBOMApi(
  id: number,
  payload: Partial<BillOfMaterials>,
): Promise<BillOfMaterials> {
  const { data } = await apiClient.patch<BillOfMaterials>(
    `/v1/manufacturing/boms/${id}/`,
    payload,
  );
  return data;
}

// ── BOM lines ───────────────────────────────────────────────────────
export async function fetchBOMLinesApi(
  params?: Record<string, string>,
): Promise<BOMLine[]> {
  const { data } = await apiClient.get<BOMLine[]>(
    "/v1/manufacturing/bom-lines/",
    { params },
  );
  return data;
}

export async function createBOMLineApi(
  payload: Partial<BOMLine>,
): Promise<BOMLine> {
  const { data } = await apiClient.post<BOMLine>(
    "/v1/manufacturing/bom-lines/",
    payload,
  );
  return data;
}

export async function deleteBOMLineApi(id: number): Promise<void> {
  await apiClient.delete(`/v1/manufacturing/bom-lines/${id}/`);
}

// ── Work orders ─────────────────────────────────────────────────────
export async function fetchWorkOrdersApi(
  params?: Record<string, string>,
): Promise<WorkOrder[]> {
  const { data } = await apiClient.get<WorkOrder[]>(
    "/v1/manufacturing/work-orders/",
    { params },
  );
  return data;
}

export async function fetchWorkOrderApi(id: number): Promise<WorkOrder> {
  const { data } = await apiClient.get<WorkOrder>(
    `/v1/manufacturing/work-orders/${id}/`,
  );
  return data;
}

export async function createWorkOrderApi(
  payload: Partial<WorkOrder>,
): Promise<WorkOrder> {
  const { data } = await apiClient.post<WorkOrder>(
    "/v1/manufacturing/work-orders/",
    payload,
  );
  return data;
}

export async function updateWorkOrderApi(
  id: number,
  payload: Partial<WorkOrder>,
): Promise<WorkOrder> {
  const { data } = await apiClient.patch<WorkOrder>(
    `/v1/manufacturing/work-orders/${id}/`,
    payload,
  );
  return data;
}

export async function startWorkOrderApi(id: number): Promise<WorkOrder> {
  const { data } = await apiClient.post<WorkOrder>(
    `/v1/manufacturing/work-orders/${id}/start/`,
  );
  return data;
}

export async function completeWorkOrderApi(id: number): Promise<WorkOrder> {
  const { data } = await apiClient.post<WorkOrder>(
    `/v1/manufacturing/work-orders/${id}/complete/`,
  );
  return data;
}
