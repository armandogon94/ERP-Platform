import { create } from "zustand";
import {
  type ModuleConfigResponse,
  type ModuleInfo,
  fetchModuleConfigApi,
  fetchModulesApi,
} from "../api/config";

interface ConfigState {
  /** Resolved config per module, keyed by module name */
  configs: Record<string, ModuleConfigResponse>;
  /** Global terminology map from the currently loaded company config */
  terminology: Record<string, string>;
  /** All installed modules for the current company */
  modules: ModuleInfo[];
  isLoading: boolean;
  error: string | null;

  fetchModuleConfig: (moduleId: number, moduleName: string) => Promise<void>;
  fetchModules: () => Promise<void>;
  clearError: () => void;
}

export const useConfigStore = create<ConfigState>((set, get) => ({
  configs: {},
  terminology: {},
  modules: [],
  isLoading: false,
  error: null,

  fetchModuleConfig: async (moduleId: number, moduleName: string) => {
    // Return early if already cached
    if (get().configs[moduleName]) return;

    set({ isLoading: true, error: null });
    try {
      const response = await fetchModuleConfigApi(moduleId);
      set((state) => ({
        configs: { ...state.configs, [moduleName]: response },
        // Merge terminology — later fetches can add new keys
        terminology: { ...state.terminology, ...response.terminology },
        isLoading: false,
      }));
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to load module config";
      set({ error: message, isLoading: false });
    }
  },

  fetchModules: async () => {
    set({ isLoading: true, error: null });
    try {
      const modules = await fetchModulesApi();
      set({ modules, isLoading: false });
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to load modules";
      set({ error: message, isLoading: false });
    }
  },

  clearError: () => set({ error: null }),
}));
