import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import POSOrderListPage from "./POSOrderListPage";

vi.mock("../../api/pos", () => ({
  fetchPOSOrdersApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchPOSOrdersApi } from "../../api/pos";

const mockFetch = vi.mocked(fetchPOSOrdersApi);

const sample = [
  {
    id: 1,
    session: 5,
    order_number: "POS/2026/00001",
    customer: null,
    customer_name: null,
    subtotal: "20.00",
    tax_amount: "2.00",
    total: "22.00",
    status: "paid",
    notes: "",
    created_at: "2026-04-17T10:00:00Z",
    updated_at: "2026-04-17T10:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/pos/orders"]}>
      <Routes>
        <Route path="/pos/orders" element={<POSOrderListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("POSOrderListPage", () => {
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

  it("shows orders after loading", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("POS/2026/00001")).toBeInTheDocument();
      expect(screen.getByText("paid")).toBeInTheDocument();
      expect(screen.getByText("22.00")).toBeInTheDocument();
    });
  });
});
