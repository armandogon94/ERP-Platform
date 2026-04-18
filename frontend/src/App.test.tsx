import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, it, expect, vi } from "vitest";
import App from "./App";
import { useAuthStore } from "./stores/authStore";

vi.mock("./api/home", () => ({
  fetchHomeKPIsApi: vi.fn().mockResolvedValue({ tiles: [] }),
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

  it("shows home page when authenticated", () => {
    useAuthStore.setState({ isAuthenticated: true });
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByRole("heading", { name: "Welcome" })).toBeInTheDocument();
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
