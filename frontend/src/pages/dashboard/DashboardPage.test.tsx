import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import DashboardPage from "./DashboardPage";

vi.mock("../../api/dashboards", () => ({
  fetchDefaultDashboardApi: vi.fn(),
  fetchDashboardDataApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import {
  fetchDashboardDataApi,
  fetchDefaultDashboardApi,
} from "../../api/dashboards";

const mockDash = vi.mocked(fetchDefaultDashboardApi);
const mockData = vi.mocked(fetchDashboardDataApi);

function renderPage() {
  return render(
    <MemoryRouter>
      <DashboardPage />
    </MemoryRouter>,
  );
}

const DASHBOARD_STUB = {
  id: 7,
  name: "Clinic Overview",
  slug: "home",
  is_default: true,
  industry_preset: "dental",
  layout_json: {},
  created_at: "",
  updated_at: "",
};

describe("DashboardPage", () => {
  beforeEach(() => {
    mockDash.mockReset();
    mockData.mockReset();
  });

  it("renders a skeleton before dashboard + data arrive", () => {
    mockDash.mockReturnValue(new Promise(() => {}));
    renderPage();
    expect(screen.getByRole("heading", { name: /dashboard/i })).toBeInTheDocument();
  });

  it("renders the dashboard name + a KPI widget with its value", async () => {
    mockDash.mockResolvedValueOnce({
      ...DASHBOARD_STUB,
      widgets: [
        {
          id: 11,
          dashboard: 7,
          position: 0,
          widget_type: "kpi",
          title: "Today's Appointments",
          subtitle: "",
          data_source: "calendar.events_today",
          config_json: {},
          created_at: "",
          updated_at: "",
        },
      ],
    });
    mockData.mockResolvedValueOnce({
      11: { value: "12", detail: "today" },
    });

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Clinic Overview")).toBeInTheDocument();
    });
    expect(screen.getByText("Today's Appointments")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
  });

  it("surfaces an error tile when a widget payload contains an error envelope", async () => {
    mockDash.mockResolvedValueOnce({
      ...DASHBOARD_STUB,
      widgets: [
        {
          id: 22,
          dashboard: 7,
          position: 0,
          widget_type: "kpi",
          title: "Broken",
          subtitle: "",
          data_source: "nope.nothing",
          config_json: {},
          created_at: "",
          updated_at: "",
        },
      ],
    });
    mockData.mockResolvedValueOnce({ 22: { error: "Unknown data source: nope.nothing" } });

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Broken")).toBeInTheDocument();
    });
    expect(screen.getByRole("alert")).toHaveTextContent(/unknown data source/i);
  });

  it("renders a table widget with inferred columns", async () => {
    mockDash.mockResolvedValueOnce({
      ...DASHBOARD_STUB,
      widgets: [
        {
          id: 33,
          dashboard: 7,
          position: 0,
          widget_type: "table",
          title: "Low-Stock Items",
          subtitle: "",
          data_source: "inventory.low_stock_items",
          config_json: {},
          created_at: "",
          updated_at: "",
        },
      ],
    });
    mockData.mockResolvedValueOnce({
      33: [
        { name: "Toothbrush", reorder_point: 10, unit: "ea" },
        { name: "Floss", reorder_point: 50, unit: "ea" },
      ],
    });

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Low-Stock Items")).toBeInTheDocument();
    });
    expect(screen.getByText("Toothbrush")).toBeInTheDocument();
    expect(screen.getByText("Floss")).toBeInTheDocument();
  });

  it("shows an error alert on API failure", async () => {
    mockDash.mockRejectedValueOnce(new Error("boom"));
    renderPage();
    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("boom");
    });
  });
});
