import { useAuthStore } from "../stores/authStore";
import NotificationBell from "./NotificationBell";

interface TopNavbarProps {
  onToggleSidebar: () => void;
  onToggleAppSwitcher: () => void;
}

export default function TopNavbar({
  onToggleSidebar,
  onToggleAppSwitcher,
}: TopNavbarProps) {
  const { user, company, logout } = useAuthStore();

  const brandColor = company?.brand_color || "#714B67";

  return (
    <nav
      className="top-navbar"
      style={{ backgroundColor: brandColor }}
      aria-label="Main navigation"
    >
      <div className="navbar-left">
        <button
          className="navbar-toggle"
          onClick={onToggleSidebar}
          aria-label="Toggle sidebar"
        >
          &#9776;
        </button>
        <button
          className="app-switcher-btn"
          onClick={onToggleAppSwitcher}
          aria-label="Open app switcher"
        >
          &#9881;
        </button>
        <span className="company-name">{company?.name || "ERP Platform"}</span>
      </div>

      <div className="navbar-right">
        <NotificationBell />
        <span className="user-name">
          {user?.first_name} {user?.last_name}
        </span>
        <button className="logout-btn" onClick={logout}>
          Logout
        </button>
      </div>
    </nav>
  );
}
