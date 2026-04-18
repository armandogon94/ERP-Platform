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

export async function fetchNotificationsApi(): Promise<Notification[]> {
  const { data } = await apiClient.get<Notification[]>("/v1/core/notifications/");
  return data;
}

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
