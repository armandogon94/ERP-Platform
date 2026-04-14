import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import EventListPage from "./EventListPage";

vi.mock("../../api/calendar", () => ({
  fetchEventsApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchEventsApi } from "../../api/calendar";

const mockFetchEvents = vi.mocked(fetchEventsApi);

const now = "2026-04-14T10:00:00Z";
const sampleEvents = [
  {
    id: 1,
    title: "Team Standup",
    description: "",
    start_datetime: now,
    end_datetime: "2026-04-14T10:30:00Z",
    event_type: "meeting",
    status: "confirmed",
    location: "Zoom",
    all_day: false,
    is_recurring: false,
    recurrence_rule: "",
    external_uid: null,
    attendee_count: 3,
    created_at: now,
    updated_at: now,
  },
  {
    id: 2,
    title: "Sprint Review",
    description: "",
    start_datetime: "2026-04-14T14:00:00Z",
    end_datetime: "2026-04-14T15:00:00Z",
    event_type: "meeting",
    status: "confirmed",
    location: "Board Room",
    all_day: false,
    is_recurring: false,
    recurrence_rule: "",
    external_uid: null,
    attendee_count: 8,
    created_at: now,
    updated_at: now,
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/calendar/events"]}>
      <Routes>
        <Route path="/calendar/events" element={<EventListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("EventListPage", () => {
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
    mockFetchEvents.mockResolvedValueOnce(sampleEvents);
    renderPage();
    expect(screen.getByRole("heading")).toBeInTheDocument();
  });

  it("shows event titles after loading", async () => {
    mockFetchEvents.mockResolvedValueOnce(sampleEvents);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Team Standup")).toBeInTheDocument();
      expect(screen.getByText("Sprint Review")).toBeInTheDocument();
    });
  });

  it("shows loading state initially", () => {
    mockFetchEvents.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("shows error message on API failure", async () => {
    mockFetchEvents.mockRejectedValueOnce(new Error("Network Error"));
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it("uses terminology for the page label", async () => {
    mockFetchEvents.mockResolvedValueOnce(sampleEvents);
    useConfigStore.setState({ terminology: { Event: "Appointment" } });
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/appointment/i)).toBeInTheDocument();
    });
  });

  it("renders status column", async () => {
    mockFetchEvents.mockResolvedValueOnce(sampleEvents);
    renderPage();
    await waitFor(() => {
      expect(screen.getAllByText("confirmed").length).toBeGreaterThan(0);
    });
  });

  it("renders attendee count", async () => {
    mockFetchEvents.mockResolvedValueOnce(sampleEvents);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("3")).toBeInTheDocument();
    });
  });
});
