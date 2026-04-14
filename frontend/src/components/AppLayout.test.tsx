import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useAuthStore } from "../stores/authStore";
import { useConfigStore } from "../stores/configStore";
import AppLayout from "./AppLayout";

// Mock the config API so fetchModules doesn't hit the network
vi.mock("../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
  patchModuleConfigApi: vi.fn(),
}));

function renderLayout() {
  return render(
    <MemoryRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<div>Dashboard Content</div>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

describe("AppLayout", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.setState({
      user: {
        id: 1,
        email: "admin@novapay.com",
        first_name: "Admin",
        last_name: "NovaPay",
        company: null,
      },
      company: {
        id: 1,
        name: "NovaPay",
        slug: "novapay",
        brand_color: "#2563EB",
        industry: "fintech",
      },
      isAuthenticated: true,
    });
    useConfigStore.setState({
      modules: [],
      configs: {},
      terminology: {},
      isLoading: false,
      error: null,
    });
  });

  it("renders navbar with company name", () => {
    renderLayout();
    expect(screen.getByText("NovaPay")).toBeInTheDocument();
  });

  it("renders sidebar with fallback module links when API not loaded", () => {
    renderLayout();
    expect(screen.getByText("Accounting")).toBeInTheDocument();
    expect(screen.getByText("HR")).toBeInTheDocument();
    expect(screen.getByText("Sales")).toBeInTheDocument();
  });

  it("renders outlet content", () => {
    renderLayout();
    expect(screen.getByText("Dashboard Content")).toBeInTheDocument();
  });

  it("shows user name in navbar", () => {
    renderLayout();
    expect(screen.getByText(/Admin/)).toBeInTheDocument();
  });

  it("applies brand color to navbar", () => {
    renderLayout();
    const navbar = screen.getByRole("navigation", { name: /main/i });
    expect(navbar).toHaveStyle({ backgroundColor: "#2563EB" });
  });

  it("has logout button", () => {
    renderLayout();
    expect(screen.getByText("Logout")).toBeInTheDocument();
  });

  it("renders API-driven modules when available", () => {
    useConfigStore.setState({
      modules: [
        {
          id: 1,
          name: "inventory",
          display_name: "Supplies",
          icon: "medical",
          is_installed: true,
          is_visible: true,
          sequence: 1,
          color: "#059669",
        },
        {
          id: 2,
          name: "calendar",
          display_name: "Appointments",
          icon: "event",
          is_installed: true,
          is_visible: true,
          sequence: 2,
          color: "#2563EB",
        },
      ],
      isLoading: false,
      error: null,
    });

    renderLayout();
    // API display names used instead of hardcoded defaults
    expect(screen.getByText("Supplies")).toBeInTheDocument();
    expect(screen.getByText("Appointments")).toBeInTheDocument();
    // Original hardcoded labels no longer shown
    expect(screen.queryByText("Inventory")).not.toBeInTheDocument();
    expect(screen.queryByText("Calendar")).not.toBeInTheDocument();
  });

  it("falls back to hardcoded modules on API failure", () => {
    // modules remains empty (simulating API failure)
    useConfigStore.setState({ modules: [], error: "Network Error" });
    renderLayout();
    // Fallback defaults still visible
    expect(screen.getByText("Accounting")).toBeInTheDocument();
    expect(screen.getByText("HR")).toBeInTheDocument();
  });
});
