import apiClient from "./client";

export interface POSSession {
  id: number;
  station: string;
  cash_on_open: string;
  cash_on_close: string | null;
  expected_cash: string | null;
  variance: string | null;
  opened_by: number;
  opened_by_username: string;
  opened_at: string;
  closed_at: string | null;
  status: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface POSOrder {
  id: number;
  session: number;
  order_number: string;
  customer: number | null;
  customer_name: string | null;
  subtotal: string;
  tax_amount: string;
  total: string;
  status: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface POSOrderLine {
  id: number;
  order: number;
  product: number;
  product_name: string;
  quantity: string;
  unit_price: string;
  tax_rate: string;
  total: string;
  created_at: string;
  updated_at: string;
}

export interface CashMovement {
  id: number;
  session: number;
  type: string;
  amount: string;
  reason: string;
  at_time: string;
  created_at: string;
  updated_at: string;
}

// ── Sessions ────────────────────────────────────────────────────────
export async function fetchPOSSessionsApi(
  params?: Record<string, string>,
): Promise<POSSession[]> {
  const { data } = await apiClient.get<POSSession[]>("/v1/pos/sessions/", {
    params,
  });
  return data;
}

export async function fetchPOSSessionApi(id: number): Promise<POSSession> {
  const { data } = await apiClient.get<POSSession>(`/v1/pos/sessions/${id}/`);
  return data;
}

export async function createPOSSessionApi(
  payload: Partial<POSSession>,
): Promise<POSSession> {
  const { data } = await apiClient.post<POSSession>(
    "/v1/pos/sessions/",
    payload,
  );
  return data;
}

export async function updatePOSSessionApi(
  id: number,
  payload: Partial<POSSession>,
): Promise<POSSession> {
  const { data } = await apiClient.patch<POSSession>(
    `/v1/pos/sessions/${id}/`,
    payload,
  );
  return data;
}

export async function closePOSSessionApi(
  id: number,
  payload: { cash_on_close: string },
): Promise<POSSession> {
  const { data } = await apiClient.post<POSSession>(
    `/v1/pos/sessions/${id}/close/`,
    payload,
  );
  return data;
}

// ── Orders ──────────────────────────────────────────────────────────
export async function fetchPOSOrdersApi(
  params?: Record<string, string>,
): Promise<POSOrder[]> {
  const { data } = await apiClient.get<POSOrder[]>("/v1/pos/orders/", {
    params,
  });
  return data;
}

export async function fetchPOSOrderApi(id: number): Promise<POSOrder> {
  const { data } = await apiClient.get<POSOrder>(`/v1/pos/orders/${id}/`);
  return data;
}

export async function createPOSOrderApi(
  payload: Partial<POSOrder>,
): Promise<POSOrder> {
  const { data } = await apiClient.post<POSOrder>("/v1/pos/orders/", payload);
  return data;
}

export async function updatePOSOrderApi(
  id: number,
  payload: Partial<POSOrder>,
): Promise<POSOrder> {
  const { data } = await apiClient.patch<POSOrder>(
    `/v1/pos/orders/${id}/`,
    payload,
  );
  return data;
}

// ── Order lines ─────────────────────────────────────────────────────
export async function fetchPOSOrderLinesApi(
  params?: Record<string, string>,
): Promise<POSOrderLine[]> {
  const { data } = await apiClient.get<POSOrderLine[]>(
    "/v1/pos/order-lines/",
    { params },
  );
  return data;
}

// ── Cash movements ──────────────────────────────────────────────────
export async function fetchCashMovementsApi(
  params?: Record<string, string>,
): Promise<CashMovement[]> {
  const { data } = await apiClient.get<CashMovement[]>(
    "/v1/pos/cash-movements/",
    { params },
  );
  return data;
}
