import type { ActivityDay } from "@/lib/api/types";

/** UTC YYYY-MM-DD string for a Date. */
export function toISODate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

/** Date shifted by n whole days (DST-safe via UTC ms). */
export function shiftDays(d: Date, n: number): Date {
  return new Date(d.getTime() + n * 86_400_000);
}

/**
 * The last `n` calendar days ending on `today` (inclusive), ascending.
 * Missing dates are zero-filled so the result always has length `n`.
 */
export function lastNDays(
  days: ActivityDay[],
  n: number,
  today: Date = new Date(),
): ActivityDay[] {
  const byDate = new Map(days.map((d) => [d.date, d]));
  const out: ActivityDay[] = [];
  for (let i = n - 1; i >= 0; i--) {
    const date = toISODate(shiftDays(today, -i));
    out.push(byDate.get(date) ?? { date, count: 0, projects: "" });
  }
  return out;
}
