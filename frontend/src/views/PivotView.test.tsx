import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import PivotView from "./PivotView";

describe("PivotView", () => {
  it("renders rows from aggregated data", () => {
    const data = [
      { group: "draft", value: 150 },
      { group: "paid", value: 200 },
    ];
    render(
      <PivotView
        rows={data}
        rowLabel="Status"
        valueLabel="Total"
        formatter={(v) => `$${v.toFixed(2)}`}
      />,
    );
    expect(screen.getByText("Status")).toBeInTheDocument();
    expect(screen.getByText("draft")).toBeInTheDocument();
    expect(screen.getByText("paid")).toBeInTheDocument();
    expect(screen.getByText("$150.00")).toBeInTheDocument();
  });

  it("shows empty state when data is empty", () => {
    render(<PivotView rows={[]} rowLabel="Status" valueLabel="Total" />);
    expect(screen.getByText(/no data/i)).toBeInTheDocument();
  });
});
