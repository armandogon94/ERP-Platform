import apiClient from "./client";

export interface Employee {
  id: number;
  employee_number: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  department: number | null;
  department_name: string | null;
  job_title: string;
  hire_date: string;
  status: string;
  employee_type: string;
  created_at: string;
  updated_at: string;
}

export interface Department {
  id: number;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface LeaveRequest {
  id: number;
  employee: number;
  employee_name: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  days_requested: number;
  status: string;
  reason: string;
  created_at: string;
  updated_at: string;
}

export interface Payroll {
  id: number;
  employee: number;
  employee_name: string;
  period_start: string;
  period_end: string;
  gross_amount: string;
  net_amount: string;
  status: string;
  payment_date: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

export async function fetchEmployeesApi(): Promise<Employee[]> {
  const { data } = await apiClient.get<Employee[]>("/v1/hr/employees/");
  return data;
}

export async function fetchEmployeeApi(id: number): Promise<Employee> {
  const { data } = await apiClient.get<Employee>(`/v1/hr/employees/${id}/`);
  return data;
}

export async function createEmployeeApi(
  payload: Partial<Employee>,
): Promise<Employee> {
  const { data } = await apiClient.post<Employee>("/v1/hr/employees/", payload);
  return data;
}

export async function updateEmployeeApi(
  id: number,
  payload: Partial<Employee>,
): Promise<Employee> {
  const { data } = await apiClient.patch<Employee>(
    `/v1/hr/employees/${id}/`,
    payload,
  );
  return data;
}

export async function deleteEmployeeApi(id: number): Promise<void> {
  await apiClient.delete(`/v1/hr/employees/${id}/`);
}

export async function fetchDepartmentsApi(): Promise<Department[]> {
  const { data } = await apiClient.get<Department[]>("/v1/hr/departments/");
  return data;
}
