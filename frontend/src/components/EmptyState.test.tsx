import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import EmptyState from "./EmptyState";

describe("EmptyState", () => {
  it("renders title and description", () => {
    render(
      <EmptyState
        title="Nothing here yet"
        description="Create your first record to get started."
      />,
    );
    expect(screen.getByText("Nothing here yet")).toBeInTheDocument();
    expect(screen.getByText(/first record/i)).toBeInTheDocument();
  });
});
