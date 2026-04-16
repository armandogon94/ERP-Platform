import { useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
import { useConfigStore } from "../stores/configStore";
import AppSwitcher, { type AppModule } from "./AppSwitcher";
import Sidebar, { type SidebarItem } from "./Sidebar";
import TopNavbar from "./TopNavbar";

// Fallback sidebar items shown while API loads or if fetch fails
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

function modulesToSidebarItems(
  modules: { name: string; display_name: string; icon: string }[],
): SidebarItem[] {
  return modules
    .filter((m) => m.name !== "reports") // reports is a BI module, not a sidebar item
    .map((m) => ({
      name: m.name,
      label: m.display_name,
      icon: m.icon || "\u{1F4CB}",
      url: `/${m.name}`,
    }));
}

export default function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [appSwitcherOpen, setAppSwitcherOpen] = useState(false);

  const { modules, fetchModules, fetchModuleConfig } = useConfigStore();

  useEffect(() => {
    fetchModules();
  }, [fetchModules]);

  useEffect(() => {
    // Prefetch each module's config so terminology is populated globally.
    for (const m of modules) {
      fetchModuleConfig(m.id, m.name);
    }
  }, [modules, fetchModuleConfig]);

  const sidebarItems =
    modules.length > 0 ? modulesToSidebarItems(modules) : DEFAULT_SIDEBAR_ITEMS;

  const appModules: AppModule[] =
    modules.length > 0
      ? modules.map((m) => ({
          name: m.name,
          display_name: m.display_name,
          icon: m.icon || "\u{1F4CB}",
          color: m.color || "#714B67",
        }))
      : DEFAULT_MODULES;

  return (
    <div className="app-layout">
      <TopNavbar
        onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
        onToggleAppSwitcher={() => setAppSwitcherOpen((prev) => !prev)}
      />
      <div className="app-body">
        <Sidebar items={sidebarItems} isOpen={sidebarOpen} />
        <main className="app-content">
          <Outlet />
        </main>
      </div>
      <AppSwitcher
        modules={appModules}
        isOpen={appSwitcherOpen}
        onClose={() => setAppSwitcherOpen(false)}
      />
    </div>
  );
}
