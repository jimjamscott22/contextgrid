import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Circle, Archive } from "lucide-react";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import { NOTE_STATUSES, type NoteStatus } from "@/lib/api/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Select } from "@/components/ui/Input";
import { StatusBadge } from "@/components/ui/Badge";
import { LoadingState, ErrorState, EmptyState } from "@/components/ui/Empty";
import { useToast } from "@/components/Toast";
import { relativeTime } from "@/lib/format";

export default function Tasks() {
  const [filter, setFilter] = useState<NoteStatus>("active");
  const { data, isLoading, error } = useQuery({
    queryKey: qk.tasks(filter),
    queryFn: () => api.listTasks(filter),
  });
  const qc = useQueryClient();
  const { toast } = useToast();

  const statusMut = useMutation({
    mutationFn: ({ id, status }: { id: number; status: NoteStatus }) =>
      api.setNoteStatus(id, status),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["tasks"] });
      qc.invalidateQueries({ queryKey: ["notes"] });
    },
    onError: (e) => toast(`Update failed: ${(e as Error).message}`, "error"),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Tasks</h1>
        <p className="mt-1 text-fg-soft">
          Cross-project notes — quickly triage what&apos;s in progress.
        </p>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>
            {data ? `${data.total} ${filter} task${data.total === 1 ? "" : "s"}` : ""}
          </CardTitle>
          <Select
            value={filter}
            onChange={(e) => setFilter(e.target.value as NoteStatus)}
            className="w-40"
          >
            {NOTE_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </Select>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading && <LoadingState />}
          {error && <ErrorState error={error} />}
          {data && data.tasks.length === 0 && (
            <EmptyState
              title={`No ${filter} tasks`}
              description="Capture notes from a project's detail view to see them here."
              className="m-4"
            />
          )}
          <ul className="divide-y divide-border">
            {data?.tasks.map((t) => (
              <li
                key={t.id}
                className="flex items-start gap-3 px-4 py-3 hover:bg-surface-alt"
              >
                <button
                  type="button"
                  onClick={() =>
                    statusMut.mutate({
                      id: t.id,
                      status: t.task_status === "completed" ? "active" : "completed",
                    })
                  }
                  className="mt-0.5 text-fg-soft hover:text-success"
                  aria-label={t.task_status === "completed" ? "Mark active" : "Mark completed"}
                >
                  {t.task_status === "completed" ? (
                    <CheckCircle2 size={18} className="text-success" />
                  ) : (
                    <Circle size={18} />
                  )}
                </button>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="cg-badge">{t.note_type}</span>
                    <Link
                      to={`/projects/${t.project_id}`}
                      className="text-xs text-primary"
                    >
                      {t.project_name}
                    </Link>
                    <StatusBadge status={t.project_status} />
                    <span className="text-xs text-fg-soft">
                      {relativeTime(t.created_at)}
                    </span>
                  </div>
                  <p className="mt-1 whitespace-pre-wrap text-sm">{t.content}</p>
                </div>
                {t.task_status !== "archived" && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => statusMut.mutate({ id: t.id, status: "archived" })}
                    aria-label="Archive"
                  >
                    <Archive size={16} />
                  </Button>
                )}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
