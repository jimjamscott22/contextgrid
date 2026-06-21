import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { HeatmapGrid } from "@/components/activity/HeatmapGrid";
import { Sparkline } from "@/components/activity/Sparkline";
import { lastNDays, mostActiveProject, resolveToday } from "@/lib/activity";
import type { ActivityHeatmap } from "@/lib/api/types";

/** Home overview "Activity" card: heatmap, 7-day sparkline, streaks, top project. */
export function ActivityCard({ data }: { data?: ActivityHeatmap }) {
  const days = data?.days ?? [];
  const streak = data?.streak;
  const week = lastNDays(days, 7, resolveToday(days));
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
