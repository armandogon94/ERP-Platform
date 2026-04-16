import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import SalesOrderListPage from "./SalesOrderListPage";

vi.mock("../../api/sales", () => ({
  fetchSalesOrdersApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchSalesOrdersApi } from "../../api/sales";

const mockFetchOrders = vi.mocked(fetchSalesOrdersApi);

const sampleOrders = [
  {
    id: 1,
    order_number: "SO-2026-001",
    customer_name: "Acme Corp",
    customer_email: "acme@example.com",
    quotation: null,
    status: "confirmed",
    order_date: "2026-01-10",
    delivery_date: null,
    notes: "",
    total_amount: "500.00",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
  {
    id: 2,
    order_number: "SO-2026-002",
    customer_name: "Globex Inc",
    customer_email: "globex@example.com",
    quotation: null,
    status: "delivered",
    order_date: "2026-01-15",
    delivery_date: "2026-01-20",
    notes: "",
    total_amount: "1200.00",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/sales/orders"]}>
      <Routes>
        <Route path="/sales/orders" element={<SalesOrderListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("SalesOrderListPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useConfigStore.setState({
      terminology: {},
      configs: {},
      modules: [],
      isLoading: false,
      error: null,
    });
  });

  it("renders page heading", () => {
    mockFetchOrders.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByRole("heading")).toBeInTheDocument();
  });

  it("shows order numbers after loading", async () => {
    mockFetchOrders.mockResolvedValueOnce(sampleOrders);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("SO-2026-001")).toBeInTheDocument();
      expect(screen.getByText("SO-2026-002")).toBeInTheDocument();
    });
  });

  it("shows loading state initially", () => {
    mockFetchOrders.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("shows error message on API failure", async () => {
    mockFetchOrders.mockRejectedValueOnce(new Error("Network Error"));
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it("renders customer name column", async () => {
    mockFetchOrders.mockResolvedValueOnce(sampleOrders);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Acme Corp")).toBeInTheDocument();
    });
  });

  it("renders status column", async () => {
    mockFetchOrders.mockResolvedValueOnce(sampleOrders);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("confirmed")).toBeInTheDocument();
    });
  });

  it("renders total amount", async () => {
    mockFetchOrders.mockResolvedValueOnce(sampleOrders);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("500.00")).toBeInTheDocument();
    });
  });

  it("uses terminology for the page heading", async () => {
    mockFetchOrders.mockResolvedValueOnce(sampleOrders);
    useConfigStore.setState({ terminology: { "Sales Order": "Guest Check" } });
    renderPage();
    await waitFor(() => {
      expect(screen.getAllByText(/Guest Check/i).length).toBeGreaterThan(0);
    });
  });
});
