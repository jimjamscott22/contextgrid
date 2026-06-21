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

export interface HeatmapCell {
  date: string | null; // null = leading pad cell
  count: number;
  level: number; // 0-4
}

export interface HeatmapMonthLabel {
  label: string;
  column: number; // 0-based grid column
}

export interface HeatmapData {
  cells: HeatmapCell[];
  weeks: number;
  months: HeatmapMonthLabel[];
}

const MONTHS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

function bucket(count: number, max: number): number {
  if (count <= 0) return 0;
  const r = count / max;
  if (r <= 0.25) return 1;
  if (r <= 0.5) return 2;
  if (r <= 0.75) return 3;
  return 4;
}

/**
 * Cells ordered for a `grid-auto-flow: column`, 7-row grid (row 0 = Sunday).
 * Leading pad cells align the first real day to its weekday row.
 */
export function buildHeatmap(
  days: ActivityDay[],
  windowDays: number,
  today: Date = new Date(),
): HeatmapData {
  const byDate = new Map(days.map((d) => [d.date, d]));
  const start = shiftDays(today, -(windowDays - 1));
  const max = Math.max(1, ...days.map((d) => d.count));
  const cells: HeatmapCell[] = [];

  // Leading pads: weekday of the first real day (0 = Sunday).
  const leadingPads = new Date(`${toISODate(start)}T00:00:00Z`).getUTCDay();
  for (let i = 0; i < leadingPads; i++) {
    cells.push({ date: null, count: 0, level: 0 });
  }

  const months: HeatmapMonthLabel[] = [];
  let lastMonth = -1;
  for (let i = 0; i < windowDays; i++) {
    const d = shiftDays(start, i);
    const iso = toISODate(d);
    const count = byDate.get(iso)?.count ?? 0;
    const column = Math.floor(cells.length / 7);
    const month = d.getUTCMonth();
    if (month !== lastMonth) {
      months.push({ label: MONTHS[month], column });
      lastMonth = month;
    }
    cells.push({ date: iso, count, level: bucket(count, max) });
  }

  return { cells, weeks: Math.ceil(cells.length / 7), months };
}
