import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, Activity, Flame, Layers, ListChecks } from "lucide-react";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/Badge";
import { LoadingState, ErrorState } from "@/components/ui/Empty";
import { ActivityCard } from "@/components/activity/ActivityCard";
import { relativeTime } from "@/lib/format";

export default function Home() {
  const projectsQ = useQuery({
    queryKey: qk.projects({ recent: true }),
    queryFn: () => api.listProjects({ sort: "recent", limit: 8 }),
  });
  const heatQ = useQuery({ queryKey: qk.heatmap, queryFn: api.activityHeatmap });
  const analyticsQ = useQuery({ queryKey: qk.analytics, queryFn: api.analytics });

  if (projectsQ.isLoading || heatQ.isLoading || analyticsQ.isLoading) {
    return <LoadingState label="Loading overview..." />;
  }
  if (projectsQ.error) return <ErrorState error={projectsQ.error} />;

  const summary = analyticsQ.data?.summary;
  const streak = heatQ.data?.streak;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Overview</h1>
        <p className="mt-1 text-fg-soft">
          Your personal project tracker at a glance.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <StatCard
          icon={<Layers size={18} />}
          label="Total projects"
          value={summary?.total ?? 0}
        />
        <StatCard
          icon={<Activity size={18} />}
          label="Active"
          value={summary?.active ?? 0}
          tone="success"
        />
        <StatCard
          icon={<ListChecks size={18} />}
          label="Avg progress"
          value={`${Math.round(summary?.avg_progress ?? 0)}%`}
        />
        <StatCard
          icon={<Flame size={18} />}
          label="Current streak"
          value={`${streak?.current_streak ?? 0}d`}
          tone="warning"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Recent activity</CardTitle>
            <Link
              to="/projects"
              className="inline-flex items-center gap-1 text-sm text-primary"
            >
              All projects <ArrowRight size={14} />
            </Link>
          </CardHeader>
          <CardContent className="divide-y divide-border p-0">
            {(projectsQ.data?.projects ?? []).map((p) => (
              <Link
                key={p.id}
                to={`/projects/${p.id}`}
                className="flex items-center justify-between gap-3 px-4 py-3 text-fg no-underline hover:bg-surface-alt hover:no-underline"
              >
                <div className="min-w-0">
                  <div className="truncate font-medium">{p.name}</div>
                  {p.description && (
                    <div className="truncate text-xs text-fg-soft">
                      {p.description}
                    </div>
                  )}
                </div>
                <div className="flex shrink-0 items-center gap-3">
                  <StatusBadge status={p.status} />
                  <span className="text-xs text-fg-soft">
                    {relativeTime(p.last_worked_at)}
                  </span>
                </div>
              </Link>
            ))}
            {projectsQ.data && projectsQ.data.projects.length === 0 && (
              <div className="px-4 py-8 text-center text-fg-soft">
                No projects yet —{" "}
                <Link to="/projects" className="text-primary">
                  create one
                </Link>
                .
              </div>
            )}
          </CardContent>
        </Card>

        <ActivityCard data={heatQ.data} />
      </div>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  tone,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  tone?: "success" | "warning";
}) {
  return (
    <Card>
      <CardContent className="flex items-center gap-3">
        <div
          className={
            tone === "success"
              ? "text-success"
              : tone === "warning"
              ? "text-warning"
              : "text-primary"
          }
        >
          {icon}
        </div>
        <div>
          <div className="text-xs uppercase tracking-wide text-fg-soft">
            {label}
          </div>
          <div className="text-2xl font-bold">{value}</div>
        </div>
      </CardContent>
    </Card>
  );
}
