import { request } from "./client";
import type {
  ActivityHeatmap,
  Analytics,
  CommandInput,
  CommandListResponse,
  Command,
  GraphData,
  Link,
  LinkInput,
  LinkListResponse,
  MessageResponse,
  Mermaid,
  Note,
  NoteListResponse,
  NoteStatus,
  NoteType,
  Project,
  ProjectInput,
  ProjectListResponse,
  ProjectStatus,
  ProjectTask,
  ProjectTaskListResponse,
  ReadmeSnapshot,
  Relationship,
  RelationshipListResponse,
  RelationshipType,
  ScreenshotListResponse,
  TagListResponse,
  TaskListResponse,
  Template,
  TemplateListResponse,
  TouchResponse,
} from "./types";

interface ListProjectsParams {
  search?: string;
  status?: ProjectStatus | "";
  tag?: string;
  sort?: "recent" | "name" | "created";
  limit?: number;
  offset?: number;
  include_archived?: boolean;
  kanban?: boolean;
}

const PROJECT_LIST_LIMIT = 50;

const SORT_MAP: Record<string, string> = {
  recent: "last_worked_at",
  name: "name",
  created: "created_at",
};

function projectLimit(limit?: number): number | undefined {
  if (limit === undefined) return undefined;
  return Math.min(limit, PROJECT_LIST_LIMIT);
}

function mapProjectQuery(p: ListProjectsParams = {}): Record<string, string | number | undefined> {
  return {
    status: p.status || undefined,
    tag: p.tag || undefined,
    limit: projectLimit(p.limit),
    offset: p.offset,
    sort_by: p.sort ? SORT_MAP[p.sort] ?? p.sort : undefined,
  };
}

export const api = {
  listProjects: (params?: ListProjectsParams) =>
    request<ProjectListResponse>("/api/projects", { query: mapProjectQuery(params) }),

  getProject: (id: number) => request<Project>(`/api/projects/${id}`),

  createProject: (data: ProjectInput) =>
    request<Project>("/api/projects", { method: "POST", body: data }),

  updateProject: (id: number, data: Partial<ProjectInput>) =>
    request<Project>(`/api/projects/${id}`, { method: "PUT", body: data }),

  deleteProject: (id: number) =>
    request<MessageResponse>(`/api/projects/${id}`, { method: "DELETE" }),

  touchProject: (id: number) =>
    request<TouchResponse>(`/api/projects/${id}/touch`, { method: "POST" }),

  listTags: () => request<TagListResponse>("/api/tags"),

  listProjectTags: (projectId: number) =>
    request<Array<{ name: string }>>(`/api/projects/${projectId}/tags`),

  addTag: (projectId: number, name: string) =>
    request<MessageResponse>(`/api/projects/${projectId}/tags`, {
      method: "POST",
      body: { name },
    }),

  removeTag: (projectId: number, name: string) =>
    request<MessageResponse>(
      `/api/projects/${projectId}/tags/${encodeURIComponent(name)}`,
      { method: "DELETE" },
    ),

  listNotes: (projectId: number) =>
    request<NoteListResponse>(`/api/projects/${projectId}/notes`),

  createNote: (projectId: number, content: string, note_type: NoteType) =>
    request<Note>(`/api/projects/${projectId}/notes`, {
      method: "POST",
      body: { content, note_type },
    }),

  deleteNote: (id: number) =>
    request<MessageResponse>(`/api/notes/${id}`, { method: "DELETE" }),

  setNoteStatus: (id: number, status: NoteStatus) =>
    request<Note>(`/api/notes/${id}/status`, {
      method: "PATCH",
      body: { status },
    }),

  listTasks: (task_status?: NoteStatus | "") =>
    request<TaskListResponse>("/api/tasks", {
      query: { task_status: task_status || undefined, limit: 200 },
    }),

  listRelationships: (projectId: number) =>
    request<RelationshipListResponse>(`/api/projects/${projectId}/relationships`),

  createRelationship: (
    projectId: number,
    target_project_id: number,
    relationship_type: RelationshipType,
  ) =>
    request<Relationship>(`/api/projects/${projectId}/relationships`, {
      method: "POST",
      body: { target_project_id, relationship_type },
    }),

  deleteRelationship: (id: number) =>
    request<MessageResponse>(`/api/relationships/${id}`, { method: "DELETE" }),

  activityHeatmap: () => request<ActivityHeatmap>("/api/activity/heatmap"),

  graph: () => request<GraphData>("/api/graph"),

  listLinks: (projectId: number) =>
    request<LinkListResponse>(`/api/projects/${projectId}/links`),

  createLink: (projectId: number, data: LinkInput) =>
    request<Link>(`/api/projects/${projectId}/links`, {
      method: "POST",
      body: data,
    }),

  deleteLink: (id: number) =>
    request<MessageResponse>(`/api/links/${id}`, { method: "DELETE" }),

  listCommands: (projectId: number) =>
    request<CommandListResponse>(`/api/projects/${projectId}/commands`),

  createCommand: (projectId: number, data: CommandInput) =>
    request<Command>(`/api/projects/${projectId}/commands`, {
      method: "POST",
      body: data,
    }),

  deleteCommand: (id: number) =>
    request<MessageResponse>(`/api/commands/${id}`, { method: "DELETE" }),

  listProjectTasks: (projectId: number) =>
    request<ProjectTaskListResponse>(`/api/projects/${projectId}/tasks`),

  createProjectTask: (projectId: number, title: string) =>
    request<ProjectTask>(`/api/projects/${projectId}/tasks`, {
      method: "POST",
      body: { title },
    }),

  toggleProjectTask: (id: number) =>
    request<ProjectTask>(`/api/project-tasks/${id}/toggle`, { method: "PATCH" }),

  deleteProjectTask: (id: number) =>
    request<MessageResponse>(`/api/project-tasks/${id}`, { method: "DELETE" }),

  listTemplates: () => request<TemplateListResponse>("/api/templates"),

  createTemplate: (data: Partial<Template>) =>
    request<Template>("/api/templates", { method: "POST", body: data }),

  deleteTemplate: (id: number) =>
    request<MessageResponse>(`/api/templates/${id}`, { method: "DELETE" }),

  analytics: () => request<Analytics>("/api/analytics"),

  listScreenshots: (projectId: number) =>
    request<ScreenshotListResponse>(`/api/projects/${projectId}/screenshots`),

  uploadScreenshot: (projectId: number, file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return request<MessageResponse>(`/api/projects/${projectId}/screenshots`, {
      method: "POST",
      formData: fd,
    });
  },

  deleteScreenshot: (projectId: number, filename: string) =>
    request<MessageResponse>(
      `/api/projects/${projectId}/screenshots/${encodeURIComponent(filename)}`,
      { method: "DELETE" },
    ),

  overviewMermaid: () => request<Mermaid>("/api/mermaid/overview"),

  getReadme: (projectId: number) =>
    request<ReadmeSnapshot>(`/api/projects/${projectId}/readme`),

  attachReadme: (projectId: number, source?: string) =>
    request<ReadmeSnapshot>(`/api/projects/${projectId}/readme/attach`, {
      method: "POST",
      body: source ? { source } : {},
    }),

  deleteReadme: (projectId: number) =>
    request<MessageResponse>(`/api/projects/${projectId}/readme`, {
      method: "DELETE",
    }),
};
