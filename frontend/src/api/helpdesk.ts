import apiClient from "./client";

export interface TicketCategory {
  id: number;
  name: string;
  sla_hours: number;
  industry_tag: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface SLAConfig {
  id: number;
  category: number;
  category_name: string;
  priority: string;
  response_hours: number;
  resolution_hours: number;
  created_at: string;
  updated_at: string;
}

export interface Ticket {
  id: number;
  ticket_number: string;
  title: string;
  description: string;
  category: number | null;
  category_name: string | null;
  reporter_partner: number | null;
  reporter_partner_name: string | null;
  reporter_user: number | null;
  assignee: number | null;
  assignee_username: string | null;
  priority: string;
  status: string;
  resolved_at: string | null;
  sla_breached: boolean;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeArticle {
  id: number;
  title: string;
  slug: string;
  body: string;
  category: number | null;
  category_name: string | null;
  published: boolean;
  tags: string[];
  created_at: string;
  updated_at: string;
}

// ── Categories ─────────────────────────────────────────────────────
export async function fetchCategoriesApi(
  params?: Record<string, string>,
): Promise<TicketCategory[]> {
  const { data } = await apiClient.get<TicketCategory[]>("/v1/helpdesk/categories/", {
    params,
  });
  return data;
}

export async function createCategoryApi(
  payload: Partial<TicketCategory>,
): Promise<TicketCategory> {
  const { data } = await apiClient.post<TicketCategory>(
    "/v1/helpdesk/categories/",
    payload,
  );
  return data;
}

// ── Tickets ────────────────────────────────────────────────────────
export async function fetchTicketsApi(
  params?: Record<string, string>,
): Promise<Ticket[]> {
  const { data } = await apiClient.get<Ticket[]>("/v1/helpdesk/tickets/", {
    params,
  });
  return data;
}

export async function fetchTicketApi(id: number): Promise<Ticket> {
  const { data } = await apiClient.get<Ticket>(`/v1/helpdesk/tickets/${id}/`);
  return data;
}

export async function createTicketApi(payload: Partial<Ticket>): Promise<Ticket> {
  const { data } = await apiClient.post<Ticket>("/v1/helpdesk/tickets/", payload);
  return data;
}

export async function updateTicketApi(
  id: number,
  payload: Partial<Ticket>,
): Promise<Ticket> {
  const { data } = await apiClient.patch<Ticket>(
    `/v1/helpdesk/tickets/${id}/`,
    payload,
  );
  return data;
}

export async function resolveTicketApi(id: number): Promise<Ticket> {
  const { data } = await apiClient.post<Ticket>(`/v1/helpdesk/tickets/${id}/resolve/`);
  return data;
}

export async function reopenTicketApi(id: number): Promise<Ticket> {
  const { data } = await apiClient.post<Ticket>(`/v1/helpdesk/tickets/${id}/reopen/`);
  return data;
}

// ── Articles ───────────────────────────────────────────────────────
export async function fetchArticlesApi(
  params?: Record<string, string>,
): Promise<KnowledgeArticle[]> {
  const { data } = await apiClient.get<KnowledgeArticle[]>("/v1/helpdesk/articles/", {
    params,
  });
  return data;
}

export async function fetchArticleApi(id: number): Promise<KnowledgeArticle> {
  const { data } = await apiClient.get<KnowledgeArticle>(
    `/v1/helpdesk/articles/${id}/`,
  );
  return data;
}

export async function createArticleApi(
  payload: Partial<KnowledgeArticle>,
): Promise<KnowledgeArticle> {
  const { data } = await apiClient.post<KnowledgeArticle>(
    "/v1/helpdesk/articles/",
    payload,
  );
  return data;
}

export async function updateArticleApi(
  id: number,
  payload: Partial<KnowledgeArticle>,
): Promise<KnowledgeArticle> {
  const { data } = await apiClient.patch<KnowledgeArticle>(
    `/v1/helpdesk/articles/${id}/`,
    payload,
  );
  return data;
}
