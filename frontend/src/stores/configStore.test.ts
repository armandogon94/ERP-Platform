import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "./configStore";

vi.mock("../api/config", () => ({
  fetchModuleConfigApi: vi.fn(),
  fetchModulesApi: vi.fn(),
}));

import { fetchModuleConfigApi, fetchModulesApi } from "../api/config";

const mockFetchModuleConfigApi = vi.mocked(fetchModuleConfigApi);
const mockFetchModulesApi = vi.mocked(fetchModulesApi);

const dentalInventoryConfig = {
  module: "inventory",
  industry: "dental",
  config: { modules: { inventory: { display_name: "Supplies" } } },
  terminology: { Warehouse: "Supply Room", Product: "Dental Supply" },
};

describe("configStore", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useConfigStore.setState({
      configs: {},
      terminology: {},
      modules: [],
      isLoading: false,
      error: null,
    });
  });

  it("starts with empty configs and terminology", () => {
    const state = useConfigStore.getState();
    expect(state.configs).toEqual({});
    expect(state.terminology).toEqual({});
    expect(state.modules).toEqual([]);
  });

  describe("fetchModuleConfig", () => {
    it("fetches and stores module config", async () => {
      mockFetchModuleConfigApi.mockResolvedValueOnce(dentalInventoryConfig);

      await useConfigStore.getState().fetchModuleConfig(1, "inventory");

      const state = useConfigStore.getState();
      expect(state.configs["inventory"]).toEqual(dentalInventoryConfig);
    });

    it("merges terminology into store", async () => {
      mockFetchModuleConfigApi.mockResolvedValueOnce(dentalInventoryConfig);

      await useConfigStore.getState().fetchModuleConfig(1, "inventory");

      const state = useConfigStore.getState();
      expect(state.terminology["Warehouse"]).toBe("Supply Room");
      expect(state.terminology["Product"]).toBe("Dental Supply");
    });

    it("does not re-fetch if already cached", async () => {
      mockFetchModuleConfigApi.mockResolvedValueOnce(dentalInventoryConfig);

      await useConfigStore.getState().fetchModuleConfig(1, "inventory");
      await useConfigStore.getState().fetchModuleConfig(1, "inventory");

      expect(mockFetchModuleConfigApi).toHaveBeenCalledTimes(1);
    });

    it("sets error on API failure", async () => {
      mockFetchModuleConfigApi.mockRejectedValueOnce(new Error("API Error"));

      await useConfigStore.getState().fetchModuleConfig(1, "inventory");

      expect(useConfigStore.getState().error).toBe("API Error");
    });

    it("sets isLoading during fetch", async () => {
      let resolvePromise!: (value: typeof dentalInventoryConfig) => void;
      mockFetchModuleConfigApi.mockReturnValueOnce(
        new Promise((res) => {
          resolvePromise = res;
        }),
      );

      const fetchPromise = useConfigStore.getState().fetchModuleConfig(1, "inventory");
      expect(useConfigStore.getState().isLoading).toBe(true);

      resolvePromise(dentalInventoryConfig);
      await fetchPromise;
      expect(useConfigStore.getState().isLoading).toBe(false);
    });
  });

  describe("fetchModules", () => {
    it("fetches and stores module list", async () => {
      const mockModules = [
        {
          id: 1,
          name: "inventory",
          display_name: "Supplies",
          icon: "medical",
          is_installed: true,
          is_visible: true,
          sequence: 1,
          color: "#059669",
        },
      ];
      mockFetchModulesApi.mockResolvedValueOnce(mockModules);

      await useConfigStore.getState().fetchModules();

      expect(useConfigStore.getState().modules).toEqual(mockModules);
    });

    it("sets error on fetch failure", async () => {
      mockFetchModulesApi.mockRejectedValueOnce(new Error("Network Error"));

      await useConfigStore.getState().fetchModules();

      expect(useConfigStore.getState().error).toBe("Network Error");
    });
  });

  describe("clearError", () => {
    it("clears the error state", () => {
      useConfigStore.setState({ error: "Some error" });
      useConfigStore.getState().clearError();
      expect(useConfigStore.getState().error).toBeNull();
    });
  });
});
