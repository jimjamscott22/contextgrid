# Activity Card Enrichment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Home "Activity" card's existing heatmap legible and add a 7-day sparkline plus a "most active project" line, entirely client-side.

**Architecture:** Pure, unit-tested helpers in `frontend/src/lib/activity.ts` compute everything from the existing `/api/activity/heatmap` payload. Presentational components (`HeatmapGrid`, `Sparkline`) render the results, and a new `ActivityCard` owns the card JSX, leaving `Home.tsx` thin. No backend changes.

**Tech Stack:** React 18 + TypeScript, Tailwind (CSS vars `--cg-*`), TanStack Query, Vitest (new dev dependency).

## Global Constraints

- Frontend-only change. No edits under `api/`, `src/`, or `web/`.
- TypeScript strict mode is on (`tsconfig.app.json`); all code must type-check via `npm run lint` (`tsc -b --noEmit`).
- Use the `@/` path alias for intra-`src` imports (configured in `vite.config.ts` and `tsconfig.app.json`).
- Use existing primitives: `Card`/`CardContent`/`CardHeader`/`CardTitle` from `@/components/ui/Card`, `cn` from `@/lib/cn`.
- Colors must use existing CSS vars: `var(--cg-fg)`, `var(--cg-primary)`, `var(--cg-surface-alt)`, `var(--cg-border)`.
- "Most active project" ranks by frequency of appearance, not activity volume — counts are not attributed per project in the payload. Document this in code.
- Helper functions must accept an injectable `today: Date` (default `new Date()`) so tests are deterministic. All date math uses UTC.

**Reference types** (already defined in `frontend/src/lib/api/types.ts`, do not redefine):

```ts
interface ActivityDay { date: string; count: number; projects: string; }
interface ActivityStreak { current_streak: number; longest_streak: number; }
interface ActivityHeatmap { days: ActivityDay[]; streak: ActivityStreak; }
```

---

### Task 1: Add Vitest

**Files:**
- Modify: `frontend/package.json` (devDependencies + scripts)
- Create: `frontend/src/lib/activity.test.ts` (smoke test only, expanded in later tasks)

**Interfaces:**
- Consumes: nothing
- Produces: a working `npm test` command (`vitest run`) that picks up `*.test.ts` under `frontend/src/` and resolves the `@/` alias via `vite.config.ts`.

- [ ] **Step 1: Install Vitest**

Run from `frontend/`:
```bash
npm install -D vitest@^2.1.0
```

- [ ] **Step 2: Add test scripts**

In `frontend/package.json`, add to `"scripts"` (after the `"lint"` line):
```json
    "test": "vitest run",
    "test:watch": "vitest"
```

- [ ] **Step 3: Write a smoke test**

Create `frontend/src/lib/activity.test.ts`:
```ts
import { describe, it, expect } from "vitest";

describe("vitest setup", () => {
  it("runs", () => {
    expect(1 + 1).toBe(2);
  });
});
```

- [ ] **Step 4: Run the test to verify the runner works**

Run from `frontend/`: `npm test`
Expected: PASS — 1 passed. Vitest auto-loads `vite.config.ts`; no extra config needed.

- [ ] **Step 5: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/src/lib/activity.test.ts
git commit -m "test: add Vitest to frontend"
```

---

### Task 2: `lastNDays` helper

**Files:**
- Create: `frontend/src/lib/activity.ts`
- Test: `frontend/src/lib/activity.test.ts` (replace smoke test)

**Interfaces:**
- Consumes: `ActivityDay` from `@/lib/api/types`.
- Produces:
  - `toISODate(d: Date): string` — UTC `YYYY-MM-DD`.
  - `shiftDays(d: Date, n: number): Date` — DST-safe (UTC ms arithmetic).
  - `lastNDays(days: ActivityDay[], n: number, today?: Date): ActivityDay[]` — exactly `n` entries ending on `today`, ascending, zero-filled (`count: 0, projects: ""`) for missing dates.

- [ ] **Step 1: Write the failing test**

Replace the contents of `frontend/src/lib/activity.test.ts`:
```ts
import { describe, it, expect } from "vitest";
import { lastNDays, toISODate, shiftDays } from "@/lib/activity";
import type { ActivityDay } from "@/lib/api/types";

const today = new Date(Date.UTC(2026, 5, 21)); // 2026-06-21

