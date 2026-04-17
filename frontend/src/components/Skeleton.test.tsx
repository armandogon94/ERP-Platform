import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Skeleton from "./Skeleton";

describe("Skeleton", () => {
  it("renders with role=status for screen readers", () => {
    render(<Skeleton lines={3} />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("renders the requested number of bars", () => {
    const { container } = render(<Skeleton lines={4} />);
    expect(container.querySelectorAll(".skeleton-bar").length).toBe(4);
  });
});
