import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ListPageShell from "./ListPageShell";

describe("ListPageShell", () => {
  it("renders title + children when loaded", () => {
    render(
      <ListPageShell title="Employees" isLoading={false}>
        <table data-testid="t">content</table>
      </ListPageShell>,
    );
    expect(screen.getByRole("heading", { name: "Employees" })).toBeInTheDocument();
    expect(screen.getByTestId("t")).toBeInTheDocument();
  });

  it("renders a skeleton while loading and hides children", () => {
    render(
      <ListPageShell title="Employees" isLoading={true}>
        <table data-testid="t">content</table>
      </ListPageShell>,
    );
    expect(screen.getByRole("status", { name: /loading/i })).toBeInTheDocument();
    expect(screen.queryByTestId("t")).not.toBeInTheDocument();
  });

  it("shows the error alert and hides children on error", () => {
    render(
      <ListPageShell title="Employees" isLoading={false} error="Boom">
        <table data-testid="t">content</table>
      </ListPageShell>,
    );
    expect(screen.getByRole("alert")).toHaveTextContent("Boom");
    expect(screen.queryByTestId("t")).not.toBeInTheDocument();
  });

  it("renders the empty state when isEmpty + empty provided", () => {
    render(
      <ListPageShell
        title="Employees"
        isLoading={false}
        isEmpty={true}
        empty={{ title: "No employees yet", description: "Add your first one." }}
      >
        <table data-testid="t">content</table>
      </ListPageShell>,
    );
    expect(screen.getByText("No employees yet")).toBeInTheDocument();
    expect(screen.queryByTestId("t")).not.toBeInTheDocument();
  });

  it("renders actions next to the heading", () => {
    render(
      <ListPageShell title="Employees" isLoading={false} actions={<button>New</button>}>
        <table />
      </ListPageShell>,
    );
    expect(screen.getByRole("button", { name: "New" })).toBeInTheDocument();
  });
});
