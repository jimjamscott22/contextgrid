export const PROJECT_STATUSES: readonly ProjectStatus[] = [
  "idea",
  "active",
  "paused",
  "archived",
];

export const PROJECT_TYPES = [
  "web-app",
  "cli",
  "documentation",
  "college",
  "desktop-app",
  "pwa",
  "llm-integrated",
  "website",
] as const;

export type ProjectType = (typeof PROJECT_TYPES)[number];

export const PROJECT_TYPE_LABELS: Record<ProjectType, string> = {
  "web-app": "Web App",
  cli: "CLI",
  documentation: "Documentation",
  college: "College",
  "desktop-app": "Desktop",
  pwa: "PWA",
  "llm-integrated": "LLM-based/integrated",
  website: "Website",
};

export function projectTypeLabel(value: string): string {
  return PROJECT_TYPE_LABELS[value as ProjectType] ?? value;
}

export const SCOPE_SIZES: readonly ScopeSize[] = ["tiny", "medium", "long-haul"];

export const NOTE_TYPES: readonly NoteType[] = [
  "log",
  "idea",
  "blocker",
  "reflection",
  "future_idea",
];

export const NOTE_STATUSES: readonly NoteStatus[] = [
  "active",
  "completed",
  "archived",
];

export const LINK_TYPES: readonly LinkType[] = [
  "docs",
  "deployment",
  "design",
  "board",
  "repo",
  "other",
];

export const RELATIONSHIP_TYPES: readonly RelationshipType[] = [
  "related_to",
  "depends_on",
  "part_of",
];

export type ProjectStatus = "idea" | "active" | "paused" | "archived";

export type ScopeSize = "tiny" | "medium" | "long-haul";

export type NoteType = "log" | "idea" | "blocker" | "reflection" | "future_idea";

export type NoteStatus = "active" | "completed" | "archived";

export type LinkType = "docs" | "deployment" | "design" | "board" | "repo" | "other";

export type RelationshipType = "related_to" | "depends_on" | "part_of";

export interface Project {
  id: number;
  name: string;
  description: string | null;
  status: ProjectStatus;
  project_type: ProjectType | null;
  primary_language: string | null;
  stack: string | null;
  repo_url: string | null;
  local_path: string | null;
  scope_size: ScopeSize | null;
  learning_goal: string | null;
  progress: number;
  folder_structure: string | null;
  folder_structure_img_url: string | null;
  created_at: string;
  last_worked_at: string | null;
  is_archived: number;
  /** Incomplete checklist tasks for this project (badge count). */
  open_task_count?: number;
}

export interface ProjectInput {
  name: string;
  description?: string | null;
  status: ProjectStatus;
  project_type?: ProjectType | null;
  primary_language?: string | null;
  stack?: string | null;
  repo_url?: string | null;
  local_path?: string | null;
  scope_size?: ScopeSize | null;
  learning_goal?: string | null;
  progress: number;
  folder_structure?: string | null;
  folder_structure_img_url?: string | null;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
}

export interface Tag {
  name: string;
  project_count: number;
}

export interface TagListResponse {
  tags: Tag[];
  total: number;
}

export interface Note {
  id: number;
  project_id: number;
  content: string;
  note_type: NoteType;
  created_at: string;
  task_status: NoteStatus;
}

export interface NoteListResponse {
  notes: Note[];
  total: number;
}

export interface TaskNote extends Note {
  project_name: string;
  project_status: ProjectStatus;
}

export interface TaskListResponse {
  tasks: TaskNote[];
  total: number;
}

export interface Relationship {
  id: number;
  source_project_id: number;
  target_project_id: number;
  relationship_type: RelationshipType;
  target_project_name: string;
  direction: "outgoing" | "incoming";
  created_at: string;
}

export interface RelationshipListResponse {
  relationships: Relationship[];
  total: number;
}

export interface ActivityDay {
  date: string;
  count: number;
  projects: string;
}

export interface ActivityStreak {
  current_streak: number;
  longest_streak: number;
}

export interface ActivityHeatmap {
  days: ActivityDay[];
  streak: ActivityStreak;
}

export interface GraphNode {
  id: number;
  label: string;
  status: ProjectStatus;
  project_type: ProjectType | null;
  primary_language: string | null;
}

export interface GraphEdge {
  source: number;
  target: number;
  relationship_type: RelationshipType;
  is_inferred: boolean;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface Link {
  id: number;
  project_id: number;
  title: string;
  url: string;
  link_type: LinkType;
  created_at: string;
}

export interface LinkInput {
  title: string;
  url: string;
  link_type: LinkType;
}

export interface LinkListResponse {
  links: Link[];
  total: number;
}

export interface Command {
  id: number;
  project_id: number;
  label: string;
  command: string;
  created_at: string;
}

export interface CommandInput {
  label: string;
  command: string;
}

export interface CommandListResponse {
  commands: Command[];
  total: number;
}

export interface ProjectTask {
  id: number;
  project_id: number;
  title: string;
  is_completed: number;
  created_at: string;
}

export interface ProjectTaskListResponse {
  tasks: ProjectTask[];
  total: number;
}

export interface Template {
  id: number;
  name: string;
  description: string | null;
  default_status: ProjectStatus;
  default_project_type: ProjectType | null;
  default_primary_language: string | null;
  default_stack: string | null;
  default_scope_size: ScopeSize | null;
  default_learning_goal: string | null;
  default_tags: string | null;
  created_at: string;
}

export interface TemplateListResponse {
  templates: Template[];
  total: number;
}

export interface AnalyticsChartItem {
  label: string;
  value: number;
}

export interface AnalyticsSummary {
  total: number;
  active: number;
  ideas: number;
  paused: number;
  archived: number;
  avg_progress: number;
}

export interface Analytics {
  summary: AnalyticsSummary;
  by_status: AnalyticsChartItem[];
  by_language: AnalyticsChartItem[];
  by_type: AnalyticsChartItem[];
  activity_over_time: AnalyticsChartItem[];
  progress_distribution: AnalyticsChartItem[];
  by_tag: AnalyticsChartItem[];
}

export interface Screenshot {
  filename: string;
  url: string;
  label: string;
  is_cover: boolean;
}

export interface ScreenshotListResponse {
  screenshots: Screenshot[];
  count: number;
}

export interface Mermaid {
  diagram: string;
  diagram_type: string;
}

export interface ReadmeSnapshot {
  project_id: number;
  content: string;
  source_ref: string | null;
  fetched_at: string;
}

export interface MessageResponse {
  message: string;
}

export interface TouchResponse {
  message: string;
  last_worked_at: string;
}
