import apiClient from "./client";

export interface Notification {
  id: number;
  title: string;
  message: string;
  notification_type: "info" | "warning" | "error" | "success";
  is_read: boolean;
  action_url: string;
  related_model: string;
  related_id: number | null;
  created_at: string;
}

export interface NotificationsResponse {
  notifications: Notification[];
  unreadCount: number;
}

/**
 * REVIEW I-9: single request returns both the list AND the unread count
 * (the count ships as an `X-Unread-Count` response header). Halves the
 * polling round trips compared to the separate /unread_count/ endpoint.
 */
export async function fetchNotificationsApi(): Promise<NotificationsResponse> {
  const response = await apiClient.get<Notification[]>("/v1/core/notifications/");
  const headerCount = response.headers["x-unread-count"];
  const unreadCount =
    typeof headerCount === "string" ? Number.parseInt(headerCount, 10) || 0 : 0;
  return { notifications: response.data, unreadCount };
}

/** @deprecated Prefer {@link fetchNotificationsApi} — kept for callers that only need the count. */
export async function fetchUnreadCountApi(): Promise<number> {
  const { data } = await apiClient.get<{ count: number }>(
    "/v1/core/notifications/unread_count/",
  );
  return data.count;
}

export async function markNotificationReadApi(id: number): Promise<Notification> {
  const { data } = await apiClient.post<Notification>(
    `/v1/core/notifications/${id}/mark_read/`,
  );
  return data;
}
