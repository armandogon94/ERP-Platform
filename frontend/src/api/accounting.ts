import apiClient from "./client";

export interface Account {
  id: number;
  code: string;
  name: string;
  account_type: string;
  parent: number | null;
  parent_name: string | null;
  description: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Journal {
  id: number;
  name: string;
  code: string;
  journal_type: string;
  default_account: number | null;
  created_at: string;
  updated_at: string;
}

export interface JournalEntry {
  id: number;
  journal: number;
  journal_name: string;
  reference: string;
  entry_date: string | null;
  status: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export async function fetchAccountsApi(
  params?: Record<string, string>,
): Promise<Account[]> {
  const { data } = await apiClient.get<Account[]>("/v1/accounting/accounts/", {
    params,
  });
  return data;
}

export async function fetchAccountApi(id: number): Promise<Account> {
  const { data } = await apiClient.get<Account>(
    `/v1/accounting/accounts/${id}/`,
  );
  return data;
}

export async function createAccountApi(
  payload: Partial<Account>,
): Promise<Account> {
  const { data } = await apiClient.post<Account>(
    "/v1/accounting/accounts/",
    payload,
  );
  return data;
}

export async function updateAccountApi(
  id: number,
  payload: Partial<Account>,
): Promise<Account> {
  const { data } = await apiClient.patch<Account>(
    `/v1/accounting/accounts/${id}/`,
    payload,
  );
  return data;
}

export async function fetchJournalsApi(
  params?: Record<string, string>,
): Promise<Journal[]> {
  const { data } = await apiClient.get<Journal[]>("/v1/accounting/journals/", {
    params,
  });
  return data;
}

export async function fetchJournalEntriesApi(
  params?: Record<string, string>,
): Promise<JournalEntry[]> {
  const { data } = await apiClient.get<JournalEntry[]>(
    "/v1/accounting/entries/",
    { params },
  );
  return data;
}

export async function fetchJournalEntryApi(id: number): Promise<JournalEntry> {
  const { data } = await apiClient.get<JournalEntry>(
    `/v1/accounting/entries/${id}/`,
  );
  return data;
}

export async function createJournalEntryApi(
  payload: Partial<JournalEntry>,
): Promise<JournalEntry> {
  const { data } = await apiClient.post<JournalEntry>(
    "/v1/accounting/entries/",
    payload,
  );
  return data;
}

export async function updateJournalEntryApi(
  id: number,
  payload: Partial<JournalEntry>,
): Promise<JournalEntry> {
  const { data } = await apiClient.patch<JournalEntry>(
    `/v1/accounting/entries/${id}/`,
    payload,
  );
  return data;
}

export async function deleteJournalEntryApi(id: number): Promise<void> {
  await apiClient.delete(`/v1/accounting/entries/${id}/`);
}
