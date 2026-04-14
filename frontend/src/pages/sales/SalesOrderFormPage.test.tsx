import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import SalesOrderFormPage from "./SalesOrderFormPage";

vi.mock("../../api/sales", () => ({
  fetchSalesOrderApi: vi.fn(),
  createSalesOrderApi: vi.fn(),
  updateSalesOrderApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import {
  fetchSalesOrderApi,
  createSalesOrderApi,
  updateSalesOrderApi,
} from "../../api/sales";

const mockFetchOrder = vi.mocked(fetchSalesOrderApi);
const mockCreateOrder = vi.mocked(createSalesOrderApi);
const mockUpdateOrder = vi.mocked(updateSalesOrderApi);

const sampleOrder = {
  id: 1,
  order_number: "SO-2026-001",
  customer_name: "Acme Corp",
  customer_email: "acme@example.com",
  quotation: null,
  status: "confirmed",
  order_date: null,
  delivery_date: null,
  notes: "",
  total_amount: "500.00",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

function renderNewForm() {
  return render(
    <MemoryRouter initialEntries={["/sales/orders/new"]}>
      <Routes>
        <Route path="/sales/orders/new" element={<SalesOrderFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

function renderEditForm(id = 1) {
  return render(
    <MemoryRouter initialEntries={[`/sales/orders/${id}/edit`]}>
      <Routes>
        <Route path="/sales/orders/:id/edit" element={<SalesOrderFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("SalesOrderFormPage", () => {
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

  it("renders form heading for new order", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByRole("heading")).toBeInTheDocument();
    });
  });

  it("shows New Sales Order heading on create route", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/new sales order/i)).toBeInTheDocument();
    });
  });

  it("shows Edit Sales Order heading on edit route", async () => {
    mockFetchOrder.mockResolvedValueOnce(sampleOrder);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByText(/edit sales order/i)).toBeInTheDocument();
    });
  });

  it("pre-fills order_number when editing", async () => {
    mockFetchOrder.mockResolvedValueOnce(sampleOrder);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("SO-2026-001")).toBeInTheDocument();
    });
  });

  it("pre-fills customer_name when editing", async () => {
    mockFetchOrder.mockResolvedValueOnce(sampleOrder);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("Acme Corp")).toBeInTheDocument();
    });
  });

  it("calls createSalesOrderApi on submit for new order", async () => {
    mockCreateOrder.mockResolvedValueOnce(sampleOrder);
    renderNewForm();

    await waitFor(() => {
      expect(screen.getByLabelText(/order number/i)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText(/order number/i), {
      target: { value: "SO-NEW-001" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockCreateOrder).toHaveBeenCalled();
    });
  });

  it("calls updateSalesOrderApi on submit for existing order", async () => {
    mockFetchOrder.mockResolvedValueOnce(sampleOrder);
    mockUpdateOrder.mockResolvedValueOnce(sampleOrder);
    renderEditForm();

    await waitFor(() => {
      expect(screen.getByDisplayValue("SO-2026-001")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockUpdateOrder).toHaveBeenCalledWith(1, expect.any(Object));
    });
  });
});
