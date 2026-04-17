import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import HomePage from "./HomePage";

vi.mock("../api/home", () => ({
  fetchHomeKPIsApi: vi.fn(),
}));

vi.mock("../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchHomeKPIsApi } from "../api/home";

const mockFetch = vi.mocked(fetchHomeKPIsApi);

function renderPage() {
  return render(
    <MemoryRouter>
      <HomePage />
    </MemoryRouter>,
  );
}

describe("HomePage", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it("renders KPI tiles from the API", async () => {
    mockFetch.mockResolvedValueOnce({
      tiles: [
        { label: "Outstanding Invoices", value: "3", detail: "$1,250.00" },
        { label: "Open Tickets", value: "7" },
      ],
    });

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Outstanding Invoices")).toBeInTheDocument();
    });
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("$1,250.00")).toBeInTheDocument();
    expect(screen.getByText("Open Tickets")).toBeInTheDocument();
  });

  it("shows empty state when no tiles returned", async () => {
    mockFetch.mockResolvedValueOnce({ tiles: [] });

    renderPage();

    await waitFor(() => {
      expect(screen.getByText(/no metrics yet/i)).toBeInTheDocument();
    });
  });
});
