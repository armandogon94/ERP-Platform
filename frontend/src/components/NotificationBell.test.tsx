import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import NotificationBell from "./NotificationBell";

vi.mock("../api/notifications", () => ({
  fetchNotificationsApi: vi.fn(),
  fetchUnreadCountApi: vi.fn(),
  markNotificationReadApi: vi.fn(),
}));

import { fetchNotificationsApi, fetchUnreadCountApi } from "../api/notifications";

const mockList = vi.mocked(fetchNotificationsApi);
const mockCount = vi.mocked(fetchUnreadCountApi);

describe("NotificationBell", () => {
  beforeEach(() => {
    mockList.mockReset();
    mockCount.mockReset();
  });

  it("renders a bell button", () => {
    mockList.mockResolvedValue([]);
    mockCount.mockResolvedValue(0);
    render(<NotificationBell />);
    expect(screen.getByRole("button", { name: /notifications/i })).toBeInTheDocument();
  });

  it("shows unread count badge when > 0", async () => {
    mockList.mockResolvedValue([]);
    mockCount.mockResolvedValue(3);
    render(<NotificationBell />);
    await waitFor(() => {
      expect(screen.getByText("3")).toBeInTheDocument();
    });
  });

  it("hides the badge when unread count is 0", async () => {
    mockList.mockResolvedValue([]);
    mockCount.mockResolvedValue(0);
    render(<NotificationBell />);
    await waitFor(() => {
      expect(mockCount).toHaveBeenCalled();
    });
    expect(screen.queryByTestId("notification-badge")).not.toBeInTheDocument();
  });
});
