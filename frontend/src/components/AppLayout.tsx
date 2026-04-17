import { useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";
import { useConfigStore } from "../stores/configStore";
import AppSwitcher, { type AppModule } from "./AppSwitcher";
import Sidebar, { type SidebarItem } from "./Sidebar";
import TopNavbar from "./TopNavbar";
import "./AppLayout.css";

// Shade a hex color toward black by `amount` (0–1). Used for --accent-strong.
function darken(hex: string, amount: number): string {
  const m = hex.replace("#", "");
  if (m.length !== 6) return hex;
  const num = parseInt(m, 16);
  const r = Math.max(0, Math.round(((num >> 16) & 0xff) * (1 - amount)));
  const g = Math.max(0, Math.round(((num >> 8) & 0xff) * (1 - amount)));
  const b = Math.max(0, Math.round((num & 0xff) * (1 - amount)));
  return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, "0")}`;
}

// Fallback sidebar items shown while API loads or if fetch fails
const DEFAULT_SIDEBAR_ITEMS: SidebarItem[] = [
  { name: "accounting", label: "Accounting", icon: "\u{1F4B0}", url: "/accounting" },
  { name: "invoicing", label: "Invoicing", icon: "\u{1F4C4}", url: "/invoicing" },
  { name: "inventory", label: "Inventory", icon: "\u{1F4E6}", url: "/inventory" },
  { name: "hr", label: "HR", icon: "\u{1F465}", url: "/hr" },
  { name: "sales", label: "Sales", icon: "\u{1F4C8}", url: "/sales" },
  { name: "purchasing", label: "Purchasing", icon: "\u{1F6D2}", url: "/purchasing" },
  { name: "calendar", label: "Calendar", icon: "\u{1F4C5}", url: "/calendar" },
  { name: "projects", label: "Projects", icon: "\u{1F4CB}", url: "/projects/projects" },
  { name: "helpdesk", label: "Helpdesk", icon: "\u{1F3AB}", url: "/helpdesk" },
  { name: "fleet", label: "Fleet", icon: "\u{1F69A}", url: "/fleet/vehicles" },
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
  const brandColor = useAuthStore((s) => s.company?.brand_color);

  useEffect(() => {
    fetchModules();
  }, [fetchModules]);

  useEffect(() => {
    // Prefetch each module's config so terminology is populated globally.
    for (const m of modules) {
      fetchModuleConfig(m.id, m.name);
    }
  }, [modules, fetchModuleConfig]);

  useEffect(() => {
    // Apply per-company theming via CSS custom properties (see D34).
    if (!brandColor) return;
    const root = document.documentElement;
    root.style.setProperty("--accent", brandColor);
    root.style.setProperty("--accent-strong", darken(brandColor, 0.15));
  }, [brandColor]);

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
