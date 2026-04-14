import apiClient from "./client";

export interface SalesQuotation {
  id: number;
  quotation_number: string;
  customer_name: string;
  customer_email: string;
  status: string;
  valid_until: string | null;
  notes: string;
  total_amount: string;
  created_at: string;
  updated_at: string;
}

export interface SalesOrder {
  id: number;
  order_number: string;
  customer_name: string;
  customer_email: string;
  quotation: number | null;
  status: string;
  order_date: string | null;
  delivery_date: string | null;
  notes: string;
  total_amount: string;
  created_at: string;
  updated_at: string;
}

export async function fetchQuotationsApi(
  params?: Record<string, string>,
): Promise<SalesQuotation[]> {
  const { data } = await apiClient.get<SalesQuotation[]>(
    "/v1/sales/quotations/",
    { params },
  );
  return data;
}

export async function fetchQuotationApi(id: number): Promise<SalesQuotation> {
  const { data } = await apiClient.get<SalesQuotation>(
    `/v1/sales/quotations/${id}/`,
  );
  return data;
}

export async function createQuotationApi(
  payload: Partial<SalesQuotation>,
): Promise<SalesQuotation> {
  const { data } = await apiClient.post<SalesQuotation>(
    "/v1/sales/quotations/",
    payload,
  );
  return data;
}

export async function updateQuotationApi(
  id: number,
  payload: Partial<SalesQuotation>,
): Promise<SalesQuotation> {
  const { data } = await apiClient.patch<SalesQuotation>(
    `/v1/sales/quotations/${id}/`,
    payload,
  );
  return data;
}

export async function fetchSalesOrdersApi(
  params?: Record<string, string>,
): Promise<SalesOrder[]> {
  const { data } = await apiClient.get<SalesOrder[]>("/v1/sales/orders/", {
    params,
  });
  return data;
}

export async function fetchSalesOrderApi(id: number): Promise<SalesOrder> {
  const { data } = await apiClient.get<SalesOrder>(`/v1/sales/orders/${id}/`);
  return data;
}

export async function createSalesOrderApi(
  payload: Partial<SalesOrder>,
): Promise<SalesOrder> {
  const { data } = await apiClient.post<SalesOrder>(
    "/v1/sales/orders/",
    payload,
  );
  return data;
}

export async function updateSalesOrderApi(
  id: number,
  payload: Partial<SalesOrder>,
): Promise<SalesOrder> {
  const { data } = await apiClient.patch<SalesOrder>(
    `/v1/sales/orders/${id}/`,
    payload,
  );
  return data;
}

export async function deleteSalesOrderApi(id: number): Promise<void> {
  await apiClient.delete(`/v1/sales/orders/${id}/`);
}
