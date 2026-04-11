import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect } from "vitest";
import App from "./App";

describe("App", () => {
  it("renders without crashing", () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByText("ERP Platform")).toBeInTheDocument();
  });

  it("shows welcome message on home page", () => {
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
