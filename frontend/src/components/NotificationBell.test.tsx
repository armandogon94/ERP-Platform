import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import NotificationBell from "./NotificationBell";

vi.mock("../api/notifications", () => ({
  fetchNotificationsApi: vi.fn(),
  markNotificationReadApi: vi.fn(),
}));

import { fetchNotificationsApi } from "../api/notifications";

const mockFetch = vi.mocked(fetchNotificationsApi);

describe("NotificationBell", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it("renders a bell button", () => {
    mockFetch.mockResolvedValue({ notifications: [], unreadCount: 0 });
    render(<NotificationBell />);
    expect(screen.getByRole("button", { name: /notifications/i })).toBeInTheDocument();
  });

  it("shows unread count badge when > 0", async () => {
    mockFetch.mockResolvedValue({ notifications: [], unreadCount: 3 });
    render(<NotificationBell />);
    await waitFor(() => {
      expect(screen.getByText("3")).toBeInTheDocument();
    });
  });

  it("hides the badge when unread count is 0", async () => {
    mockFetch.mockResolvedValue({ notifications: [], unreadCount: 0 });
    render(<NotificationBell />);
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalled();
    });
    expect(screen.queryByTestId("notification-badge")).not.toBeInTheDocument();
  });
});
