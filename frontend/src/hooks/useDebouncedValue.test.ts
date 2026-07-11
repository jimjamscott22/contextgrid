import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useDebouncedValue } from "./useDebouncedValue";

describe("useDebouncedValue", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it("returns the initial value immediately", () => {
    const { result } = renderHook(() => useDebouncedValue("abc", 200));
    expect(result.current).toBe("abc");
  });

  it("does not update until delay elapses", () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebouncedValue(value, 200),
      { initialProps: { value: "a" } }
    );
    rerender({ value: "ab" });
    rerender({ value: "abc" });
    expect(result.current).toBe("a");
    act(() => {
      vi.advanceTimersByTime(199);
    });
    expect(result.current).toBe("a");
    act(() => {
      vi.advanceTimersByTime(1);
    });
    expect(result.current).toBe("abc");
  });

  it("resets the timer on each change", () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebouncedValue(value, 200),
      { initialProps: { value: "" } }
    );
    rerender({ value: "c" });
    act(() => {
      vi.advanceTimersByTime(150);
    });
    rerender({ value: "co" });
    act(() => {
      vi.advanceTimersByTime(150);
    });
    expect(result.current).toBe("");
    act(() => {
      vi.advanceTimersByTime(50);
    });
    expect(result.current).toBe("co");
  });
});
