"""
ContextGrid Web UI
FastAPI application for browsing and managing projects
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import sys

# Add src to path to import our existing models
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import models

# Initialize FastAPI app
app = FastAPI(
    title="ContextGrid",
    description="Personal project tracker - Local-first web interface",
    version="1.0.0"
)

# Setup static files and templates
STATIC_DIR = Path(__file__).parent / "static"
TEMPLATE_DIR = Path(__file__).parent / "templates"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


# =========================
# Routes
# =========================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with dashboard overview."""
    # Get project counts by status
    all_projects = models.list_projects()
    
    status_counts = {
        "active": 0,
        "idea": 0,
        "paused": 0,
        "archived": 0
    }
    
    for project in all_projects:
        status = project.get("status", "idea")
        if status in status_counts:
            status_counts[status] += 1
    
    # Get recent projects (last worked on)
    recent_projects = all_projects[:5]  # Already sorted by last_worked_at
    
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "status_counts": status_counts,
            "total_projects": len(all_projects),
            "recent_projects": recent_projects
        }
    )


@app.get("/projects", response_class=HTMLResponse)
async def projects_list(request: Request, status: str = None, tag: str = None):
    """List all projects with optional filtering."""
    # Fetch projects based on filters
    if tag:
        projects = models.list_projects_by_tag(tag, status=status)
    else:
        projects = models.list_projects(status=status)
    
    # Get all tags for filter UI
    all_tags = models.list_all_tags()
    
    return templates.TemplateResponse(
        "projects.html",
        {
            "request": request,
            "projects": projects,
            "all_tags": all_tags,
            "current_status": status,
            "current_tag": tag
        }
    )


@app.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_detail(request: Request, project_id: int):
    """Show detailed view of a single project."""
    project = models.get_project(project_id)
    
    if not project:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": f"Project {project_id} not found"
            },
            status_code=404
        )
    
    # Get tags and notes
    project_tags = models.list_project_tags(project_id)
    notes = models.list_notes(project_id)
    
    return templates.TemplateResponse(
        "project_detail.html",
        {
            "request": request,
            "project": project,
            "tags": project_tags,
            "notes": notes
        }
    )


@app.get("/tags", response_class=HTMLResponse)
async def tags_list(request: Request):
    """Browse all tags."""
    all_tags = models.list_all_tags()
    
    return templates.TemplateResponse(
        "tags.html",
        {
            "request": request,
            "tags": all_tags
        }
    )


# =========================
# Health Check
# =========================

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "app": "ContextGrid"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

