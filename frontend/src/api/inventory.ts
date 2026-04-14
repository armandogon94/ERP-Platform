import apiClient from "./client";

export interface Product {
  id: number;
  name: string;
  sku: string;
  description: string;
  category: number | null;
  category_name: string | null;
  unit_of_measure: string;
  cost_price: string;
  sale_price: string;
  reorder_point: string | null;
  min_stock_level: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductCategory {
  id: number;
  name: string;
  description: string;
  parent: number | null;
  created_at: string;
  updated_at: string;
}

export interface StockLocation {
  id: number;
  name: string;
  location_type: string;
  parent: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface StockMove {
  id: number;
  product: number;
  product_name: string;
  source_location: number;
  source_location_name: string;
  destination_location: number;
  destination_location_name: string;
  quantity: string;
  lot: number | null;
  move_type: string;
  status: string;
  reference: string;
  move_date: string | null;
  created_at: string;
  updated_at: string;
}

export async function fetchProductsApi(params?: Record<string, string>): Promise<Product[]> {
  const { data } = await apiClient.get<Product[]>("/v1/inventory/products/", { params });
  return data;
}

export async function fetchProductApi(id: number): Promise<Product> {
  const { data } = await apiClient.get<Product>(`/v1/inventory/products/${id}/`);
  return data;
}

export async function createProductApi(payload: Partial<Product>): Promise<Product> {
  const { data } = await apiClient.post<Product>("/v1/inventory/products/", payload);
  return data;
}

export async function updateProductApi(
  id: number,
  payload: Partial<Product>,
): Promise<Product> {
  const { data } = await apiClient.patch<Product>(
    `/v1/inventory/products/${id}/`,
    payload,
  );
  return data;
}

export async function deleteProductApi(id: number): Promise<void> {
  await apiClient.delete(`/v1/inventory/products/${id}/`);
}

export async function fetchCategoriesApi(): Promise<ProductCategory[]> {
  const { data } = await apiClient.get<ProductCategory[]>("/v1/inventory/categories/");
  return data;
}

export async function fetchLocationsApi(): Promise<StockLocation[]> {
  const { data } = await apiClient.get<StockLocation[]>("/v1/inventory/locations/");
  return data;
}
