import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Search } from "lucide-react";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import {
  PROJECT_STATUSES,
  type Project,
  type ProjectInput,
  type ProjectStatus,
} from "@/lib/api/types";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input, Select } from "@/components/ui/Input";
import { StatusBadge } from "@/components/ui/Badge";
import { Dialog } from "@/components/ui/Dialog";
import { LoadingState, ErrorState, EmptyState } from "@/components/ui/Empty";
import { ProjectForm } from "@/components/forms/ProjectForm";
import { ProjectThumbnail } from "@/components/project/ProjectThumbnail";
import { useToast } from "@/components/Toast";
import { relativeTime } from "@/lib/format";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";

export default function Projects() {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search, 200);
  const [status, setStatus] = useState<ProjectStatus | "">("");
  const [tag, setTag] = useState<string>("");
  const [createOpen, setCreateOpen] = useState(false);

  const { toast } = useToast();
  const qc = useQueryClient();

  const projectsQ = useQuery({
    queryKey: qk.projects({ search: debouncedSearch, status, tag }),
    queryFn: () =>
      api.listProjects({
        search: debouncedSearch || undefined,
        status: status || undefined,
        tag: tag || undefined,
        sort: "recent",
        limit: 50,
      }),
    placeholderData: (prev) => prev,
  });
  const tagsQ = useQuery({ queryKey: qk.tags, queryFn: api.listTags });

  const createMut = useMutation({
    mutationFn: (data: ProjectInput) => api.createProject(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["projects"] });
      toast("Project created", "success");
      setCreateOpen(false);
    },
    onError: (e) => toast(`Create failed: ${(e as Error).message}`, "error"),
  });

  const projects = useMemo(() => projectsQ.data?.projects ?? [], [projectsQ.data]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Projects</h1>
          <p className="mt-1 text-fg-soft">
            {projectsQ.data ? `${projectsQ.data.total} total` : ""}
          </p>
        </div>
        <Button onClick={() => setCreateOpen(true)}>
          <Plus size={16} /> New project
        </Button>
      </div>

      <Card>
        <CardContent className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <Search
              size={16}
              className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-fg-soft"
            />
            <Input
              className="pl-9"
              type="search"
              placeholder="Search projects..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <Select
            value={status}
            onChange={(e) => setStatus(e.target.value as ProjectStatus | "")}
            className="w-40"
          >
            <option value="">All statuses</option>
            {PROJECT_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </Select>
          <Select
            value={tag}
            onChange={(e) => setTag(e.target.value)}
            className="w-44"
          >
            <option value="">All tags</option>
            {(tagsQ.data?.tags ?? []).map((t) => (
              <option key={t.name} value={t.name}>
                {t.name} ({t.project_count})
              </option>
            ))}
          </Select>
        </CardContent>
      </Card>

      {projectsQ.isLoading && <LoadingState />}
      {projectsQ.error && <ErrorState error={projectsQ.error} />}

      {projectsQ.data && projects.length === 0 && (
        <EmptyState
          title="No projects match your filters"
          description="Try clearing filters or create a new project to get started."
          action={
            <Button onClick={() => setCreateOpen(true)}>
              <Plus size={16} /> New project
            </Button>
          }
        />
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {projects.map((p) => (
          <ProjectCard key={p.id} project={p} />
        ))}
      </div>

      <Dialog
        open={createOpen}
        onOpenChange={setCreateOpen}
        title="Create project"
        description="Track a new project. You can fill in just the name now and refine later."
      >
        <ProjectForm
          onSubmit={async (values) => {
            await createMut.mutateAsync(values);
          }}
          onCancel={() => setCreateOpen(false)}
          submitting={createMut.isPending}
          submitLabel="Create"
        />
      </Dialog>
    </div>
  );
}

function ProjectCard({ project }: { project: Project }) {
  const openTasks = project.open_task_count ?? 0;

  return (
    <Link
      to={`/projects/${project.id}`}
      className="group block text-fg no-underline hover:no-underline"
    >
      <Card className="flex h-full flex-col overflow-hidden cg-card-hover">
        <ProjectThumbnail project={project} />
        <CardContent className="flex-1 space-y-3">
          <div className="flex items-start justify-between gap-2">
            <h3 className="flex items-center gap-2 text-lg font-semibold leading-tight">
              <span>{project.name}</span>
              {openTasks > 0 && (
                <span
                  className="inline-flex h-5 min-w-5 shrink-0 items-center justify-center rounded-full bg-danger px-1 text-[11px] font-semibold leading-none text-white"
                  aria-label={`${openTasks} open task${openTasks === 1 ? "" : "s"}`}
                  title={`${openTasks} open task${openTasks === 1 ? "" : "s"}`}
                >
                  {openTasks > 99 ? "99+" : openTasks}
                </span>
              )}
            </h3>
            <StatusBadge status={project.status} />
          </div>
          {project.description && (
            <p className="line-clamp-3 text-sm text-fg-soft">{project.description}</p>
          )}

          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs text-fg-soft">
              <span>Progress</span>
              <span>{project.progress}%</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-surface-alt">
              <div
                className="h-full bg-primary transition-all"
                style={{ width: `${project.progress}%` }}
              />
            </div>
          </div>

          <div className="flex flex-wrap gap-1.5">
            {project.project_type && (
              <span className="cg-badge">{project.project_type}</span>
            )}
            {project.primary_language && (
              <span className="cg-badge">{project.primary_language}</span>
            )}
            {project.scope_size && (
              <span className="cg-badge">{project.scope_size}</span>
            )}
          </div>

          <div className="text-xs text-fg-soft">
            Last worked: {relativeTime(project.last_worked_at)}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
