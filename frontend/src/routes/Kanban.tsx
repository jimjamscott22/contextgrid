import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useDraggable,
  useDroppable,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import {
  PROJECT_STATUSES,
  type Project,
  type ProjectStatus,
} from "@/lib/api/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/Badge";
import { LoadingState, ErrorState } from "@/components/ui/Empty";
import { useToast } from "@/components/Toast";
import { cn } from "@/lib/cn";

const COLUMN_LABELS: Record<ProjectStatus, string> = {
  idea: "Ideas",
  active: "Active",
  paused: "Paused",
  archived: "Archived",
};

export default function Kanban() {
  const [activeId, setActiveId] = useState<number | null>(null);
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));
  const qc = useQueryClient();
  const { toast } = useToast();

  const { data, isLoading, error } = useQuery({
    queryKey: qk.projects({ kanban: true }),
    queryFn: () => api.listProjects({ include_archived: true, limit: 50 }),
  });

  const grouped = useMemo(() => {
    const groups: Record<ProjectStatus, Project[]> = {
      idea: [],
      active: [],
      paused: [],
      archived: [],
    };
    for (const p of data?.projects ?? []) groups[p.status].push(p);
    return groups;
  }, [data]);

  const updateMut = useMutation({
    mutationFn: ({ id, status }: { id: number; status: ProjectStatus }) =>
      api.updateProject(id, { status }),
    onMutate: async ({ id, status }) => {
      await qc.cancelQueries({ queryKey: ["projects"] });
      const prev = qc.getQueriesData({ queryKey: ["projects"] });
      qc.setQueriesData({ queryKey: ["projects"] }, (old: unknown) => {
        const typed = old as { projects?: Project[]; total?: number } | undefined;
        if (!typed?.projects) return old;
        return {
          ...typed,
          projects: typed.projects.map((p) =>
            p.id === id ? { ...p, status } : p
          ),
        };
      });
      return { prev };
    },
    onError: (err, _vars, ctx) => {
      if (ctx?.prev) {
        for (const [key, value] of ctx.prev) qc.setQueryData(key, value);
      }
      toast(`Move failed: ${(err as Error).message}`, "error");
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  const handleDragStart = (e: DragStartEvent) => {
    setActiveId(Number(e.active.id));
  };

  const handleDragEnd = (e: DragEndEvent) => {
    setActiveId(null);
    const overId = e.over?.id;
    if (!overId) return;
    const targetStatus = String(overId) as ProjectStatus;
    if (!PROJECT_STATUSES.includes(targetStatus)) return;
    const id = Number(e.active.id);
    const current = data?.projects.find((p) => p.id === id);
    if (!current || current.status === targetStatus) return;
    updateMut.mutate({ id, status: targetStatus });
  };

  const activeProject = data?.projects.find((p) => p.id === activeId);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Kanban</h1>
        <p className="mt-1 text-fg-soft">
          Drag projects between columns to change their status.
        </p>
      </div>

      {isLoading && <LoadingState />}
      {error && <ErrorState error={error} />}

      {data && (
        <DndContext sensors={sensors} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {PROJECT_STATUSES.map((status) => (
              <KanbanColumn
                key={status}
                status={status}
                projects={grouped[status]}
              />
            ))}
          </div>
          <DragOverlay>
            {activeProject ? <ProjectCardMini project={activeProject} dragging /> : null}
          </DragOverlay>
        </DndContext>
      )}
    </div>
  );
}

function KanbanColumn({
  status,
  projects,
}: {
  status: ProjectStatus;
  projects: Project[];
}) {
  const { setNodeRef, isOver } = useDroppable({ id: status });
  return (
    <Card
      ref={setNodeRef as never}
      className={cn(
        "h-full transition-colors",
        isOver && "ring-2 ring-primary/40"
      )}
    >
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="capitalize">{COLUMN_LABELS[status]}</CardTitle>
        <span className="cg-badge">{projects.length}</span>
      </CardHeader>
      <CardContent className="space-y-2">
        {projects.length === 0 && (
          <p className="py-6 text-center text-xs text-fg-soft">Drop projects here</p>
        )}
        {projects.map((p) => (
          <DraggableProject key={p.id} project={p} />
        ))}
      </CardContent>
    </Card>
  );
}

function DraggableProject({ project }: { project: Project }) {
  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({
    id: project.id,
  });
  return (
    <div
      ref={setNodeRef}
      {...attributes}
      {...listeners}
      className={cn(
        "cursor-grab active:cursor-grabbing",
        isDragging && "opacity-30"
      )}
    >
      <ProjectCardMini project={project} />
    </div>
  );
}

function ProjectCardMini({
  project,
  dragging,
}: {
  project: Project;
  dragging?: boolean;
}) {
  return (
    <div
      className={cn(
        "rounded-md border border-border bg-surface p-3 shadow-sm",
        dragging && "shadow-xl ring-2 ring-primary/40"
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <Link
          to={`/projects/${project.id}`}
          className="line-clamp-2 font-medium text-fg no-underline hover:text-primary hover:no-underline"
          onClick={(e) => e.stopPropagation()}
        >
          {project.name}
        </Link>
        <StatusBadge status={project.status} />
      </div>
      {project.description && (
        <p className="mt-1 line-clamp-2 text-xs text-fg-soft">
          {project.description}
        </p>
      )}
      <div className="mt-2 flex flex-wrap gap-1">
        {project.primary_language && (
          <span className="cg-badge text-[10px]">{project.primary_language}</span>
        )}
        {project.project_type && (
          <span className="cg-badge text-[10px]">{project.project_type}</span>
        )}
      </div>
      <div className="mt-2 h-1 overflow-hidden rounded-full bg-surface-alt">
        <div
          className="h-full bg-primary"
          style={{ width: `${project.progress}%` }}
        />
      </div>
    </div>
  );
}
