import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import ProductFormPage from "./ProductFormPage";

vi.mock("../../api/inventory", () => ({
  fetchProductApi: vi.fn(),
  createProductApi: vi.fn(),
  updateProductApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import {
  fetchProductApi,
  createProductApi,
  updateProductApi,
} from "../../api/inventory";

const mockFetchProduct = vi.mocked(fetchProductApi);
const mockCreateProduct = vi.mocked(createProductApi);
const mockUpdateProduct = vi.mocked(updateProductApi);

const sampleProduct = {
  id: 1,
  name: "Dental Mirror",
  sku: "SKU-001",
  description: "Standard dental mirror",
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
};

function renderNewForm() {
  return render(
    <MemoryRouter initialEntries={["/inventory/products/new"]}>
      <Routes>
        <Route path="/inventory/products/new" element={<ProductFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

function renderEditForm(id = 1) {
  return render(
    <MemoryRouter initialEntries={[`/inventory/products/${id}/edit`]}>
      <Routes>
        <Route path="/inventory/products/:id/edit" element={<ProductFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ProductFormPage", () => {
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

  it("renders form heading for new product", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByRole("heading")).toBeInTheDocument();
    });
  });

  it("shows New Product heading on create route", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/new product/i)).toBeInTheDocument();
    });
  });

  it("shows Edit Product heading on edit route", async () => {
    mockFetchProduct.mockResolvedValueOnce(sampleProduct);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByText(/edit product/i)).toBeInTheDocument();
    });
  });

  it("pre-fills form fields when editing", async () => {
    mockFetchProduct.mockResolvedValueOnce(sampleProduct);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("Dental Mirror")).toBeInTheDocument();
      expect(screen.getByDisplayValue("SKU-001")).toBeInTheDocument();
    });
  });

  it("calls createProductApi on submit for new product", async () => {
    mockCreateProduct.mockResolvedValueOnce(sampleProduct);
    renderNewForm();

    await waitFor(() => {
      expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText(/name/i), {
      target: { value: "New Item" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockCreateProduct).toHaveBeenCalled();
    });
  });

  it("calls updateProductApi on submit for existing product", async () => {
    mockFetchProduct.mockResolvedValueOnce(sampleProduct);
    mockUpdateProduct.mockResolvedValueOnce(sampleProduct);
    renderEditForm();

    await waitFor(() => {
      expect(screen.getByDisplayValue("Dental Mirror")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockUpdateProduct).toHaveBeenCalledWith(1, expect.any(Object));
    });
  });

  it("uses terminology for form label", async () => {
    useConfigStore.setState({ terminology: { Product: "Supply Item" } });
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /supply item/i })).toBeInTheDocument();
    });
  });
});
