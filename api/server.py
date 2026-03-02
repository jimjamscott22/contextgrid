"""
ContextGrid API Server
FastAPI application providing REST API for project management
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional
import sys
from pathlib import Path

# Add project root to path for imports to work when running directly
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from api.models import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    NoteCreate, NoteResponse, NoteListResponse,
    TagCreate, TagResponse, TagListResponse, TagSimple,
    HealthResponse, MessageResponse, TouchResponse,
    RelationshipCreate, RelationshipResponse, RelationshipListResponse,
    GraphNode, GraphEdge, GraphDataResponse,
    ActivityDay, ActivityStreakResponse, ActivityHeatmapResponse,
    LinkCreate, LinkResponse, LinkListResponse,
    TemplateCreate, TemplateUpdate, TemplateResponse, TemplateListResponse,
    AnalyticsChartItem, AnalyticsSummary, AnalyticsResponse
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


@app.put("/api/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: int, note: NoteCreate):
    """Update a note by ID."""
    try:
        # Check if note exists
        existing_note = db.get_note(note_id)
        if not existing_note:
            raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
        
        # Update the note
        success = db.update_note(note_id, content=note.content, note_type=note.note_type)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update note")
        
        # Fetch and return the updated note
        updated_note = db.get_note(note_id)
        return updated_note
        
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
# Relationship Endpoints
# =========================

@app.get("/api/projects/{project_id}/relationships", response_model=RelationshipListResponse)
async def get_project_relationships(project_id: int):
    """Get all relationships for a specific project (both outgoing and incoming)."""
    try:
        # Check if project exists
        project = db.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        relationships = db.list_project_relationships(project_id)
        return RelationshipListResponse(relationships=relationships, total=len(relationships))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/projects/{project_id}/relationships", response_model=RelationshipResponse, status_code=201)
async def create_relationship(project_id: int, relationship: RelationshipCreate):
    """Create a new relationship from this project to another."""
    try:
        # Check if source project exists
        source_project = db.get_project(project_id)
        if not source_project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        # Check if target project exists
        target_project = db.get_project(relationship.target_project_id)
        if not target_project:
            raise HTTPException(status_code=404, detail=f"Target project {relationship.target_project_id} not found")

        # Prevent self-relationships
        if project_id == relationship.target_project_id:
            raise HTTPException(status_code=400, detail="Cannot create relationship to self")

        # Check if relationship already exists
        if db.relationship_exists(project_id, relationship.target_project_id, relationship.relationship_type):
            raise HTTPException(status_code=409, detail="Relationship already exists")

        # Create the relationship
        relationship_id = db.create_relationship(
            source_project_id=project_id,
            target_project_id=relationship.target_project_id,
            relationship_type=relationship.relationship_type
        )

        # Fetch and return the created relationship
        created_relationship = db.get_relationship(relationship_id)
        return created_relationship

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/relationships/{relationship_id}", response_model=MessageResponse)
async def delete_relationship(relationship_id: int):
    """Delete a relationship by ID."""
    try:
        success = db.delete_relationship(relationship_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"Relationship {relationship_id} not found")

        return MessageResponse(message=f"Relationship {relationship_id} deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Activity / Heatmap Endpoints
# =========================

@app.get("/api/activity/heatmap", response_model=ActivityHeatmapResponse)
async def get_activity_heatmap(
    days: int = Query(365, ge=30, le=730)
):
    """
    Get activity heatmap data.

    Query Parameters:
    - days: Number of days of history to include (default: 365, min: 30, max: 730)
    """
    try:
        activity_data = db.get_activity_heatmap(days=days)
        streak_data = db.get_activity_streak()

        return ActivityHeatmapResponse(
            days=[ActivityDay(**day) for day in activity_data],
            streak=ActivityStreakResponse(**streak_data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Graph Data Endpoints
# =========================

@app.get("/api/graph", response_model=GraphDataResponse)
async def get_full_graph(include_inferred: bool = Query(True)):
    """
    Get full graph data for visualization.

    Query Parameters:
    - include_inferred: Whether to include auto-inferred relationships (default: True)
    """
    try:
        graph_data = db.get_graph_data()

        # Build nodes
        nodes = [
            GraphNode(
                id=p['id'],
                label=p['name'],
                status=p['status'],
                project_type=p.get('project_type'),
                primary_language=p.get('primary_language')
            )
            for p in graph_data['nodes']
        ]

        # Build explicit edges
        edges = [
            GraphEdge(
                source=e['source_project_id'],
                target=e['target_project_id'],
                relationship_type=e['relationship_type'],
                is_inferred=False
            )
            for e in graph_data['explicit_edges']
        ]

        # Add inferred edges if requested
        if include_inferred:
            inferred_edges = _compute_inferred_edges(graph_data['nodes'])
            edges.extend(inferred_edges)

        return GraphDataResponse(nodes=nodes, edges=edges)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/graph", response_model=GraphDataResponse)
async def get_project_graph(project_id: int, include_inferred: bool = Query(True)):
    """
    Get graph data for a specific project and its related projects.

    Returns the project and all directly connected projects (1 hop).
    """
    try:
        project = db.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        # Get explicit relationships
        relationships = db.list_project_relationships(project_id)

        # Collect connected project IDs
        connected_ids = {project_id}
        for rel in relationships:
            connected_ids.add(rel['target_project_id'])

        # Get inferred connections if requested
        inferred_edges = []
        if include_inferred:
            # Projects sharing tags
            tag_matches = db.get_projects_sharing_tags(project_id)
            for match in tag_matches:
                connected_ids.add(match['id'])
                inferred_edges.append(GraphEdge(
                    source=project_id,
                    target=match['id'],
                    relationship_type='shared_tags',
                    is_inferred=True
                ))

            # Projects with same language
            if project.get('primary_language'):
                lang_matches = db.get_projects_by_language(project['primary_language'], project_id)
                for match in lang_matches:
                    connected_ids.add(match['id'])
                    # Avoid duplicate edges
                    if not any(e.target == match['id'] and e.relationship_type == 'same_language' for e in inferred_edges):
                        inferred_edges.append(GraphEdge(
                            source=project_id,
                            target=match['id'],
                            relationship_type='same_language',
                            is_inferred=True
                        ))

        # Build nodes for all connected projects
        nodes = []
        for pid in connected_ids:
            p = db.get_project(pid)
            if p:
                nodes.append(GraphNode(
                    id=p['id'],
                    label=p['name'],
                    status=p['status'],
                    project_type=p.get('project_type'),
                    primary_language=p.get('primary_language')
                ))

        # Build explicit edges
        explicit_edges = [
            GraphEdge(
                source=project_id if rel['direction'] == 'outgoing' else rel['target_project_id'],
                target=rel['target_project_id'] if rel['direction'] == 'outgoing' else project_id,
                relationship_type=rel['relationship_type'],
                is_inferred=False
            )
            for rel in relationships
        ]

        edges = explicit_edges + inferred_edges

        return GraphDataResponse(nodes=nodes, edges=edges)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Project Link Endpoints
# =========================

@app.get("/api/projects/{project_id}/links", response_model=LinkListResponse)
async def get_project_links(project_id: int):
    """Get all resource links for a specific project."""
    try:
        project = db.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        links = db.list_project_links(project_id)
        return LinkListResponse(links=links, total=len(links))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/projects/{project_id}/links", response_model=LinkResponse, status_code=201)
async def create_project_link(project_id: int, link: LinkCreate):
    """Add a resource link to a project."""
    try:
        project = db.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        link_id = db.create_link(
            project_id=project_id,
            title=link.title,
            url=link.url,
            link_type=link.link_type
        )

        created_link = db.get_link(link_id)
        return created_link

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/links/{link_id}", response_model=MessageResponse)
async def delete_link(link_id: int):
    """Delete a project link by ID."""
    try:
        success = db.delete_link(link_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Link {link_id} not found")
        return MessageResponse(message=f"Link {link_id} deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Project Template Endpoints
# =========================

@app.get("/api/templates", response_model=TemplateListResponse)
async def list_templates():
    """List all project templates."""
    try:
        templates = db.list_templates()
        return TemplateListResponse(templates=templates, total=len(templates))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/templates/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: int):
    """Get a single project template by ID."""
    try:
        template = db.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/templates", response_model=TemplateResponse, status_code=201)
async def create_template(template: TemplateCreate):
    """Create a new project template."""
    try:
        template_id = db.create_template(
            name=template.name,
            description=template.description,
            default_status=template.default_status,
            default_project_type=template.default_project_type,
            default_primary_language=template.default_primary_language,
            default_stack=template.default_stack,
            default_scope_size=template.default_scope_size,
            default_learning_goal=template.default_learning_goal,
            default_tags=template.default_tags
        )
        created = db.get_template(template_id)
        return created
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/templates/{template_id}", response_model=TemplateResponse)
async def update_template(template_id: int, template: TemplateUpdate):
    """Update a project template."""
    try:
        existing = db.get_template(template_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")

        updates = {k: v for k, v in template.dict().items() if v is not None}
        if updates:
            db.update_template(template_id, **updates)

        updated = db.get_template(template_id)
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/templates/{template_id}", response_model=MessageResponse)
async def delete_template(template_id: int):
    """Delete a project template by ID."""
    try:
        success = db.delete_template(template_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
        return MessageResponse(message=f"Template {template_id} deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Analytics Endpoints
# =========================

@app.get("/api/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    """Get analytics data for charts and dashboards."""
    try:
        data = db.get_analytics()
        return AnalyticsResponse(
            summary=AnalyticsSummary(**data['summary']),
            by_status=[AnalyticsChartItem(**item) for item in data['by_status']],
            by_language=[AnalyticsChartItem(**item) for item in data['by_language']],
            by_type=[AnalyticsChartItem(**item) for item in data['by_type']],
            activity_over_time=[AnalyticsChartItem(**item) for item in data['activity_over_time']],
            progress_distribution=[AnalyticsChartItem(**item) for item in data['progress_distribution']],
            by_tag=[AnalyticsChartItem(**item) for item in data['by_tag']],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _compute_inferred_edges(projects: list) -> list[GraphEdge]:
    """
    Compute inferred edges based on shared attributes.

    Inferred relationship types:
    - same_language: Projects using the same primary language
    """
    edges = []
    seen_pairs = set()

    # Group projects by language
    by_language = {}
    for p in projects:
        lang = p.get('primary_language')
        if lang:
            if lang not in by_language:
                by_language[lang] = []
            by_language[lang].append(p['id'])

    # Create edges for same language
    for lang, project_ids in by_language.items():
        if len(project_ids) > 1:
            for i, pid1 in enumerate(project_ids):
                for pid2 in project_ids[i+1:]:
                    pair = tuple(sorted([pid1, pid2]))
                    if pair not in seen_pairs:
                        seen_pairs.add(pair)
                        edges.append(GraphEdge(
                            source=pid1,
                            target=pid2,
                            relationship_type='same_language',
                            is_inferred=True
                        ))

    return edges


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
