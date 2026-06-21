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

/**
 * Top project by number of days it appears in `projects`.
 * NOTE: ranks by frequency of appearance, not activity volume — the payload
 * does not attribute per-day counts to individual projects. Ties break
 * alphabetically. Returns null when no project appears.
 */
export function mostActiveProject(days: ActivityDay[]): string | null {
  const tally = new Map<string, number>();
  for (const d of days) {
    if (!d.projects) continue;
    for (const name of d.projects.split(", ")) {
      const key = name.trim();
      if (!key) continue;
      tally.set(key, (tally.get(key) ?? 0) + 1);
    }
  }
  if (tally.size === 0) return null;
  return [...tally.entries()].sort(
    (a, b) => b[1] - a[1] || a[0].localeCompare(b[0]),
  )[0][0];
}
