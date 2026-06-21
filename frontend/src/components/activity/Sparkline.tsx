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
