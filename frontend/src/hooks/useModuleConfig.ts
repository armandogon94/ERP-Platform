import { useEffect } from "react";
import type { ModuleConfigResponse } from "../api/config";
import { useConfigStore } from "../stores/configStore";

interface UseModuleConfigResult {
  config: ModuleConfigResponse | null;
  isLoading: boolean;
  error: string | null;
  refetch: (moduleId: number, moduleName: string) => Promise<void>;
}

/**
 * Fetch and cache the resolved config for a module.
 * Returns the config from the store cache on subsequent calls.
 */
export function useModuleConfig(
  moduleId: number | null,
  moduleName: string,
): UseModuleConfigResult {
  const { configs, isLoading, error, fetchModuleConfig } = useConfigStore();

  useEffect(() => {
    if (moduleId !== null && !configs[moduleName]) {
      fetchModuleConfig(moduleId, moduleName);
    }
  }, [moduleId, moduleName, configs, fetchModuleConfig]);

  return {
    config: configs[moduleName] ?? null,
    isLoading,
    error,
    refetch: fetchModuleConfig,
  };
}
