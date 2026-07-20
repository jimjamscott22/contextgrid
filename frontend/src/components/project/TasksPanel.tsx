import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckSquare, Square, Trash2 } from "lucide-react";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { LoadingState, EmptyState } from "@/components/ui/Empty";

export function TasksPanel({ projectId }: { projectId: number }) {
  const [title, setTitle] = useState("");
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: qk.projectTasks(projectId),
    queryFn: () => api.listProjectTasks(projectId),
  });

  const createMut = useMutation({
    mutationFn: () => api.createProjectTask(projectId, title),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.projectTasks(projectId) });
      qc.invalidateQueries({ queryKey: ["projects"] });
      setTitle("");
    },
  });
  const toggleMut = useMutation({
    mutationFn: (id: number) => api.toggleProjectTask(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.projectTasks(projectId) });
      qc.invalidateQueries({ queryKey: ["projects"] });
    },
  });
  const deleteMut = useMutation({
    mutationFn: (id: number) => api.deleteProjectTask(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.projectTasks(projectId) });
      qc.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Checklist</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (title.trim()) createMut.mutate();
          }}
          className="flex gap-2"
        >
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Add a task..."
          />
          <Button type="submit" disabled={!title.trim() || createMut.isPending}>
            Add
          </Button>
        </form>

        {isLoading && <LoadingState />}
        {data && data.tasks.length === 0 && (
          <EmptyState
            title="No tasks"
            description="Break down work into small, checkable items."
          />
        )}

        <ul className="divide-y divide-border">
          {data?.tasks.map((t) => (
            <li key={t.id} className="flex items-center gap-3 py-2">
              <button
                type="button"
                onClick={() => toggleMut.mutate(t.id)}
                className="text-fg-soft hover:text-primary"
                aria-label={t.is_completed ? "Mark incomplete" : "Mark complete"}
              >
                {t.is_completed ? (
                  <CheckSquare size={18} className="text-success" />
                ) : (
                  <Square size={18} />
                )}
              </button>
              <span
                className={
                  t.is_completed ? "flex-1 text-fg-soft line-through" : "flex-1"
                }
              >
                {t.title}
              </span>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => deleteMut.mutate(t.id)}
                aria-label="Delete"
              >
                <Trash2 size={14} />
              </Button>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
