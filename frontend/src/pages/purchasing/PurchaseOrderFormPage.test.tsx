import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import PurchaseOrderFormPage from "./PurchaseOrderFormPage";

vi.mock("../../api/purchasing", () => ({
  fetchPurchaseOrderApi: vi.fn(),
  createPurchaseOrderApi: vi.fn(),
  updatePurchaseOrderApi: vi.fn(),
  fetchVendorsApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import {
  fetchPurchaseOrderApi,
  createPurchaseOrderApi,
  updatePurchaseOrderApi,
  fetchVendorsApi,
} from "../../api/purchasing";

const mockFetchPO = vi.mocked(fetchPurchaseOrderApi);
const mockCreatePO = vi.mocked(createPurchaseOrderApi);
const mockUpdatePO = vi.mocked(updatePurchaseOrderApi);
const mockFetchVendors = vi.mocked(fetchVendorsApi);

const sampleVendors = [
  {
    id: 1,
    name: "Acme Supplies",
    email: "",
    contact_name: "",
    phone: "",
    address: "",
    currency: "USD",
    payment_terms: "net_30",
    is_active: true,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

const samplePO = {
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
};

function renderNewForm() {
  return render(
    <MemoryRouter initialEntries={["/purchasing/purchase-orders/new"]}>
      <Routes>
        <Route
          path="/purchasing/purchase-orders/new"
          element={<PurchaseOrderFormPage />}
        />
      </Routes>
    </MemoryRouter>,
  );
}

function renderEditForm(id = 1) {
  return render(
    <MemoryRouter initialEntries={[`/purchasing/purchase-orders/${id}/edit`]}>
      <Routes>
        <Route
          path="/purchasing/purchase-orders/:id/edit"
          element={<PurchaseOrderFormPage />}
        />
      </Routes>
    </MemoryRouter>,
  );
}

describe("PurchaseOrderFormPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFetchVendors.mockResolvedValue(sampleVendors);
    useConfigStore.setState({
      terminology: {},
      configs: {},
      modules: [],
      isLoading: false,
      error: null,
    });
  });

  it("renders form heading for new PO", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByRole("heading")).toBeInTheDocument();
    });
  });

  it("shows New Purchase Order heading on create route", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/new purchase order/i)).toBeInTheDocument();
    });
  });

  it("shows Edit Purchase Order heading on edit route", async () => {
    mockFetchPO.mockResolvedValueOnce(samplePO);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByText(/edit purchase order/i)).toBeInTheDocument();
    });
  });

  it("pre-fills po_number when editing", async () => {
    mockFetchPO.mockResolvedValueOnce(samplePO);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("PO-2026-001")).toBeInTheDocument();
    });
  });

  it("calls createPurchaseOrderApi on submit for new PO", async () => {
    mockCreatePO.mockResolvedValueOnce(samplePO);
    renderNewForm();

    await waitFor(() => {
      expect(screen.getByLabelText(/po number/i)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText(/po number/i), {
      target: { value: "PO-NEW-001" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockCreatePO).toHaveBeenCalled();
    });
  });

  it("calls updatePurchaseOrderApi on submit for existing PO", async () => {
    mockFetchPO.mockResolvedValueOnce(samplePO);
    mockUpdatePO.mockResolvedValueOnce(samplePO);
    renderEditForm();

    await waitFor(() => {
      expect(screen.getByDisplayValue("PO-2026-001")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockUpdatePO).toHaveBeenCalledWith(1, expect.any(Object));
    });
  });

  it("uses terminology for the form heading", async () => {
    useConfigStore.setState({ terminology: { "Purchase Order": "Supply Request" } });
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/Supply Request/i)).toBeInTheDocument();
    });
  });
});
