import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, it, expect, vi } from "vitest";
import App from "./App";
import { useAuthStore } from "./stores/authStore";

vi.mock("./api/home", () => ({
  fetchHomeKPIsApi: vi.fn().mockResolvedValue({ tiles: [] }),
}));

vi.mock("./api/dashboards", () => ({
  fetchDefaultDashboardApi: vi.fn().mockResolvedValue({
    id: 1,
    name: "Welcome",
    slug: "home",
    is_default: true,
    industry_preset: "generic",
    layout_json: {},
    widgets: [],
    created_at: "",
    updated_at: "",
  }),
  fetchDashboardDataApi: vi.fn().mockResolvedValue({}),
}));

vi.mock("./api/notifications", () => ({
  fetchNotificationsApi: vi
    .fn()
    .mockResolvedValue({ notifications: [], unreadCount: 0 }),
  markNotificationReadApi: vi.fn(),
}));

vi.mock("./api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

describe("App", () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.setState({
      user: null,
      company: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  });

  it("renders without crashing", () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>,
    );
    // LoginPage is the default for unauthenticated users
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  });

  it("redirects to login when unauthenticated", () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  });

  it("shows the dashboard when authenticated", async () => {
    useAuthStore.setState({ isAuthenticated: true });
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>,
    );
    // DashboardPage renders a "Dashboard" heading while loading, then
    // swaps it for the dashboard name once the API resolves. Match
    // either so the test tolerates mock timing.
    expect(
      await screen.findByRole("heading", { name: /dashboard|welcome/i }),
    ).toBeInTheDocument();
  });

  it("shows 404 for unknown routes", () => {
    render(
      <MemoryRouter initialEntries={["/nonexistent"]}>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByText("404")).toBeInTheDocument();
    expect(screen.getByText("Page not found.")).toBeInTheDocument();
  });
});
