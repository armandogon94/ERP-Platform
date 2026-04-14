import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import PurchaseOrderListPage from "./PurchaseOrderListPage";

vi.mock("../../api/purchasing", () => ({
  fetchPurchaseOrdersApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchPurchaseOrdersApi } from "../../api/purchasing";

const mockFetchPOs = vi.mocked(fetchPurchaseOrdersApi);

const samplePOs = [
  {
    id: 1,
    vendor: 1,
    vendor_name: "Acme Supplies",
    po_number: "PO-2026-001",
    status: "draft",
    order_date: null,
    expected_date: null,
    notes: "",
    total_amount: "250.00",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
  {
    id: 2,
    vendor: 2,
    vendor_name: "MedLine",
    po_number: "PO-2026-002",
    status: "confirmed",
    order_date: "2026-01-10",
    expected_date: "2026-01-20",
    notes: "",
    total_amount: "800.00",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/purchasing/purchase-orders"]}>
      <Routes>
        <Route path="/purchasing/purchase-orders" element={<PurchaseOrderListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("PurchaseOrderListPage", () => {
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
    mockFetchPOs.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByRole("heading")).toBeInTheDocument();
  });

  it("shows PO numbers after loading", async () => {
    mockFetchPOs.mockResolvedValueOnce(samplePOs);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("PO-2026-001")).toBeInTheDocument();
      expect(screen.getByText("PO-2026-002")).toBeInTheDocument();
    });
  });

  it("shows loading state initially", () => {
    mockFetchPOs.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("shows error message on API failure", async () => {
    mockFetchPOs.mockRejectedValueOnce(new Error("Network Error"));
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it("renders vendor name column", async () => {
    mockFetchPOs.mockResolvedValueOnce(samplePOs);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Acme Supplies")).toBeInTheDocument();
    });
  });

  it("renders status column", async () => {
    mockFetchPOs.mockResolvedValueOnce(samplePOs);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("draft")).toBeInTheDocument();
    });
  });
});
