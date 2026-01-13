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
    project_type: Optional[str] = Field(None, pattern="^(web|cli|library|homelab|research)?$")
    primary_language: Optional[str] = None
    stack: Optional[str] = None
    repo_url: Optional[str] = None
    local_path: Optional[str] = None
    scope_size: Optional[str] = Field(None, pattern="^(tiny|medium|long-haul)?$")
    learning_goal: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Model for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Model for updating a project. All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(idea|active|paused|archived)$")
    project_type: Optional[str] = Field(None, pattern="^(web|cli|library|homelab|research)?$")
    primary_language: Optional[str] = None
    stack: Optional[str] = None
    repo_url: Optional[str] = None
    local_path: Optional[str] = None
    scope_size: Optional[str] = Field(None, pattern="^(tiny|medium|long-haul)?$")
    learning_goal: Optional[str] = None


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
    note_type: str = Field(default="log", pattern="^(log|idea|blocker|reflection)$")


class NoteCreate(NoteBase):
    """Model for creating a new note."""
    pass


class NoteResponse(NoteBase):
    """Model for note response."""
    id: int
    project_id: int
    created_at: str
    
    class Config:
        from_attributes = True


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
