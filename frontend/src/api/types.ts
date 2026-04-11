/** Standard API error response shape */
export interface ApiError {
  detail: string;
  code?: string;
}

/** Standard paginated response from DRF cursor pagination */
export interface PaginatedResponse<T> {
  next: string | null;
  previous: string | null;
  results: T[];
}

/** JWT token pair from /auth/token/ */
export interface TokenPair {
  access: string;
  refresh: string;
}
