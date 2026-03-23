"""
Pydantic models for API request/response validation.
These models define the structure of data exchanged via the API.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# =========================
# Project Models
# =========================

class ProjectBase(BaseModel):
    """Base model for project data."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = Field(default="idea", pattern="^(idea|active|paused|archived)$")
    project_type: Optional[str] = Field(None, pattern="^(web|cli|library|school|homelab|desktop|llm-integrated|other)?$")
    primary_language: Optional[str] = None
    stack: Optional[str] = None
    repo_url: Optional[str] = None
    local_path: Optional[str] = None
    scope_size: Optional[str] = Field(None, pattern="^(tiny|medium|long-haul)?$")
    learning_goal: Optional[str] = None
    progress: int = Field(default=0, ge=0, le=100)
    folder_structure: Optional[str] = Field(None, max_length=65535)
    folder_structure_img_url: Optional[str] = Field(None, max_length=2000)


class ProjectCreate(ProjectBase):
    """Model for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Model for updating a project. All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(idea|active|paused|archived)$")
    project_type: Optional[str] = Field(None, pattern="^(web|cli|library|school|homelab|desktop|llm-integrated|other)?$")
    primary_language: Optional[str] = None
    stack: Optional[str] = None
    repo_url: Optional[str] = None
    local_path: Optional[str] = None
    scope_size: Optional[str] = Field(None, pattern="^(tiny|medium|long-haul)?$")
    learning_goal: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    folder_structure: Optional[str] = Field(None, max_length=65535)
    folder_structure_img_url: Optional[str] = Field(None, max_length=2000)


class ProjectResponse(ProjectBase):
    """Model for project response."""
    id: int
    created_at: str
    last_worked_at: Optional[str] = None
    is_archived: int = 0
    
    class Config:
        from_attributes = True


# =========================
# Note Models
# =========================

class NoteBase(BaseModel):
    """Base model for note data."""
    content: str = Field(..., min_length=1)
    note_type: str = Field(default="log", pattern="^(log|idea|blocker|reflection|future_idea)$")


class NoteCreate(NoteBase):
    """Model for creating a new note."""
    pass


class NoteResponse(NoteBase):
    """Model for note response."""
    id: int
    project_id: int
    created_at: str
    task_status: str = "active"

    class Config:
        from_attributes = True


class NoteStatusUpdate(BaseModel):
    """Model for updating only the task_status of a note."""
    status: str = Field(..., pattern="^(active|completed|archived)$")


# =========================
# Tag Models
# =========================

class TagBase(BaseModel):
    """Base model for tag data."""
    name: str = Field(..., min_length=1, max_length=100)


class TagCreate(TagBase):
    """Model for adding a tag to a project."""
    pass


class TagResponse(BaseModel):
    """Model for tag response."""
    name: str
    project_count: int = 0
    
    class Config:
        from_attributes = True


class TagSimple(BaseModel):
    """Simple tag model with just the name."""
    name: str


# =========================
# Response Models
# =========================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    message: str


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


class TouchResponse(BaseModel):
    """Response for touch endpoint."""
    message: str
    last_worked_at: str


class ProjectListResponse(BaseModel):
    """Response for listing projects."""
    projects: list[ProjectResponse]
    total: int


class TagListResponse(BaseModel):
    """Response for listing tags."""
    tags: list[TagResponse]
    total: int


class NoteListResponse(BaseModel):
    """Response for listing notes."""
    notes: list[NoteResponse]
    total: int


class TaskNoteResponse(NoteBase):
    """Note response enriched with parent project info, for cross-project task listing."""
    id: int
    project_id: int
    created_at: str
    task_status: str = "active"
    project_name: str
    project_status: str

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Response for listing notes/tasks across all projects."""
    tasks: list[TaskNoteResponse]
    total: int


# =========================
# Relationship Models
# =========================

class RelationshipBase(BaseModel):
    """Base model for relationship data."""
    target_project_id: int
    relationship_type: str = Field(..., pattern="^(related_to|depends_on|part_of)$")


class RelationshipCreate(RelationshipBase):
    """Model for creating a new relationship."""
    pass


class RelationshipResponse(BaseModel):
    """Model for relationship response."""
    id: int
    source_project_id: int
    target_project_id: int
    relationship_type: str
    target_project_name: str
    direction: str = "outgoing"
    created_at: str

    class Config:
        from_attributes = True


class RelationshipListResponse(BaseModel):
    """Response for listing relationships."""
    relationships: list[RelationshipResponse]
    total: int


# =========================
# Graph Data Models
# =========================

# =========================
# Activity / Heatmap Models
# =========================

class ActivityDay(BaseModel):
    """A single day's activity data for the heatmap."""
    date: str
    count: int
    projects: str = ""


class ActivityStreakResponse(BaseModel):
    """Streak tracking data."""
    current_streak: int
    longest_streak: int


class ActivityHeatmapResponse(BaseModel):
    """Full heatmap response with activity data and streaks."""
    days: list[ActivityDay]
    streak: ActivityStreakResponse


