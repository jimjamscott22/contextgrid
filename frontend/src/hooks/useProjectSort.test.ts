import { act, cleanup, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useProjectSort } from "./useProjectSort";

const storageKey = "cg-project-sort";

beforeEach(() => localStorage.clear());
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("useProjectSort", () => {
  it("defaults to the custom order, which fetches by recent activity", () => {
    const { result } = renderHook(() => useProjectSort());
    expect(result.current.field).toBe("custom");
    expect(result.current.isCustom).toBe(true);
    expect(result.current.query).toEqual({ sort: "recent", sort_order: "desc" });
  });

  it("uses each field's natural direction and maps it to the API query", () => {
    const { result } = renderHook(() => useProjectSort());
    act(() => result.current.setField("name"));
    expect(result.current.query).toEqual({ sort: "name", sort_order: "asc" });
    act(() => result.current.setField("created"));
    expect(result.current.query).toEqual({ sort: "created", sort_order: "desc" });
    expect(result.current.isCustom).toBe(false);
  });

  it("toggles direction and restores the choice on remount", () => {
    const { result, unmount } = renderHook(() => useProjectSort());
    act(() => result.current.setField("status"));
    act(() => result.current.toggleDirection());
    expect(result.current.direction).toBe("desc");
    expect(JSON.parse(localStorage.getItem(storageKey)!)).toEqual({
      field: "status",
      direction: "desc",
    });
    unmount();

    const restored = renderHook(() => useProjectSort());
    expect(restored.result.current.query).toEqual({ sort: "status", sort_order: "desc" });
  });

  it("resets direction to the field default when the field changes", () => {
    const { result } = renderHook(() => useProjectSort());
    act(() => result.current.setField("name"));
    act(() => result.current.toggleDirection());
    act(() => result.current.setField("recent"));
    expect(result.current.direction).toBe("desc");
  });

  it.each([
    "broken JSON",
    "null",
    "[]",
    '{"field":"bogus","direction":"asc"}',
    '{"field":"name","direction":"sideways"}',
    '{"field":"name"}',
  ])("falls back to the custom order for invalid storage: %s", (value) => {
    localStorage.setItem(storageKey, value);
    const { result } = renderHook(() => useProjectSort());
    expect(result.current.field).toBe("custom");
    expect(result.current.isCustom).toBe(true);
  });

  it("keeps working in memory when storage is unavailable", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("Storage blocked");
    });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("Storage blocked");
    });
    const { result } = renderHook(() => useProjectSort());
    act(() => result.current.setField("name"));
    expect(result.current.query).toEqual({ sort: "name", sort_order: "asc" });
  });
});
