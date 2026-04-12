import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it } from "vitest";
import AppLayout from "./AppLayout";
import { useAuthStore } from "../stores/authStore";

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
    useAuthStore.setState({
      user: { id: 1, email: "admin@novapay.com", first_name: "Admin", last_name: "NovaPay", company: null },
      company: { id: 1, name: "NovaPay", slug: "novapay", brand_color: "#2563EB", industry: "fintech" },
      isAuthenticated: true,
    });
  });

  it("renders navbar with company name", () => {
    renderLayout();
    expect(screen.getByText("NovaPay")).toBeInTheDocument();
  });

  it("renders sidebar with module links", () => {
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
});
