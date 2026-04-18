import { useCallback, useEffect, useState } from "react";
import {
  fetchNotificationsApi,
  markNotificationReadApi,
  type Notification,
} from "../api/notifications";

const POLL_INTERVAL_MS = 30_000;

export function useNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const refresh = useCallback(async () => {
    try {
      // REVIEW I-9: single round-trip returns both list + unread count.
      const { notifications: list, unreadCount: count } = await fetchNotificationsApi();
      setNotifications(list);
      setUnreadCount(count);
    } catch {
      // Silent fail — polling will retry.
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = window.setInterval(refresh, POLL_INTERVAL_MS);
    return () => window.clearInterval(id);
  }, [refresh]);

  const markRead = useCallback(
    async (id: number) => {
      await markNotificationReadApi(id);
      await refresh();
    },
    [refresh],
  );

  return { notifications, unreadCount, refresh, markRead };
}
