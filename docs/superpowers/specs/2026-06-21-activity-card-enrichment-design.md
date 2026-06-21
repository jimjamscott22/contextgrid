# Activity Card Enrichment — Design

**Date:** 2026-06-21
**Status:** Approved
**Area:** `frontend/` (React SPA) — Home overview page

## Problem

The "Activity" card on the Home overview ([frontend/src/routes/Home.tsx](../../../frontend/src/routes/Home.tsx)) already renders an
activity heatmap fed by `GET /api/activity/heatmap`, plus current/longest streak
counters. But in practice the card reads as empty:

- Zero-activity days render as `rgb(var(--cg-surface-alt))`, a dark square that
  blends into the card background in dark themes. With sparse activity, nearly
  every cell is a zero-day, so the grid looks like a blank block.
- The grid uses default row-flow, so days do not stack vertically by week the way
  a GitHub-style heatmap does.
- The card has unused vertical space and only two stats.

## Goal

Make the existing heatmap legible **and** add new supporting stats — all
computed client-side from the existing payload. **No backend changes.**

## Constraints

- No backend/API changes. The `/api/activity/heatmap` payload already contains
  everything needed: per-day `{ date, count, projects }` for the last 365 days,
  and `streak: { current_streak, longest_streak }`. The frontend already fetches
  the full window.
- Follow existing frontend patterns (Tailwind, CSS vars `--cg-*`, TanStack Query,
  the `Card`/`CardContent` primitives).
- Python style rules do not apply (frontend-only change).

## Scope

In scope:
1. Heatmap legibility fixes.
2. A 7-day activity sparkline.
3. A "most active project" line.
4. Extract activity math into a testable module and the card into its own component.

Out of scope (YAGNI): per-project activity attribution, configurable date ranges,
backend changes, anything on the Analytics page.

## Design

### Data (unchanged)

```ts
interface ActivityDay { date: string; count: number; projects: string; }
interface ActivityStreak { current_streak: number; longest_streak: number; }
interface ActivityHeatmap { days: ActivityDay[]; streak: ActivityStreak; }
```

`projects` is a comma-separated list of project names active that day. Per-day
`count` is **not** attributed per project — only presence is known.

### 1. Heatmap legibility (`HeatmapGrid`)

- **Week-column layout:** `grid-auto-flow: column` with 7 fixed rows. Each column
  is one week; days stack vertically Sun→Sat. Pad leading empty cells so the first
  real day lands on its correct weekday row.
- **Contrast via discrete buckets:** replace the continuous opacity ramp with 5
  levels — empty + 4 intensities. Empty days get a visible muted fill
  (`rgba(var(--cg-fg), 0.07)`) instead of near-invisible `surface-alt`. Non-empty
  buckets use `rgba(var(--cg-primary), α)` at increasing α.
- **Month labels** along the top of the grid.
- **Legend:** `Less ▢▢▢▢ More` row beneath the grid using the same 5 swatches.

Bucketing: given `max = Math.max(1, ...counts)`, map a non-zero `count` into one of
4 buckets by `ratio = count / max` (e.g. quartiles). Zero maps to the empty swatch.

### 2. 7-day sparkline (`Sparkline`)

- Compact row of 7 mini-bars from the last 7 days' counts, normalized to the
  7-day max. Labeled "Last 7 days". Each bar has a `title` of `date: N activity`.
- Pure presentational component; receives an array of `{ date, count }`.

### 3. Most active project

- Count each project name's appearances across the windowed days (split each day's
  `projects` on `, `, tally). Show the top one as `Most active · <name>`.
- If there is no activity, render nothing (or a muted "—").
- Caveat documented in code: ranks by frequency of appearance, not exact volume.

### 4. Code structure

New module `frontend/src/lib/activity.ts` — pure, unit-testable functions:

- `lastNDays(days: ActivityDay[], n: number): ActivityDay[]` — last `n` calendar
  days ending today, zero-filled for missing dates.
- `mostActiveProject(days: ActivityDay[]): string | null` — top project by
  appearance count, `null` when none.
- `buildHeatmapWeeks(days: ActivityDay[], windowDays: number)` — returns the
  windowed cells plus the count of leading pad cells needed for weekday alignment,
  and the per-cell bucket level (0–4).

New/changed components in `frontend/src/`:

- `ActivityCard` — owns the card JSX (extracted from `Home.tsx`), consumes the
  heatmap query result. Keeps `Home.tsx` focused.
- `HeatmapGrid` — updated per §1.
- `Sparkline` — new per §2.

`Home.tsx` renders `<ActivityCard data={heatQ.data} />` in place of the inline JSX.

### Resulting layout

```
Activity
Last ~6 months
 J  F  M  A  M  J          ← month labels
▣▢▣▢▢▣▢ ...                ← 7-row week-column grid
Less ▢▢▣▣ More
──────────────────────────
Last 7 days   ▁▃▂▅▁▂▆
──────────────────────────
Current  1 day    Longest  4 days
Most active · ChatArchive
```

## Testing

The `lib/activity.ts` functions are pure and the natural test surface:

- `lastNDays` — correct length, zero-fill for gaps, ends on today, ordering.
- `mostActiveProject` — tie-breaking, empty input → `null`, comma parsing.
- `buildHeatmapWeeks` — leading pad count for a known start weekday, bucket
  boundaries (0 → empty, max → top bucket), window slicing.

Note: the repo's existing tests are shell-based and there is no JS test runner
configured. The implementation plan must decide whether to add a lightweight
runner (e.g. Vitest) for these pure functions or defer test wiring; this is called
out as an open decision for the plan, not the spec.

## Risks / Notes

- Weekday alignment math is the most error-prone part — drive it with tests.
- "Most active project" can mislead (appearance, not volume); caveat in code.
- No backend change keeps the blast radius to `frontend/src/`.
