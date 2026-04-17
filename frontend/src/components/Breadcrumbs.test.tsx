import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import Breadcrumbs from "./Breadcrumbs";

describe("Breadcrumbs", () => {
  it("renders Home + one segment at a single-level path", () => {
    render(
      <MemoryRouter initialEntries={["/hr"]}>
        <Breadcrumbs />
      </MemoryRouter>,
    );
    expect(screen.getByText(/home/i)).toBeInTheDocument();
    expect(screen.getByText("hr")).toBeInTheDocument();
  });

  it("renders Home + two segments at a nested path", () => {
    render(
      <MemoryRouter initialEntries={["/hr/employees"]}>
        <Breadcrumbs />
      </MemoryRouter>,
    );
    expect(screen.getByText("hr")).toBeInTheDocument();
    expect(screen.getByText("employees")).toBeInTheDocument();
  });

  it("renders only Home at root", () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <Breadcrumbs />
      </MemoryRouter>,
    );
    expect(screen.getByText(/home/i)).toBeInTheDocument();
    // No "/" segment
    expect(screen.queryByText("/")).not.toBeInTheDocument();
  });
});
