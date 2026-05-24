import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowLeft,
  Edit3,
  ExternalLink,
  Folder,
  Hand,
  Trash2,
} from "lucide-react";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { StatusBadge } from "@/components/ui/Badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tabs";
import { Dialog } from "@/components/ui/Dialog";
import { LoadingState, ErrorState } from "@/components/ui/Empty";
import { Markdown } from "@/components/Markdown";
import { ProjectForm } from "@/components/forms/ProjectForm";
import { ProjectTagsPanel } from "@/components/project/TagsPanel";
import { NotesPanel } from "@/components/project/NotesPanel";
import { TasksPanel } from "@/components/project/TasksPanel";
import { LinksPanel } from "@/components/project/LinksPanel";
import { CommandsPanel } from "@/components/project/CommandsPanel";
import { RelationshipsPanel } from "@/components/project/RelationshipsPanel";
import { ScreenshotsPanel } from "@/components/project/ScreenshotsPanel";
import { ReadmePanel } from "@/components/project/ReadmePanel";
import { useToast } from "@/components/Toast";
import { formatDate, relativeTime } from "@/lib/format";
import type { ProjectInput } from "@/lib/api/types";

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const projectId = Number(id);
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { toast } = useToast();
  const [editOpen, setEditOpen] = useState(false);

  const { data: project, isLoading, error } = useQuery({
    queryKey: qk.project(projectId),
    queryFn: () => api.getProject(projectId),
    enabled: !Number.isNaN(projectId),
  });

  const touchMut = useMutation({
    mutationFn: () => api.touchProject(projectId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.project(projectId) });
      qc.invalidateQueries({ queryKey: ["projects"] });
      toast("Touched — last worked just now", "success");
    },
  });

  const deleteMut = useMutation({
    mutationFn: () => api.deleteProject(projectId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["projects"] });
      toast("Project deleted", "success");
      navigate("/projects");
    },
    onError: (e) => toast(`Delete failed: ${(e as Error).message}`, "error"),
  });

  const updateMut = useMutation({
    mutationFn: (data: ProjectInput) => api.updateProject(projectId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.project(projectId) });
      qc.invalidateQueries({ queryKey: ["projects"] });
      toast("Project updated", "success");
      setEditOpen(false);
    },
    onError: (e) => toast(`Update failed: ${(e as Error).message}`, "error"),
  });

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState error={error} />;
  if (!project) return null;

  return (
    <div className="space-y-6">
      <div>
        <Link
          to="/projects"
          className="inline-flex items-center gap-1 text-sm text-fg-soft no-underline hover:text-primary"
        >
          <ArrowLeft size={14} /> All projects
        </Link>
      </div>

      <Card>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-3xl font-bold tracking-tight">{project.name}</h1>
                <StatusBadge status={project.status} />
              </div>
              {project.description && (
                <p className="mt-2 text-fg-soft">{project.description}</p>
              )}
              <div className="mt-3 flex flex-wrap gap-3 text-xs text-fg-soft">
                <span>Created {formatDate(project.created_at)}</span>
                <span>Last worked {relativeTime(project.last_worked_at)}</span>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button variant="secondary" onClick={() => touchMut.mutate()}>
                <Hand size={16} /> Touch
              </Button>
              <Button variant="secondary" onClick={() => setEditOpen(true)}>
                <Edit3 size={16} /> Edit
              </Button>
              <Button
                variant="danger"
                onClick={() => {
                  if (confirm(`Delete "${project.name}"? This cannot be undone.`)) {
                    deleteMut.mutate();
                  }
                }}
              >
                <Trash2 size={16} /> Delete
              </Button>
            </div>
          </div>

          <div className="grid gap-3 md:grid-cols-4">
            <Meta label="Type" value={project.project_type ?? "—"} />
            <Meta label="Language" value={project.primary_language ?? "—"} />
            <Meta label="Scope" value={project.scope_size ?? "—"} />
            <Meta label="Progress" value={`${project.progress}%`} />
          </div>

          {project.stack && (
            <Meta label="Stack" value={project.stack} block />
          )}

          {(project.repo_url || project.local_path) && (
            <div className="flex flex-wrap gap-2">
              {project.repo_url && (
                <a
                  href={project.repo_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 rounded-md border border-border bg-surface-alt px-3 py-1.5 text-sm text-fg no-underline hover:text-primary hover:no-underline"
                >
                  <ExternalLink size={14} /> Repo
                </a>
              )}
              {project.local_path && (
                <span className="inline-flex items-center gap-1.5 rounded-md border border-border bg-surface-alt px-3 py-1.5 text-sm">
                  <Folder size={14} /> {project.local_path}
                </span>
              )}
            </div>
          )}

          {project.learning_goal && (
            <Card className="border-warning/40 bg-warning/5">
              <CardContent>
                <div className="text-xs font-semibold uppercase text-warning">
                  Learning goal
                </div>
                <p className="mt-1 text-sm">{project.learning_goal}</p>
              </CardContent>
            </Card>
          )}

          <ProjectTagsPanel projectId={projectId} />
        </CardContent>
      </Card>

      <Tabs defaultValue="notes" className="space-y-4">
        <TabsList>
          <TabsTrigger value="notes">Notes</TabsTrigger>
          <TabsTrigger value="tasks">Tasks</TabsTrigger>
          <TabsTrigger value="links">Links</TabsTrigger>
          <TabsTrigger value="commands">Commands</TabsTrigger>
          <TabsTrigger value="relationships">Relationships</TabsTrigger>
          <TabsTrigger value="screenshots">Screenshots</TabsTrigger>
          <TabsTrigger value="readme">README</TabsTrigger>
          <TabsTrigger value="structure">Structure</TabsTrigger>
        </TabsList>
        <TabsContent value="notes">
          <NotesPanel projectId={projectId} />
        </TabsContent>
        <TabsContent value="tasks">
          <TasksPanel projectId={projectId} />
        </TabsContent>
        <TabsContent value="links">
          <LinksPanel projectId={projectId} />
        </TabsContent>
        <TabsContent value="commands">
          <CommandsPanel projectId={projectId} />
        </TabsContent>
        <TabsContent value="relationships">
          <RelationshipsPanel projectId={projectId} />
        </TabsContent>
        <TabsContent value="screenshots">
          <ScreenshotsPanel projectId={projectId} />
        </TabsContent>
        <TabsContent value="readme">
          <ReadmePanel projectId={projectId} />
        </TabsContent>
        <TabsContent value="structure">
          <Card>
            <CardHeader>
              <CardTitle>Folder structure</CardTitle>
            </CardHeader>
            <CardContent>
              {project.folder_structure ? (
                <Markdown source={"```\n" + project.folder_structure + "\n```"} />
              ) : (
                <p className="text-sm text-fg-soft">
                  No folder structure captured. Edit the project to add one.
                </p>
              )}
              {project.folder_structure_img_url && (
                <img
                  src={project.folder_structure_img_url}
                  alt="Folder structure"
                  className="mt-4 max-w-full rounded-md border border-border"
                />
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Dialog
        open={editOpen}
        onOpenChange={setEditOpen}
        title="Edit project"
        className="w-[min(48rem,92vw)]"
      >
        <ProjectForm
          defaultValues={{
            ...project,
            description: project.description ?? "",
            primary_language: project.primary_language ?? "",
            stack: project.stack ?? "",
            repo_url: project.repo_url ?? "",
            local_path: project.local_path ?? "",
            learning_goal: project.learning_goal ?? "",
          }}
          onSubmit={async (values) => {
            await updateMut.mutateAsync(values);
          }}
          onCancel={() => setEditOpen(false)}
          submitting={updateMut.isPending}
          submitLabel="Save changes"
        />
      </Dialog>
    </div>
  );
}

function Meta({
  label,
  value,
  block,
}: {
  label: string;
  value: string;
  block?: boolean;
}) {
  return (
    <div
      className={
        block
          ? "rounded-md border border-border bg-surface-alt p-3"
          : "rounded-md border border-border bg-surface-alt p-3"
      }
    >
      <div className="text-xs uppercase tracking-wide text-fg-soft">{label}</div>
      <div className="mt-1 truncate text-sm font-medium text-fg">{value}</div>
    </div>
  );
}
