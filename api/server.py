"""
ContextGrid API Server
FastAPI application providing REST API for project management
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional
import sys

from api.models import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    NoteCreate, NoteResponse, NoteListResponse,
    TagCreate, TagResponse, TagListResponse, TagSimple,
    HealthResponse, MessageResponse, TouchResponse
)
from api.config import config
from api import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    try:
        # Validate configuration
        is_valid, error = config.validate()
        if not is_valid:
            message = f"Configuration error: {error}"
            print(message, file=sys.stderr)
            raise RuntimeError(message)

        # Test database connection
        success, error = db.test_connection()
        if not success:
            message = f"Database connection failed: {error}"
            print(message, file=sys.stderr)
            raise RuntimeError(message)

        # Initialize schema
        db.initialize_database()
        print("Database initialized successfully")
    except Exception as e:
        if not isinstance(e, RuntimeError):
            print(f"Startup error: {e}", file=sys.stderr)
        raise

    yield


# Initialize FastAPI app
app = FastAPI(
    title="ContextGrid API",
    description="REST API for personal project tracking and management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Startup and Health Check
# =========================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    success, error = db.test_connection()
    
    if success:
        return HealthResponse(
            status="ok",
            message="API server and database are healthy"
        )
    else:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {error}"
        )


# =========================
# Project Endpoints
# =========================

@app.get("/api/projects", response_model=ProjectListResponse)
async def list_projects(
    status: Optional[str] = Query(None, pattern="^(idea|active|paused|archived)$"),
    tag: Optional[str] = Query(None),
    limit: Optional[int] = Query(None, ge=1, le=100),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: str = Query("last_worked_at", pattern="^(name|created_at|last_worked_at|status)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$")
):
    """
    List all projects with optional filtering and pagination.
    
    Query Parameters:
    - status: Filter by status (idea, active, paused, archived)
    - tag: Filter by tag name
    - limit: Maximum number of results
    - offset: Number of results to skip
    - sort_by: Field to sort by
    - sort_order: Sort order (asc or desc)
    """
    try:
        projects = db.list_projects(
            status=status,
            tag=tag,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return ProjectListResponse(
            projects=projects,
            total=len(projects)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int):
    """Get a single project by ID."""
    try:
        project = db.get_project(project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/projects", response_model=ProjectResponse, status_code=201)
async def create_project(project: ProjectCreate):
    """Create a new project."""
    try:
        project_id = db.create_project(
            name=project.name,
            description=project.description,
            status=project.status,
            project_type=project.project_type,
            primary_language=project.primary_language,
            stack=project.stack,
            repo_url=project.repo_url,
            local_path=project.local_path,
            scope_size=project.scope_size,
            learning_goal=project.learning_goal
        )
        
        # Fetch and return the created project
        created_project = db.get_project(project_id)
        return created_project
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, project: ProjectUpdate):
    """Update a project."""
    try:
        # Check if project exists
        existing = db.get_project(project_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        # Build update dict (only include non-None values)
        updates = {k: v for k, v in project.dict().items() if v is not None}
        
        if updates:
            success = db.update_project(project_id, **updates)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to update project")
        
        # Fetch and return the updated project
        updated_project = db.get_project(project_id)
        return updated_project
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/projects/{project_id}", response_model=MessageResponse)
async def delete_project(project_id: int):
    """Delete a project."""
    try:
        success = db.delete_project(project_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        return MessageResponse(message=f"Project {project_id} deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/projects/{project_id}/touch", response_model=TouchResponse)
async def touch_project(project_id: int):
    """Update the last_worked_at timestamp for a project."""
    try:
        success, timestamp = db.update_last_worked(project_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        return TouchResponse(
            message=f"Updated last_worked_at for project {project_id}",
            last_worked_at=timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Tag Endpoints
# =========================

@app.get("/api/tags", response_model=TagListResponse)
async def list_tags():
    """List all tags with project counts."""
    try:
        tags = db.list_all_tags()
        return TagListResponse(tags=tags, total=len(tags))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/tags", response_model=list[TagSimple])
async def get_project_tags(project_id: int):
    """Get all tags for a specific project."""
    try:
        # Check if project exists
        project = db.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        tag_names = db.list_project_tags(project_id)
        return [TagSimple(name=name) for name in tag_names]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/projects/{project_id}/tags", response_model=MessageResponse, status_code=201)
async def add_tag_to_project(project_id: int, tag: TagCreate):
    """Add a tag to a project."""
    try:
        # Check if project exists
        project = db.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        # Normalize tag name (lowercase, strip whitespace)
        tag_name = tag.name.strip().lower()
        
        added = db.add_tag_to_project(project_id, tag_name)
        
        if added:
            return MessageResponse(message=f"Tag '{tag_name}' added to project {project_id}")
        else:
            return MessageResponse(message=f"Tag '{tag_name}' already exists on project {project_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/projects/{project_id}/tags/{tag_name}", response_model=MessageResponse)
async def remove_tag_from_project(project_id: int, tag_name: str):
    """Remove a tag from a project."""
    try:
        # Normalize tag name
        tag_name = tag_name.strip().lower()
        
        removed = db.remove_tag_from_project(project_id, tag_name)
        
        if not removed:
            raise HTTPException(
                status_code=404,
                detail=f"Tag '{tag_name}' not found on project {project_id}"
            )
        
        return MessageResponse(message=f"Tag '{tag_name}' removed from project {project_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Note Endpoints
# =========================

@app.get("/api/projects/{project_id}/notes", response_model=NoteListResponse)
async def get_project_notes(project_id: int):
    """Get all notes for a project."""
    try:
        # Check if project exists
        project = db.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        notes = db.list_notes(project_id)
        return NoteListResponse(notes=notes, total=len(notes))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/projects/{project_id}/notes", response_model=NoteResponse, status_code=201)
async def create_note(project_id: int, note: NoteCreate):
    """Create a new note for a project."""
    try:
        # Check if project exists
        project = db.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        note_id = db.create_note(
            project_id=project_id,
            content=note.content,
            note_type=note.note_type
        )
        
        # Fetch and return the created note
        created_note = db.get_note(note_id)
        return created_note
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int):
    """Get a single note by ID."""
    try:
        note = db.get_note(note_id)
        
        if not note:
            raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
        
        return note
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/notes/{note_id}", response_model=MessageResponse)
async def delete_note(note_id: int):
    """Delete a note by ID."""
    try:
        success = db.delete_note(note_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
        
        return MessageResponse(message=f"Note {note_id} deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Main Entry Point
# =========================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        log_level="info"
    )
