import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import POSSessionFormPage from "./POSSessionFormPage";

vi.mock("../../api/pos", () => ({
  fetchPOSSessionApi: vi.fn(),
  createPOSSessionApi: vi.fn(),
  updatePOSSessionApi: vi.fn(),
  closePOSSessionApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import {
  fetchPOSSessionApi,
  createPOSSessionApi,
  closePOSSessionApi,
} from "../../api/pos";

const mockFetch = vi.mocked(fetchPOSSessionApi);
const mockCreate = vi.mocked(createPOSSessionApi);
const mockClose = vi.mocked(closePOSSessionApi);

const sample = {
  id: 1,
  station: "Bar-1",
  cash_on_open: "100.00",
  cash_on_close: null,
  expected_cash: null,
  variance: null,
  opened_by: 1,
  opened_by_username: "admin",
  opened_at: "2026-04-17T10:00:00Z",
  closed_at: null,
  status: "open",
  notes: "",
  created_at: "2026-04-17T10:00:00Z",
  updated_at: "2026-04-17T10:00:00Z",
};

function renderNewForm() {
  return render(
    <MemoryRouter initialEntries={["/pos/sessions/new"]}>
      <Routes>
        <Route path="/pos/sessions/new" element={<POSSessionFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

function renderEditForm(id = 1) {
  return render(
    <MemoryRouter initialEntries={[`/pos/sessions/${id}/edit`]}>
      <Routes>
        <Route path="/pos/sessions/:id/edit" element={<POSSessionFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("POSSessionFormPage", () => {
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

  it("shows New Session heading on create route", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/new session/i)).toBeInTheDocument();
    });
  });

  it("calls createPOSSessionApi on new submit", async () => {
    mockCreate.mockResolvedValueOnce(sample);
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByLabelText(/station/i)).toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText(/station/i), {
      target: { value: "Bar-99" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(mockCreate).toHaveBeenCalled();
    });
  });

  it("shows Close button when session is open", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderEditForm();
    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /close session/i }),
      ).toBeInTheDocument();
    });
  });

  it("calls closePOSSessionApi on Close click", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    mockClose.mockResolvedValueOnce({ ...sample, status: "closed" });
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByLabelText(/cash on close/i)).toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText(/cash on close/i), {
      target: { value: "150.00" },
    });
    fireEvent.click(screen.getByRole("button", { name: /close session/i }));
    await waitFor(() => {
      expect(mockClose).toHaveBeenCalledWith(1, { cash_on_close: "150.00" });
    });
  });
});
