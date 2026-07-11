import { useEffect, useState } from "react";

/**
 * Return `value` delayed by `delayMs` milliseconds.
 * Updates reset the timer so rapid changes only emit the latest value.
 */
export function useDebouncedValue<T>(value: T, delayMs: number = 200): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const id = window.setTimeout(() => setDebounced(value), delayMs);
    return () => window.clearTimeout(id);
  }, [value, delayMs]);

  return debounced;
}
