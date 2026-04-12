import { beforeEach, describe, expect, it, vi } from "vitest";
import { useAuthStore } from "./authStore";

// Mock the auth API
vi.mock("../api/auth", () => ({
  loginApi: vi.fn(),
  logoutApi: vi.fn(),
  getMeApi: vi.fn(),
}));

import { loginApi, logoutApi, getMeApi } from "../api/auth";

const mockLoginApi = vi.mocked(loginApi);
const mockLogoutApi = vi.mocked(logoutApi);
const mockGetMeApi = vi.mocked(getMeApi);

describe("authStore", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    // Reset the store
    useAuthStore.setState({
      user: null,
      company: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  });

  it("starts unauthenticated with no tokens", () => {
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
    expect(state.company).toBeNull();
  });

  it("login sets user, company, and tokens", async () => {
    const mockResponse = {
      access: "test-access",
      refresh: "test-refresh",
      user: { id: 1, email: "test@novapay.com", first_name: "Admin", last_name: "NovaPay", company: null },
      company: { id: 1, name: "NovaPay", slug: "novapay", brand_color: "#2563EB", industry: "fintech" },
    };
    mockLoginApi.mockResolvedValueOnce(mockResponse);

    await useAuthStore.getState().login("test@novapay.com", "admin");

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.user?.email).toBe("test@novapay.com");
    expect(state.company?.name).toBe("NovaPay");
    expect(localStorage.getItem("access_token")).toBe("test-access");
    expect(localStorage.getItem("refresh_token")).toBe("test-refresh");
  });

  it("login sets error on failure", async () => {
    mockLoginApi.mockRejectedValueOnce(new Error("Invalid credentials"));

    await expect(
      useAuthStore.getState().login("bad@email.com", "wrong"),
    ).rejects.toThrow();

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.error).toBe("Invalid credentials");
  });

  it("logout clears state and tokens", async () => {
    localStorage.setItem("access_token", "tok");
    localStorage.setItem("refresh_token", "ref");
    useAuthStore.setState({ isAuthenticated: true, user: { id: 1 } as any });

    mockLogoutApi.mockResolvedValueOnce(undefined);
    await useAuthStore.getState().logout();

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
    expect(localStorage.getItem("access_token")).toBeNull();
    expect(localStorage.getItem("refresh_token")).toBeNull();
  });

  it("loadUser fetches and sets user data", async () => {
    localStorage.setItem("access_token", "tok");
    useAuthStore.setState({ isAuthenticated: true });

    const mockUser = {
      id: 1,
      email: "admin@novapay.com",
      first_name: "Admin",
      last_name: "NovaPay",
      company: { id: 1, name: "NovaPay", slug: "novapay", brand_color: "#2563EB", industry: "fintech" },
    };
    mockGetMeApi.mockResolvedValueOnce(mockUser);

    await useAuthStore.getState().loadUser();

    const state = useAuthStore.getState();
    expect(state.user?.email).toBe("admin@novapay.com");
    expect(state.company?.name).toBe("NovaPay");
  });

  it("loadUser clears auth on failure", async () => {
    localStorage.setItem("access_token", "expired");
    useAuthStore.setState({ isAuthenticated: true });

    mockGetMeApi.mockRejectedValueOnce(new Error("401"));

    await useAuthStore.getState().loadUser();

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(localStorage.getItem("access_token")).toBeNull();
  });

  it("clearError resets error to null", () => {
    useAuthStore.setState({ error: "some error" });
    useAuthStore.getState().clearError();
    expect(useAuthStore.getState().error).toBeNull();
  });
});