describe("toISODate / shiftDays", () => {
  it("formats UTC dates", () => {
    expect(toISODate(today)).toBe("2026-06-21");
  });
  it("shifts by whole days", () => {
    expect(toISODate(shiftDays(today, -2))).toBe("2026-06-19");
  });
});

describe("lastNDays", () => {
  it("returns exactly n ascending days ending today, zero-filled", () => {
    const input: ActivityDay[] = [
      { date: "2026-06-20", count: 3, projects: "A" },
      { date: "2026-06-18", count: 1, projects: "B" },
      { date: "2026-01-01", count: 9, projects: "C" }, // outside window
    ];
    const out = lastNDays(input, 7, today);
    expect(out).toHaveLength(7);
    expect(out[0].date).toBe("2026-06-15");
    expect(out[6].date).toBe("2026-06-21");
    expect(out[6].count).toBe(0); // today, no data
    expect(out[5].count).toBe(3); // 2026-06-20
    expect(out[3].count).toBe(1); // 2026-06-18
    expect(out[4].count).toBe(0); // 2026-06-19 gap
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run from `frontend/`: `npm test`
Expected: FAIL — cannot resolve `@/lib/activity`.

- [ ] **Step 3: Write minimal implementation**

Create `frontend/src/lib/activity.ts`:
```ts
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
```

- [ ] **Step 4: Run test to verify it passes**

Run from `frontend/`: `npm test`
Expected: PASS — all tests green.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/lib/activity.ts frontend/src/lib/activity.test.ts
git commit -m "feat: add lastNDays activity helper"
```

---

### Task 3: `mostActiveProject` helper

**Files:**
- Modify: `frontend/src/lib/activity.ts`
- Test: `frontend/src/lib/activity.test.ts`

**Interfaces:**
- Consumes: `ActivityDay`.
- Produces: `mostActiveProject(days: ActivityDay[]): string | null` — top project by number of days it appears in (`projects` split on `", "`); ties broken alphabetically; `null` when no project appears.

- [ ] **Step 1: Write the failing test**

Append to `frontend/src/lib/activity.test.ts`:
```ts
import { mostActiveProject } from "@/lib/activity";

describe("mostActiveProject", () => {
  it("returns the most frequently appearing project", () => {
    const input: ActivityDay[] = [
      { date: "2026-06-20", count: 2, projects: "Alpha, Beta" },
      { date: "2026-06-19", count: 1, projects: "Alpha" },
      { date: "2026-06-18", count: 1, projects: "Beta" },
    ];
    expect(mostActiveProject(input)).toBe("Alpha"); // 2 appearances vs 2... tie -> alpha
  });
  it("breaks ties alphabetically", () => {
    const input: ActivityDay[] = [
      { date: "2026-06-20", count: 1, projects: "Zeta" },
      { date: "2026-06-19", count: 1, projects: "Alpha" },
    ];
    expect(mostActiveProject(input)).toBe("Alpha");
  });
  it("returns null when there is no activity", () => {
    expect(mostActiveProject([{ date: "2026-06-20", count: 0, projects: "" }])).toBeNull();
    expect(mostActiveProject([])).toBeNull();
  });
});
```

Note: in the first case Alpha and Beta both appear twice, so the alphabetical tie-break selects Alpha.

- [ ] **Step 2: Run test to verify it fails**

Run from `frontend/`: `npm test`
Expected: FAIL — `mostActiveProject` is not exported.

- [ ] **Step 3: Write minimal implementation**

Append to `frontend/src/lib/activity.ts`:
```ts
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
```

- [ ] **Step 4: Run test to verify it passes**

Run from `frontend/`: `npm test`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/lib/activity.ts frontend/src/lib/activity.test.ts
git commit -m "feat: add mostActiveProject activity helper"
```

---

### Task 4: `buildHeatmap` helper

**Files:**
- Modify: `frontend/src/lib/activity.ts`
- Test: `frontend/src/lib/activity.test.ts`

**Interfaces:**
- Consumes: `ActivityDay`, `toISODate`, `shiftDays`.
- Produces:
  - `interface HeatmapCell { date: string | null; count: number; level: number; }` — `date: null` marks a leading pad cell; `level` is 0–4.
  - `interface HeatmapMonthLabel { label: string; column: number; }` — `label` is `"Jan"` etc; `column` is the 0-based grid column where that month's first cell sits.
  - `interface HeatmapData { cells: HeatmapCell[]; weeks: number; months: HeatmapMonthLabel[]; }`
  - `buildHeatmap(days: ActivityDay[], windowDays: number, today?: Date): HeatmapData` — windowed cells ordered for a `grid-auto-flow: column`, 7-row grid (row 0 = Sunday). Leading pad cells (date `null`, count 0, level 0) align the first real day to its weekday row. `level` buckets non-zero counts into 1–4 by `count / max` quartiles (max over real days, floored at 1); 0 stays level 0.

- [ ] **Step 1: Write the failing test**

Append to `frontend/src/lib/activity.test.ts`:
```ts
import { buildHeatmap } from "@/lib/activity";

describe("buildHeatmap", () => {
  // today = 2026-06-21 is a Sunday (getUTCDay() === 0).
  it("pads the start to align the first day to its weekday row", () => {
    // window of 8 days: 2026-06-14 (Sun) .. 2026-06-21 (Sun)
    const out = buildHeatmap([], 8, today);
    // 2026-06-14 is a Sunday -> 0 leading pads
    expect(out.cells.filter((c) => c.date === null)).toHaveLength(0);
    expect(out.cells[0].date).toBe("2026-06-14");
  });

  it("adds leading pads when the window does not start on Sunday", () => {
    // window of 5 days: 2026-06-17 (Wed=3) .. 2026-06-21 (Sun)
    const out = buildHeatmap([], 5, today);
    const pads = out.cells.filter((c) => c.date === null);
    expect(pads).toHaveLength(3); // Sun,Mon,Tue placeholders before Wed
    expect(out.cells[3].date).toBe("2026-06-17");
  });

  it("buckets counts into levels 1-4 and 0 for empty", () => {
    const input: ActivityDay[] = [
      { date: "2026-06-21", count: 8, projects: "A" }, // max -> level 4
      { date: "2026-06-20", count: 2, projects: "A" }, // 2/8=0.25 -> level 1
      { date: "2026-06-19", count: 4, projects: "A" }, // 4/8=0.5 -> level 2
      { date: "2026-06-18", count: 6, projects: "A" }, // 6/8=0.75 -> level 3
    ];
    const out = buildHeatmap(input, 4, today); // Thu..Sun, 4 leading pads (Thu=4)
    const byDate = (d: string) => out.cells.find((c) => c.date === d)!;
    expect(byDate("2026-06-21").level).toBe(4);
    expect(byDate("2026-06-20").level).toBe(1);
    expect(byDate("2026-06-19").level).toBe(2);
    expect(byDate("2026-06-18").level).toBe(3);
  });

  it("reports the number of week columns and month labels", () => {
    const out = buildHeatmap([], 8, today);
    expect(out.weeks).toBe(2); // 8 days span 2 Sunday-started columns
    expect(out.months[0]).toEqual({ label: "Jun", column: 0 });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run from `frontend/`: `npm test`
Expected: FAIL — `buildHeatmap` is not exported.

- [ ] **Step 3: Write minimal implementation**

Append to `frontend/src/lib/activity.ts`:
```ts
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
```

- [ ] **Step 4: Run test to verify it passes**

Run from `frontend/`: `npm test`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/lib/activity.ts frontend/src/lib/activity.test.ts
git commit -m "feat: add buildHeatmap activity helper"
```

---

### Task 5: `Sparkline` component

**Files:**
- Create: `frontend/src/components/activity/Sparkline.tsx`

**Interfaces:**
- Consumes: `ActivityDay` from `@/lib/api/types`.
- Produces: `export function Sparkline({ days }: { days: ActivityDay[] }): JSX.Element` — a row of mini-bars, one per element of `days`, bar height normalized to the max count in `days`, each with a `title` of `"<date>: <count> activity"`.

- [ ] **Step 1: Create the component**

Create `frontend/src/components/activity/Sparkline.tsx`:
```tsx
import type { ActivityDay } from "@/lib/api/types";

/** Compact bar chart of recent daily activity counts. */
export function Sparkline({ days }: { days: ActivityDay[] }) {
  const max = Math.max(1, ...days.map((d) => d.count));
  return (
    <div className="flex h-8 items-end gap-[3px]">
      {days.map((d) => {
        const pct = d.count === 0 ? 0 : Math.max(12, (d.count / max) * 100);
        return (
          <div
            key={d.date}
            title={`${d.date}: ${d.count} activity`}
            className="flex-1 rounded-[2px]"
            style={{
              height: `${pct}%`,
              minHeight: 2,
              backgroundColor:
                d.count === 0
                  ? "rgba(var(--cg-fg), 0.10)"
                  : "rgb(var(--cg-primary))",
            }}
          />
        );
      })}
    </div>
  );
}
```

- [ ] **Step 2: Verify it type-checks**

Run from `frontend/`: `npm run lint`
Expected: PASS — no type errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/activity/Sparkline.tsx
git commit -m "feat: add Sparkline component"
```

---

### Task 6: Rewrite `HeatmapGrid` for legibility

**Files:**
- Create: `frontend/src/components/activity/HeatmapGrid.tsx`

**Interfaces:**
- Consumes: `buildHeatmap`, `HeatmapCell` from `@/lib/activity`; `ActivityDay` from `@/lib/api/types`.
- Produces: `export function HeatmapGrid({ days }: { days: ActivityDay[] }): JSX.Element` — month labels, a 7-row week-column grid using discrete level colors, and a Less→More legend.

- [ ] **Step 1: Create the component**

Create `frontend/src/components/activity/HeatmapGrid.tsx`:
```tsx
import { buildHeatmap, type HeatmapCell } from "@/lib/activity";
import type { ActivityDay } from "@/lib/api/types";

const WINDOW_DAYS = 182; // ~6 months

// Discrete swatches keyed by level (0 = empty real day, 1-4 = activity).
const LEVEL_COLORS: Record<number, string> = {
  0: "rgba(var(--cg-fg), 0.07)",
  1: "rgba(var(--cg-primary), 0.30)",
  2: "rgba(var(--cg-primary), 0.50)",
  3: "rgba(var(--cg-primary), 0.72)",
  4: "rgb(var(--cg-primary))",
};

function cellColor(cell: HeatmapCell): string {
  if (cell.date === null) return "transparent"; // leading pad
  return LEVEL_COLORS[cell.level];
}

/** GitHub-style activity heatmap, ~6 months, week-per-column. */
export function HeatmapGrid({ days }: { days: ActivityDay[] }) {
  const { cells, weeks, months } = buildHeatmap(days, WINDOW_DAYS);
  const columns = `repeat(${weeks}, minmax(0, 1fr))`;

  return (
    <div>
      {/* Month labels aligned to their starting column. */}
      <div className="mb-1 grid text-[10px] text-fg-soft" style={{ gridTemplateColumns: columns }}>
        {months.map((m) => (
          <span key={`${m.label}-${m.column}`} style={{ gridColumnStart: m.column + 1 }}>
            {m.label}
          </span>
        ))}
      </div>

      {/* 7-row, week-per-column grid. */}
      <div
        className="grid grid-flow-col gap-[2px]"
        style={{ gridTemplateRows: "repeat(7, minmax(0, 1fr))", gridTemplateColumns: columns }}
      >
        {cells.map((cell, i) => (
          <div
            key={cell.date ?? `pad-${i}`}
            title={cell.date ? `${cell.date}: ${cell.count} activity` : undefined}
            className="aspect-square rounded-[2px]"
            style={{ backgroundColor: cellColor(cell) }}
          />
        ))}
      </div>

      {/* Legend. */}
      <div className="mt-2 flex items-center gap-1 text-[10px] text-fg-soft">
        <span>Less</span>
        {[0, 1, 2, 3, 4].map((lvl) => (
          <span
            key={lvl}
            className="h-2.5 w-2.5 rounded-[2px]"
            style={{ backgroundColor: LEVEL_COLORS[lvl] }}
          />
        ))}
        <span>More</span>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify it type-checks**

Run from `frontend/`: `npm run lint`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/activity/HeatmapGrid.tsx
git commit -m "feat: rewrite HeatmapGrid for legibility"
```

---

### Task 7: `ActivityCard` component + wire into Home

**Files:**
- Create: `frontend/src/components/activity/ActivityCard.tsx`
- Modify: `frontend/src/routes/Home.tsx` (remove inline `HeatmapGrid` + inline Activity card JSX; render `<ActivityCard>`)

**Interfaces:**
- Consumes: `HeatmapGrid`, `Sparkline`, `lastNDays`, `mostActiveProject`; `ActivityHeatmap` from `@/lib/api/types`; `Card`/`CardContent`/`CardHeader`/`CardTitle` from `@/components/ui/Card`.
- Produces: `export function ActivityCard({ data }: { data?: ActivityHeatmap }): JSX.Element`.

- [ ] **Step 1: Create the component**

Create `frontend/src/components/activity/ActivityCard.tsx`:
```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { HeatmapGrid } from "@/components/activity/HeatmapGrid";
import { Sparkline } from "@/components/activity/Sparkline";
import { lastNDays, mostActiveProject } from "@/lib/activity";
import type { ActivityHeatmap } from "@/lib/api/types";

/** Home overview "Activity" card: heatmap, 7-day sparkline, streaks, top project. */
export function ActivityCard({ data }: { data?: ActivityHeatmap }) {
  const days = data?.days ?? [];
  const streak = data?.streak;
  const week = lastNDays(days, 7);
  const topProject = mostActiveProject(days);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-3 text-xs text-fg-soft">Last ~6 months</div>
        {data && <HeatmapGrid days={days} />}

        <div className="mt-4 border-t border-border pt-3">
          <div className="mb-1 text-xs text-fg-soft">Last 7 days</div>
          <Sparkline days={week} />
        </div>

        <div className="mt-4 flex items-center justify-between border-t border-border pt-3 text-sm">
          <div>
            <div className="text-xs text-fg-soft">Current</div>
            <div className="font-semibold">{streak?.current_streak ?? 0} days</div>
          </div>
          <div>
            <div className="text-xs text-fg-soft">Longest</div>
            <div className="font-semibold">{streak?.longest_streak ?? 0} days</div>
          </div>
        </div>

        {topProject && (
          <div className="mt-3 truncate text-xs text-fg-soft">
            Most active · <span className="font-medium text-fg">{topProject}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 2: Remove the old inline implementation from Home.tsx**

In `frontend/src/routes/Home.tsx`:

Delete the `HeatmapGrid` function (lines 12-38) and its now-unused import of `ActivityDay`.

Replace the entire inline Activity `<Card>...</Card>` block (currently lines 136-154) with:
```tsx
        <ActivityCard data={heatQ.data} />
```

Add the import near the other component imports (after the `LoadingState`/`ErrorState` import line):
```tsx
import { ActivityCard } from "@/components/activity/ActivityCard";
```

Remove the now-unused `import type { ActivityDay } from "@/lib/api/types";` line.

Keep the `heatQ` query and the `streak`/`StatCard` usage at the top untouched — the "Current streak" StatCard still uses `streak?.current_streak`.

- [ ] **Step 3: Verify it type-checks**

Run from `frontend/`: `npm run lint`
Expected: PASS — no unused-import or type errors. (If `tsc` flags `streak` as unused, confirm the `StatCard` at line ~85 still references it; it should.)

- [ ] **Step 4: Run the full test suite**

Run from `frontend/`: `npm test`
Expected: PASS — all activity helper tests still green.

- [ ] **Step 5: Manual smoke check**

Run the API server (`bash start.sh`) and `cd frontend && npm run dev`, open the overview. Confirm: the heatmap is visibly a grid of squares (empty days faintly visible, active days in primary color), month labels appear, the Less→More legend renders, the 7-day sparkline shows, and "Most active · <project>" appears when there is activity.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/activity/ActivityCard.tsx frontend/src/routes/Home.tsx
git commit -m "feat: enrich Activity card with sparkline and top project"
```

---

## Self-Review Notes

- **Spec coverage:** heatmap legibility (Task 6), week-column layout + month labels + legend (Tasks 4, 6), discrete buckets (Task 4), 7-day sparkline (Tasks 2, 5, 7), most active project (Tasks 3, 7), `lib/activity.ts` extraction + tests (Tasks 1-4), `ActivityCard` extraction (Task 7), Vitest decision (Task 1). No backend changes — all data from the existing payload. All spec sections map to a task.
- **Type consistency:** `lastNDays`, `mostActiveProject`, `buildHeatmap`, `HeatmapCell`, `HeatmapData` names are identical across producer and consumer tasks. `ActivityDay`/`ActivityHeatmap` come from existing `types.ts`.
- **No placeholders:** every code step contains complete code; every run step has an exact command and expected result.
