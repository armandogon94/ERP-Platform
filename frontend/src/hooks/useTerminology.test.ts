import { renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { useConfigStore } from "../stores/configStore";
import { useTerminology } from "./useTerminology";

describe("useTerminology", () => {
  beforeEach(() => {
    useConfigStore.setState({
      configs: {},
      terminology: {},
      modules: [],
      isLoading: false,
      error: null,
    });
  });

  it("returns the overridden term when terminology is loaded", () => {
    useConfigStore.setState({
      terminology: { Warehouse: "Supply Room", Product: "Dental Supply" },
    });
    const { result } = renderHook(() => useTerminology("Warehouse"));
    expect(result.current).toBe("Supply Room");
  });

  it("returns the key itself when no override exists", () => {
    useConfigStore.setState({ terminology: {} });
    const { result } = renderHook(() => useTerminology("Warehouse"));
    expect(result.current).toBe("Warehouse");
  });

  it("returns the provided fallback when no override exists", () => {
    useConfigStore.setState({ terminology: {} });
    const { result } = renderHook(() => useTerminology("UnknownKey", "Default Label"));
    expect(result.current).toBe("Default Label");
  });

  it("override wins over fallback", () => {
    useConfigStore.setState({ terminology: { Product: "Menu Item" } });
    const { result } = renderHook(() => useTerminology("Product", "Default"));
    expect(result.current).toBe("Menu Item");
  });

  it("returns key itself for unknown key with no fallback", () => {
    useConfigStore.setState({ terminology: {} });
    const { result } = renderHook(() => useTerminology("SomeLabel"));
    expect(result.current).toBe("SomeLabel");
  });
});
