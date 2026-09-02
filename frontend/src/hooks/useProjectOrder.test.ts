import { act, cleanup, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { Project } from "@/lib/api/types";
import { useProjectOrder } from "./useProjectOrder";

const storageKey = "cg-project-order";
const projects = (ids: number[]) => ids.map((id) => ({ id }) as Project);
const ids = (list: Project[]) => list.map((p) => p.id);

beforeEach(() => localStorage.clear());
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("useProjectOrder", () => {
  it("follows recent activity until the first move, then restores the order on remount", () => {
    const { result, rerender, unmount } = renderHook(
      ({ list }) => useProjectOrder(list),
      { initialProps: { list: projects([1, 2, 3]) } },
    );
    rerender({ list: projects([3, 1, 2]) });
    expect(ids(result.current.orderedProjects)).toEqual([3, 1, 2]);
    expect(result.current.hasCustomOrder).toBe(false);
    act(() => result.current.moveProject(2, 3));
    expect(ids(result.current.orderedProjects)).toEqual([2, 3, 1]);
    expect(JSON.parse(localStorage.getItem(storageKey)!)).toEqual([2, 3, 1]);
    unmount();

    const restored = renderHook(() => useProjectOrder(projects([1, 2, 3])));
    expect(ids(restored.result.current.orderedProjects)).toEqual([2, 3, 1]);
  });

  it("reorders filtered cards without moving or forgetting hidden cards", () => {
    localStorage.setItem(storageKey, JSON.stringify([1, 2, 3, 4]));
    const { result, rerender } = renderHook(
      ({ list }) => useProjectOrder(list),
      { initialProps: { list: projects([4, 2]) } },
    );
    expect(ids(result.current.orderedProjects)).toEqual([2, 4]);
    act(() => result.current.moveProject(4, 2));
    expect(ids(result.current.orderedProjects)).toEqual([4, 2]);
    rerender({ list: [] });
    expect(result.current.orderedProjects).toEqual([]);
    rerender({ list: projects([4, 3, 2, 1]) });
    expect(ids(result.current.orderedProjects)).toEqual([1, 4, 3, 2]);
  });

  it("appends new projects and keeps their positions through subsequent refreshes", () => {
    localStorage.setItem(storageKey, JSON.stringify([2, 1]));
    const { result, rerender } = renderHook(
      ({ list }) => useProjectOrder(list),
      { initialProps: { list: projects([3, 1, 2]) } },
    );
    expect(ids(result.current.orderedProjects)).toEqual([2, 1, 3]);
    rerender({ list: projects([4, 3, 2, 1]) });
    expect(ids(result.current.orderedProjects)).toEqual([2, 1, 3, 4]);
    expect(JSON.parse(localStorage.getItem(storageKey)!)).toEqual([2, 1, 3, 4]);
  });

  it("ignores removed projects and resets to current recent-activity order", () => {
    localStorage.setItem(storageKey, JSON.stringify([3, 2, 1]));
    const { result, rerender } = renderHook(
      ({ list }) => useProjectOrder(list),
      { initialProps: { list: projects([1, 3]) } },
    );
    expect(ids(result.current.orderedProjects)).toEqual([3, 1]);
    act(() => result.current.resetOrder());
    expect(ids(result.current.orderedProjects)).toEqual([1, 3]);
    expect(localStorage.getItem(storageKey)).toBeNull();
    rerender({ list: projects([3, 1]) });
    expect(ids(result.current.orderedProjects)).toEqual([3, 1]);
    expect(result.current.hasCustomOrder).toBe(false);
  });

  it.each(["broken JSON", "{}", '[1,"2"]', "[-1,2]", "[]"])(
    "falls back to recent activity for invalid storage: %s",
    (value) => {
      localStorage.setItem(storageKey, value);
      const { result } = renderHook(() => useProjectOrder(projects([2, 1])));
      expect(ids(result.current.orderedProjects)).toEqual([2, 1]);
      expect(result.current.hasCustomOrder).toBe(false);
    },
  );

  it("deduplicates saved IDs", () => {
    localStorage.setItem(storageKey, "[2,2,1]");
    const { result } = renderHook(() => useProjectOrder(projects([1, 2])));
    expect(ids(result.current.orderedProjects)).toEqual([2, 1]);
    expect(JSON.parse(localStorage.getItem(storageKey)!)).toEqual([2, 1]);
  });

  it("ignores cancelled, unchanged, or stale moves", () => {
    const { result } = renderHook(() => useProjectOrder(projects([1, 2])));
    act(() => {
      result.current.moveProject(1, 1);
      result.current.moveProject(99, 1);
      result.current.moveProject(1, 99);
    });
    expect(result.current.hasCustomOrder).toBe(false);
    expect(localStorage.getItem(storageKey)).toBeNull();
  });

  it("keeps working in memory and reports unavailable storage", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("Storage blocked");
    });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("Storage blocked");
    });
    const { result } = renderHook(() => useProjectOrder(projects([1, 2])));
    act(() => result.current.moveProject(2, 1));
    expect(ids(result.current.orderedProjects)).toEqual([2, 1]);
    expect(result.current.storageError).toBe(true);
  });
});
