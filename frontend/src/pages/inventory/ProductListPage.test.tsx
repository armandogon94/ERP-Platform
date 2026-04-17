import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import ProductListPage from "./ProductListPage";

vi.mock("../../api/inventory", () => ({
  fetchProductsApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchProductsApi } from "../../api/inventory";

const mockFetchProducts = vi.mocked(fetchProductsApi);

const sampleProducts = [
  {
    id: 1,
    name: "Dental Mirror",
    sku: "SKU-001",
    description: "",
    category: null,
    category_name: null,
    unit_of_measure: "each",
    cost_price: "5.00",
    sale_price: "10.00",
    reorder_point: "5.00",
    min_stock_level: "0.00",
    is_active: true,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
  {
    id: 2,
    name: "Latex Gloves",
    sku: "SKU-002",
    description: "",
    category: null,
    category_name: null,
    unit_of_measure: "box",
    cost_price: "8.00",
    sale_price: "12.00",
    reorder_point: "10.00",
    min_stock_level: "0.00",
    is_active: true,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/inventory/products"]}>
      <Routes>
        <Route path="/inventory/products" element={<ProductListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ProductListPage", () => {
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

  it("renders page heading", async () => {
    mockFetchProducts.mockResolvedValueOnce(sampleProducts);
    renderPage();
    expect(screen.getByRole("heading")).toBeInTheDocument();
  });

  it("shows product names after loading", async () => {
    mockFetchProducts.mockResolvedValueOnce(sampleProducts);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Dental Mirror")).toBeInTheDocument();
      expect(screen.getByText("Latex Gloves")).toBeInTheDocument();
    });
  });

  it("shows loading state initially", () => {
    mockFetchProducts.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByRole("status", { name: /loading/i })).toBeInTheDocument();
  });

  it("shows error message on API failure", async () => {
    mockFetchProducts.mockRejectedValueOnce(new Error("Network Error"));
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it("uses terminology for the page label", async () => {
    mockFetchProducts.mockResolvedValueOnce(sampleProducts);
    useConfigStore.setState({ terminology: { Product: "Dental Supply" } });
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/dental supply/i)).toBeInTheDocument();
    });
  });

  it("renders SKU column", async () => {
    mockFetchProducts.mockResolvedValueOnce(sampleProducts);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("SKU-001")).toBeInTheDocument();
    });
  });

  it("renders sale price", async () => {
    mockFetchProducts.mockResolvedValueOnce(sampleProducts);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("10.00")).toBeInTheDocument();
    });
  });
});
