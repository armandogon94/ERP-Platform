import apiClient from "./client";

export interface Vendor {
  id: number;
  name: string;
  email: string;
  contact_name: string;
  phone: string;
  address: string;
  currency: string;
  payment_terms: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PurchaseOrder {
  id: number;
  vendor: number;
  vendor_name: string;
  po_number: string;
  status: string;
  order_date: string | null;
  expected_date: string | null;
  notes: string;
  total_amount: string;
  created_at: string;
  updated_at: string;
}

export interface RequestForQuote {
  id: number;
  vendor: number;
  vendor_name: string;
  rfq_number: string;
  status: string;
  request_date: string | null;
  deadline: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

export async function fetchVendorsApi(
  params?: Record<string, string>,
): Promise<Vendor[]> {
  const { data } = await apiClient.get<Vendor[]>("/v1/purchasing/vendors/", { params });
  return data;
}

export async function fetchVendorApi(id: number): Promise<Vendor> {
  const { data } = await apiClient.get<Vendor>(`/v1/purchasing/vendors/${id}/`);
  return data;
}

export async function createVendorApi(payload: Partial<Vendor>): Promise<Vendor> {
  const { data } = await apiClient.post<Vendor>("/v1/purchasing/vendors/", payload);
  return data;
}

export async function updateVendorApi(
  id: number,
  payload: Partial<Vendor>,
): Promise<Vendor> {
  const { data } = await apiClient.patch<Vendor>(
    `/v1/purchasing/vendors/${id}/`,
    payload,
  );
  return data;
}

export async function deleteVendorApi(id: number): Promise<void> {
  await apiClient.delete(`/v1/purchasing/vendors/${id}/`);
}

export async function fetchPurchaseOrdersApi(
  params?: Record<string, string>,
): Promise<PurchaseOrder[]> {
  const { data } = await apiClient.get<PurchaseOrder[]>(
    "/v1/purchasing/purchase-orders/",
    { params },
  );
  return data;
}

export async function fetchPurchaseOrderApi(id: number): Promise<PurchaseOrder> {
  const { data } = await apiClient.get<PurchaseOrder>(
    `/v1/purchasing/purchase-orders/${id}/`,
  );
  return data;
}

export async function createPurchaseOrderApi(
  payload: Partial<PurchaseOrder>,
): Promise<PurchaseOrder> {
  const { data } = await apiClient.post<PurchaseOrder>(
    "/v1/purchasing/purchase-orders/",
    payload,
  );
  return data;
}

export async function updatePurchaseOrderApi(
  id: number,
  payload: Partial<PurchaseOrder>,
): Promise<PurchaseOrder> {
  const { data } = await apiClient.patch<PurchaseOrder>(
    `/v1/purchasing/purchase-orders/${id}/`,
    payload,
  );
  return data;
}

export async function deletePurchaseOrderApi(id: number): Promise<void> {
  await apiClient.delete(`/v1/purchasing/purchase-orders/${id}/`);
}

export async function fetchRFQsApi(
  params?: Record<string, string>,
): Promise<RequestForQuote[]> {
  const { data } = await apiClient.get<RequestForQuote[]>(
    "/v1/purchasing/rfqs/",
    { params },
  );
  return data;
}
