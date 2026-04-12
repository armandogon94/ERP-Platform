import { useState } from "react";
import { Outlet } from "react-router-dom";
import AppSwitcher, { type AppModule } from "./AppSwitcher";
import Sidebar, { type SidebarItem } from "./Sidebar";
import TopNavbar from "./TopNavbar";

// Default sidebar items (modules will be loaded from API later)
const DEFAULT_SIDEBAR_ITEMS: SidebarItem[] = [
  { name: "accounting", label: "Accounting", icon: "\u{1F4B0}", url: "/accounting" },
  { name: "invoicing", label: "Invoicing", icon: "\u{1F4C4}", url: "/invoicing" },
  { name: "inventory", label: "Inventory", icon: "\u{1F4E6}", url: "/inventory" },
  { name: "hr", label: "HR", icon: "\u{1F465}", url: "/hr" },
  { name: "sales", label: "Sales", icon: "\u{1F4C8}", url: "/sales" },
  { name: "purchasing", label: "Purchasing", icon: "\u{1F6D2}", url: "/purchasing" },
  { name: "calendar", label: "Calendar", icon: "\u{1F4C5}", url: "/calendar" },
  { name: "projects", label: "Projects", icon: "\u{1F4CB}", url: "/projects" },
  { name: "helpdesk", label: "Helpdesk", icon: "\u{1F3AB}", url: "/helpdesk" },
];

const DEFAULT_MODULES: AppModule[] = DEFAULT_SIDEBAR_ITEMS.map((item) => ({
  name: item.name,
  display_name: item.label,
  icon: item.icon,
  color: "#714B67",
}));

export default function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [appSwitcherOpen, setAppSwitcherOpen] = useState(false);

  return (
    <div className="app-layout">
      <TopNavbar
        onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
        onToggleAppSwitcher={() => setAppSwitcherOpen((prev) => !prev)}
      />
      <div className="app-body">
        <Sidebar items={DEFAULT_SIDEBAR_ITEMS} isOpen={sidebarOpen} />
        <main className="app-content">
          <Outlet />
        </main>
      </div>
      <AppSwitcher
        modules={DEFAULT_MODULES}
        isOpen={appSwitcherOpen}
        onClose={() => setAppSwitcherOpen(false)}
      />
    </div>
  );
}
