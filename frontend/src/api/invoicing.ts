import apiClient from "./client";

export interface Invoice {
  id: number;
  invoice_number: string;
  invoice_type: string;
  status: string;
  customer: number | null;
  customer_name: string;
  customer_email: string;
  invoice_date: string | null;
  due_date: string | null;
  notes: string;
  subtotal: string;
  tax_amount: string;
  total_amount: string;
  amount_paid: string;
  created_at: string;
  updated_at: string;
}

export interface InvoiceLine {
  id: number;
  invoice: number;
  description: string;
  quantity: string;
  unit_price: string;
  tax_rate: string;
  total_price: string;
  created_at: string;
  updated_at: string;
}

export interface CreditNote {
  id: number;
  credit_note_number: string;
  invoice: number;
  invoice_number: string;
  reason: string;
  amount: string;
  issue_date: string | null;
  created_at: string;
  updated_at: string;
}

export async function fetchInvoicesApi(
  params?: Record<string, string>,
): Promise<Invoice[]> {
  const { data } = await apiClient.get<Invoice[]>("/v1/invoicing/invoices/", {
    params,
  });
  return data;
}

export async function fetchInvoiceApi(id: number): Promise<Invoice> {
  const { data } = await apiClient.get<Invoice>(`/v1/invoicing/invoices/${id}/`);
  return data;
}

export async function createInvoiceApi(payload: Partial<Invoice>): Promise<Invoice> {
  const { data } = await apiClient.post<Invoice>("/v1/invoicing/invoices/", payload);
  return data;
}

export async function updateInvoiceApi(
  id: number,
  payload: Partial<Invoice>,
): Promise<Invoice> {
  const { data } = await apiClient.patch<Invoice>(
    `/v1/invoicing/invoices/${id}/`,
    payload,
  );
  return data;
}

export async function deleteInvoiceApi(id: number): Promise<void> {
  await apiClient.delete(`/v1/invoicing/invoices/${id}/`);
}

export async function fetchCreditNotesApi(
  params?: Record<string, string>,
): Promise<CreditNote[]> {
  const { data } = await apiClient.get<CreditNote[]>("/v1/invoicing/credit-notes/", {
    params,
  });
  return data;
}
