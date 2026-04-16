import apiClient from "./client";

export interface Partner {
  id: number;
  name: string;
  email: string;
  phone: string;
  is_customer: boolean;
  is_vendor: boolean;
  tax_id: string;
  payment_terms_days: number;
  credit_limit: string;
  industry_tags: string[];
  address_json: Record<string, unknown>;
  notes: string;
  created_at: string;
  updated_at: string;
}

export async function fetchPartnersApi(
  params?: Record<string, string>,
): Promise<Partner[]> {
  const { data } = await apiClient.get<Partner[]>("/v1/core/partners/", {
    params,
  });
  return data;
}

export async function fetchPartnerApi(id: number): Promise<Partner> {
  const { data } = await apiClient.get<Partner>(`/v1/core/partners/${id}/`);
  return data;
}

export async function createPartnerApi(
  payload: Partial<Partner>,
): Promise<Partner> {
  const { data } = await apiClient.post<Partner>("/v1/core/partners/", payload);
  return data;
}

export async function updatePartnerApi(
  id: number,
  payload: Partial<Partner>,
): Promise<Partner> {
  const { data } = await apiClient.patch<Partner>(
    `/v1/core/partners/${id}/`,
    payload,
  );
  return data;
}

export async function deletePartnerApi(id: number): Promise<void> {
  await apiClient.delete(`/v1/core/partners/${id}/`);
}
