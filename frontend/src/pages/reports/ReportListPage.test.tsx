import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ReportListPage from "./ReportListPage";

vi.mock("../../api/reports", () => ({
  fetchReportTemplatesApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchReportTemplatesApi } from "../../api/reports";

const mockFetch = vi.mocked(fetchReportTemplatesApi);

function renderPage() {
  return render(
    <MemoryRouter>
      <ReportListPage />
    </MemoryRouter>,
  );
}

describe("ReportListPage", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it("renders a skeleton while loading", () => {
    mockFetch.mockReturnValue(new Promise(() => {}));
    renderPage();
    expect(screen.getByRole("status", { name: /loading/i })).toBeInTheDocument();
  });

  it("renders the builder link and a row for each template", async () => {
    mockFetch.mockResolvedValueOnce([
      {
        id: 1,
        name: "Monthly Sales",
        model_name: "sales.SalesOrder",
        default_filters: {},
        default_group_by: ["customer_name"],
        default_measures: ["total_amount"],
        industry_tag: "fintech",
        description: "End-of-month rollup",
        created_at: "2026-04-17T00:00:00Z",
        updated_at: "2026-04-17T00:00:00Z",
      },
      {
        id: 2,
        name: "Invoices by Customer",
        model_name: "invoicing.Invoice",
        default_filters: {},
        default_group_by: ["customer_name"],
        default_measures: ["total_amount"],
        industry_tag: "",
        description: "",
        created_at: "2026-04-17T00:00:00Z",
        updated_at: "2026-04-17T00:00:00Z",
      },
    ]);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Monthly Sales")).toBeInTheDocument();
    });
    expect(screen.getByText("Invoices by Customer")).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /new report/i }),
    ).toHaveAttribute("href", "/reports/builder");
  });

  it("surfaces errors via role=alert", async () => {
    mockFetch.mockRejectedValueOnce(new Error("Server exploded"));
    renderPage();
    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("Server exploded");
    });
  });
});
