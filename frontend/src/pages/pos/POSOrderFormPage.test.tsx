import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import POSOrderFormPage from "./POSOrderFormPage";

vi.mock("../../api/pos", () => ({
  fetchPOSOrderApi: vi.fn(),
  createPOSOrderApi: vi.fn(),
  updatePOSOrderApi: vi.fn(),
  fetchPOSSessionsApi: vi.fn().mockResolvedValue([]),
}));

vi.mock("../../api/partners", () => ({
  fetchPartnersApi: vi.fn().mockResolvedValue([]),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import {
  fetchPOSOrderApi,
  createPOSOrderApi,
  updatePOSOrderApi,
} from "../../api/pos";

const mockFetch = vi.mocked(fetchPOSOrderApi);
const mockCreate = vi.mocked(createPOSOrderApi);
const mockUpdate = vi.mocked(updatePOSOrderApi);

const sample = {
  id: 1,
  session: 5,
  order_number: "POS/2026/00001",
  customer: null,
  customer_name: null,
  subtotal: "20.00",
  tax_amount: "2.00",
  total: "22.00",
  status: "draft",
  notes: "",
  created_at: "2026-04-17T10:00:00Z",
  updated_at: "2026-04-17T10:00:00Z",
};

function renderNewForm() {
  return render(
    <MemoryRouter initialEntries={["/pos/orders/new"]}>
      <Routes>
        <Route path="/pos/orders/new" element={<POSOrderFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

function renderEditForm(id = 1) {
  return render(
    <MemoryRouter initialEntries={[`/pos/orders/${id}/edit`]}>
      <Routes>
        <Route path="/pos/orders/:id/edit" element={<POSOrderFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("POSOrderFormPage", () => {
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

  it("shows New Order heading on create route", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/new order/i)).toBeInTheDocument();
    });
  });

  it("pre-fills total when editing", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("22.00")).toBeInTheDocument();
    });
  });

  it("calls createPOSOrderApi on new submit", async () => {
    mockCreate.mockResolvedValueOnce(sample);
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByLabelText(/^total$/i)).toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText(/^total$/i), {
      target: { value: "50.00" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(mockCreate).toHaveBeenCalled();
    });
  });

  it("calls updatePOSOrderApi on edit submit", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    mockUpdate.mockResolvedValueOnce(sample);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("22.00")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(mockUpdate).toHaveBeenCalledWith(1, expect.any(Object));
    });
  });
});
