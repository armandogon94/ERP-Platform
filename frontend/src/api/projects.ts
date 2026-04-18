import apiClient from "./client";

export interface Project {
  id: number;
  name: string;
  code: string;
  customer: number | null;
  customer_name: string | null;
  start_date: string | null;
  end_date: string | null;
  status: string;
  budget: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: number;
  project: number;
  project_name: string;
  name: string;
  description: string;
  assignee: number | null;
  assignee_name: string | null;
  status: string;
  priority: string;
  due_date: string | null;
  parent_task: number | null;
  created_at: string;
  updated_at: string;
}

export interface Milestone {
  id: number;
  project: number;
  project_name: string;
  name: string;
  due_date: string | null;
  completed: boolean;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectTimesheet {
  id: number;
  project: number;
  project_name: string;
  task: number | null;
  employee: number;
  employee_name: string | null;
  date: string;
  hours: string;
  billable: boolean;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectProgress {
  total_tasks: number;
  done: number;
  hours_logged: string;
  budget_consumed_pct: number;
}

// ── Projects ────────────────────────────────────────────────────────
export async function fetchProjectsApi(
  params?: Record<string, string>,
): Promise<Project[]> {
  const { data } = await apiClient.get<Project[]>("/v1/projects/projects/", {
    params,
  });
  return data;
}

export async function fetchProjectApi(id: number): Promise<Project> {
  const { data } = await apiClient.get<Project>(`/v1/projects/projects/${id}/`);
  return data;
}

export async function createProjectApi(payload: Partial<Project>): Promise<Project> {
  const { data } = await apiClient.post<Project>("/v1/projects/projects/", payload);
  return data;
}

export async function updateProjectApi(
  id: number,
  payload: Partial<Project>,
): Promise<Project> {
  const { data } = await apiClient.patch<Project>(
    `/v1/projects/projects/${id}/`,
    payload,
  );
  return data;
}

export async function fetchProjectProgressApi(id: number): Promise<ProjectProgress> {
  const { data } = await apiClient.get<ProjectProgress>(
    `/v1/projects/projects/${id}/progress/`,
  );
  return data;
}

// ── Tasks ───────────────────────────────────────────────────────────
export async function fetchTasksApi(params?: Record<string, string>): Promise<Task[]> {
  const { data } = await apiClient.get<Task[]>("/v1/projects/tasks/", { params });
  return data;
}

export async function fetchTaskApi(id: number): Promise<Task> {
  const { data } = await apiClient.get<Task>(`/v1/projects/tasks/${id}/`);
  return data;
}

export async function createTaskApi(payload: Partial<Task>): Promise<Task> {
  const { data } = await apiClient.post<Task>("/v1/projects/tasks/", payload);
  return data;
}

export async function updateTaskApi(id: number, payload: Partial<Task>): Promise<Task> {
  const { data } = await apiClient.patch<Task>(`/v1/projects/tasks/${id}/`, payload);
  return data;
}

// ── Milestones ──────────────────────────────────────────────────────
export async function fetchMilestonesApi(
  params?: Record<string, string>,
): Promise<Milestone[]> {
  const { data } = await apiClient.get<Milestone[]>("/v1/projects/milestones/", {
    params,
  });
  return data;
}

// ── Timesheets ──────────────────────────────────────────────────────
export async function fetchProjectTimesheetsApi(
  params?: Record<string, string>,
): Promise<ProjectTimesheet[]> {
  const { data } = await apiClient.get<ProjectTimesheet[]>("/v1/projects/timesheets/", {
    params,
  });
  return data;
}
