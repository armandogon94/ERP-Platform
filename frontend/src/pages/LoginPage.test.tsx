import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import LoginPage from "./LoginPage";
import { useAuthStore } from "../stores/authStore";

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

function renderLogin() {
  return render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>,
  );
}

describe("LoginPage", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    useAuthStore.setState({
      user: null,
      company: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  });

  it("renders login form", () => {
    renderLogin();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  });

  it("shows heading", () => {
    renderLogin();
    expect(screen.getByText("ERP Platform")).toBeInTheDocument();
  });

  it("displays error message from store", () => {
    useAuthStore.setState({ error: "Invalid credentials" });
    renderLogin();
    expect(screen.getByRole("alert")).toHaveTextContent("Invalid credentials");
  });

  it("disables button while loading", () => {
    useAuthStore.setState({ isLoading: true });
    renderLogin();
    expect(screen.getByRole("button")).toBeDisabled();
    expect(screen.getByRole("button")).toHaveTextContent("Signing in...");
  });
});
