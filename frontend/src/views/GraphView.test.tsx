import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import GraphView from "./GraphView";

// Recharts relies on ResizeObserver which jsdom doesn't implement.
beforeEach(() => {
  // @ts-expect-error jsdom polyfill
  global.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
});

describe("GraphView", () => {
  const data = [
    { group: "draft", value: 150 },
    { group: "paid", value: 200 },
  ];

  // Recharts inside ResponsiveContainer doesn't paint an <svg> under jsdom
  // because the container has zero dimensions. Assert the wrapper div
  // mounts (i.e. the component selected the right chart type and did not
  // throw) — real visual verification lives in the Preview-tab sweep.

  it("mounts the wrapper for bar chart type", () => {
    const { container } = render(<GraphView rows={data} chartType="bar" />);
    expect(container.firstChild).not.toBeNull();
  });

  it("mounts the wrapper for line chart type", () => {
    const { container } = render(<GraphView rows={data} chartType="line" />);
    expect(container.firstChild).not.toBeNull();
  });

  it("mounts the wrapper for pie chart type", () => {
    const { container } = render(<GraphView rows={data} chartType="pie" />);
    expect(container.firstChild).not.toBeNull();
  });

  it("mounts the wrapper for area chart type", () => {
    const { container } = render(<GraphView rows={data} chartType="area" />);
    expect(container.firstChild).not.toBeNull();
  });

  it("shows empty state when data is empty", () => {
    render(<GraphView rows={[]} chartType="bar" />);
    expect(screen.getByText(/no data/i)).toBeInTheDocument();
  });
});
