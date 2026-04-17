import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AuditLogTimelinePage from "./AuditLogTimelinePage";

vi.mock("../../api/auditLog", () => ({
  fetchAuditLogApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchAuditLogApi } from "../../api/auditLog";

const mockFetch = vi.mocked(fetchAuditLogApi);

function renderPage() {
  return render(
    <MemoryRouter>
      <AuditLogTimelinePage />
    </MemoryRouter>,
  );
}

describe("AuditLogTimelinePage", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it("renders a timeline of audit entries", async () => {
    mockFetch.mockResolvedValueOnce([
      {
        id: 1,
        model_name: "Invoice",
        model_id: 42,
        action: "create",
        user_name: "Alice Lane",
        old_values: {},
        new_values: { number: "INV-A" },
        timestamp: "2026-04-17T12:00:00Z",
      },
    ]);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText(/Invoice/)).toBeInTheDocument();
    });
    expect(screen.getByText(/Alice Lane/)).toBeInTheDocument();
    expect(screen.getByText(/create/i)).toBeInTheDocument();
  });

  it("shows empty state when no audit entries", async () => {
    mockFetch.mockResolvedValueOnce([]);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/no audit entries/i)).toBeInTheDocument();
    });
  });
});
