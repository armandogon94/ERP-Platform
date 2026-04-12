import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, it, expect } from "vitest";
import App from "./App";
import { useAuthStore } from "./stores/authStore";

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
    expect(screen.getByText("ERP Platform")).toBeInTheDocument();
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
    expect(screen.getByText("Welcome to the ERP Platform.")).toBeInTheDocument();
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
