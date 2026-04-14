import { useConfigStore } from "../stores/configStore";

/**
 * Return the industry-specific term for a generic label.
 *
 * @param key      The generic label, e.g. "Warehouse"
 * @param fallback Optional fallback. Defaults to the key itself.
 *
 * Examples:
 *   useTerminology("Warehouse")           → "Supply Room"  (for dental)
 *   useTerminology("UnknownKey")          → "UnknownKey"
 *   useTerminology("UnknownKey", "Default") → "Default"
 */
export function useTerminology(key: string, fallback?: string): string {
  const terminology = useConfigStore((state) => state.terminology);
  return terminology[key] ?? fallback ?? key;
}
