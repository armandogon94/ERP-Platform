import { useState } from "react";
import { Bell } from "lucide-react";
import { Link } from "react-router-dom";
import { useNotifications } from "../hooks/useNotifications";

export default function NotificationBell(): JSX.Element {
  const { notifications, unreadCount, markRead } = useNotifications();
  const [open, setOpen] = useState(false);

  return (
    <div className="notification-bell">
      <button
        type="button"
        aria-label="Notifications"
        className="notification-bell-btn"
        onClick={() => setOpen((v) => !v)}
      >
        <Bell size={18} aria-hidden="true" />
        {unreadCount > 0 && (
          <span className="notification-badge" data-testid="notification-badge">
            {unreadCount}
          </span>
        )}
      </button>
      {open && (
        <div className="notification-panel" role="dialog" aria-label="Notifications">
          {notifications.length === 0 ? (
            <div className="notification-empty">No notifications</div>
          ) : (
            <ul className="notification-list">
              {notifications.map((n) => (
                <li
                  key={n.id}
                  className={`notification-item ${n.is_read ? "read" : "unread"}`}
                  onClick={() => markRead(n.id)}
                >
                  <strong>{n.title}</strong>
                  {n.message && <div className="notification-message">{n.message}</div>}
                  {n.action_url && (
                    <Link to={n.action_url} className="notification-link">
                      View
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
