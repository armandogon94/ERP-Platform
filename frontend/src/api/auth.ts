import apiClient from "./client";

export interface Company {
  id: number;
  name: string;
  slug: string;
  brand_color: string;
  industry: string;
}

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  company: Company | null;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
  company: Company;
}

export async function loginApi(
  email: string,
  password: string,
): Promise<LoginResponse> {
  const { data } = await apiClient.post<LoginResponse>("/v1/auth/login/", {
    email,
    password,
  });
  return data;
}

export async function logoutApi(refresh: string): Promise<void> {
  await apiClient.post("/v1/auth/logout/", { refresh });
}

export async function getMeApi(): Promise<User> {
  const { data } = await apiClient.get<User>("/v1/auth/me/");
  return data;
}
