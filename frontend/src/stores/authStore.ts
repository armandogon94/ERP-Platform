import { create } from "zustand";
import { type Company, type User, getMeApi, loginApi, logoutApi } from "../api/auth";

interface AuthState {
  user: User | null;
  company: Company | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loadUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  company: null,
  isAuthenticated: !!localStorage.getItem("access_token"),
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await loginApi(email, password);
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
      set({
        user: data.user,
        company: data.company,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Login failed";
      set({ error: message, isLoading: false });
      throw err;
    }
  },

  logout: async () => {
    const refresh = localStorage.getItem("refresh_token");
    try {
      if (refresh) {
        await logoutApi(refresh);
      }
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      set({
        user: null,
        company: null,
        isAuthenticated: false,
        error: null,
      });
    }
  },

  loadUser: async () => {
    if (!get().isAuthenticated) return;
    set({ isLoading: true });
    try {
      const user = await getMeApi();
      set({ user, company: user.company, isLoading: false });
    } catch {
      set({ isAuthenticated: false, isLoading: false });
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
  },

  clearError: () => set({ error: null }),
}));