class GraphNode(BaseModel):
    """Node in the project graph."""
    id: int
    label: str
    status: str
    project_type: Optional[str] = None
    primary_language: Optional[str] = None


class GraphEdge(BaseModel):
    """Edge in the project graph."""
    source: int
    target: int
    relationship_type: str
    is_inferred: bool = False


class GraphDataResponse(BaseModel):
    """Full graph data for visualization."""
    nodes: list[GraphNode]
    edges: list[GraphEdge]


# =========================
# Project Link Models
# =========================

class LinkBase(BaseModel):
    """Base model for project link data."""
    title: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., min_length=1, max_length=2000)
    link_type: str = Field(default="other", pattern="^(docs|deployment|design|board|repo|other)$")


class LinkCreate(LinkBase):
    """Model for creating a new project link."""
    pass


class LinkResponse(LinkBase):
    """Model for project link response."""
    id: int
    project_id: int
    created_at: str

    class Config:
        from_attributes = True


class LinkListResponse(BaseModel):
    """Response for listing project links."""
    links: list[LinkResponse]
    total: int


# =========================
# Project Command Models
# =========================

class CommandBase(BaseModel):
    """Base model for project command data."""
    label: str = Field(..., min_length=1, max_length=255)
    command: str = Field(..., min_length=1)


class CommandCreate(CommandBase):
    """Model for creating a new project command."""
    pass


class CommandResponse(CommandBase):
    """Model for project command response."""
    id: int
    project_id: int
    created_at: str

    class Config:
        from_attributes = True


class CommandListResponse(BaseModel):
    """Response for listing project commands."""
    commands: list[CommandResponse]
    total: int


# =========================
# Project Task Models (checkable per-project tasks)
# =========================

class ProjectTaskBase(BaseModel):
    """Base model for a project task."""
    title: str = Field(..., min_length=1, max_length=500)


class ProjectTaskCreate(ProjectTaskBase):
    """Model for creating a new project task."""
    pass


class ProjectTaskResponse(ProjectTaskBase):
    """Model for project task response."""
    id: int
    project_id: int
    is_completed: int = 0
    created_at: str

    class Config:
        from_attributes = True


class ProjectTaskListResponse(BaseModel):
    """Response for listing project tasks."""
    tasks: list[ProjectTaskResponse]
    total: int


# =========================
# Project Template Models
# =========================

class TemplateBase(BaseModel):
    """Base model for project template data."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    default_status: str = Field(default="idea", pattern="^(idea|active|paused|archived)$")
    default_project_type: Optional[str] = Field(None, pattern="^(web|cli|library|school|homelab|desktop|llm-integrated|other)?$")
    default_primary_language: Optional[str] = None
    default_stack: Optional[str] = None
    default_scope_size: Optional[str] = Field(None, pattern="^(tiny|medium|long-haul)?$")
    default_learning_goal: Optional[str] = None
    default_tags: Optional[str] = None  # comma-separated


class TemplateCreate(TemplateBase):
    """Model for creating a new project template."""
    pass


class TemplateUpdate(BaseModel):
    """Model for updating a project template. All fields optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    default_status: Optional[str] = Field(None, pattern="^(idea|active|paused|archived)$")
    default_project_type: Optional[str] = Field(None, pattern="^(web|cli|library|school|homelab|desktop|llm-integrated|other)?$")
    default_primary_language: Optional[str] = None
    default_stack: Optional[str] = None
    default_scope_size: Optional[str] = Field(None, pattern="^(tiny|medium|long-haul)?$")
    default_learning_goal: Optional[str] = None
    default_tags: Optional[str] = None


class TemplateResponse(TemplateBase):
    """Model for project template response."""
    id: int
    created_at: str

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """Response for listing project templates."""
    templates: list[TemplateResponse]
    total: int


# =========================
# Analytics Models
# =========================

class AnalyticsChartItem(BaseModel):
    """A single data point for a chart."""
    label: str
    value: int


class AnalyticsSummary(BaseModel):
    """Summary statistics for the analytics dashboard."""
    total: int = 0
    active: int = 0
    ideas: int = 0
    paused: int = 0
    archived: int = 0
    avg_progress: float = 0.0


class AnalyticsResponse(BaseModel):
    """Full analytics response with all chart data."""
    summary: AnalyticsSummary
    by_status: list[AnalyticsChartItem]
    by_language: list[AnalyticsChartItem]
    by_type: list[AnalyticsChartItem]
    activity_over_time: list[AnalyticsChartItem]
    progress_distribution: list[AnalyticsChartItem]
    by_tag: list[AnalyticsChartItem]


# =========================
# Screenshot Models
# =========================

class ScreenshotResponse(BaseModel):
    """Model for a single screenshot."""
    filename: str
    url: str
    label: str


class ScreenshotListResponse(BaseModel):
    """Model for list of screenshots."""
    screenshots: list[ScreenshotResponse]
    count: int


# =========================
# Mermaid Diagram Models
# =========================

class MermaidResponse(BaseModel):
    """Response containing a Mermaid diagram definition string."""
    diagram: str
    diagram_type: str
