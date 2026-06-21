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
