"""
ContextGrid Web UI
FastAPI application for browsing and managing projects
"""

from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional, List, Dict
import os
import sys
import shutil
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE, override=True)

# Add src to path to import our existing models
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import async_models as models

# Initialize FastAPI app
app = FastAPI(
    title="ContextGrid",
    description="Personal project tracker - Local-first web interface",
    version="1.0.0"
)

# Close the shared async API client when the app shuts down
app.add_event_handler("shutdown", models.aclose_client)

# Setup static files and templates
STATIC_DIR = Path(__file__).parent / "static"
TEMPLATE_DIR = Path(__file__).parent / "templates"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
templates.env.globals["api_base_url"] = os.getenv("API_ENDPOINT", "http://localhost:8000").rstrip("/")

SCREENSHOTS_DIR = STATIC_DIR / "screenshots"


def get_project_screenshots(project_id: int) -> List[Dict[str, str]]:
    """Return screenshots for a project from web/static/screenshots/<project_id>/."""
    project_dir = SCREENSHOTS_DIR / str(project_id)
    if not project_dir.is_dir():
        return []

    allowed_exts = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
    screenshots = []
    for path in sorted(project_dir.iterdir(), key=lambda p: p.name.lower()):
        if not path.is_file() or path.suffix.lower() not in allowed_exts:
            continue
        label = path.stem.replace("_", " ").replace("-", " ").strip()
        screenshots.append(
            {
                "url": f"/static/screenshots/{project_id}/{path.name}",
                "label": label,
                "filename": path.name,
            }
        )

    return screenshots


# =========================
# Routes
# =========================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with dashboard overview."""
    # Get project counts by status
    all_projects = await models.list_projects()
    
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

    # Add screenshots to each project
    for project in recent_projects:
        project['screenshots'] = get_project_screenshots(project['id'])

    # Get activity heatmap data
    try:
        heatmap_data = await models.get_activity_heatmap(days=365)
    except Exception as e:
        print(f"Warning: Failed to fetch heatmap data: {e}")
        heatmap_data = {"days": [], "streak": {"current_streak": 0, "longest_streak": 0}}

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "status_counts": status_counts,
            "total_projects": len(all_projects),
            "recent_projects": recent_projects,
            "heatmap_data": heatmap_data
        }
    )


@app.get("/projects", response_class=HTMLResponse)
async def projects_list(
    request: Request,
    status: str = None,
    tag: str = None,
    search: str = None,
    page: int = 1,
    sort: str = "last_worked_at",
    order: str = "desc"
):
    """List all projects with optional filtering, search, pagination, and sorting."""
    # Validate page number
    if page < 1:
        page = 1
    
    # Pagination settings
    per_page = 15
    offset = (page - 1) * per_page
    
    # Fetch projects based on filters
    if search and search.strip():
        # Search projects with pagination
        total_count = await models.get_projects_count(status, None, search)
        projects = await models.search_projects(
            search,
            status=status,
            limit=per_page,
            offset=offset,
            sort_by=sort,
            sort_order=order
        )
    elif tag:
        total_count = await models.get_projects_count(status, tag)
        projects = await models.list_projects_by_tag(
            tag,
            status=status,
            limit=per_page,
            offset=offset,
            sort_by=sort,
            sort_order=order
        )
    else:
        total_count = await models.get_projects_count(status, None)
        projects = await models.list_projects(
            status=status,
            limit=per_page,
            offset=offset,
            sort_by=sort,
            sort_order=order
        )
    
    # Calculate pagination info
    total_pages = (total_count + per_page - 1) // per_page  # Ceiling division
    has_prev = page > 1
    has_next = page < total_pages
    
    # Get all tags for filter UI
    all_tags = await models.list_all_tags()
    
    return templates.TemplateResponse(
        "projects.html",
        {
            "request": request,
            "projects": projects,
            "all_tags": all_tags,
            "current_status": status,
            "current_tag": tag,
            "search_query": search,
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "has_prev": has_prev,
            "has_next": has_next,
            "sort": sort,
            "order": order
        }
    )


@app.get("/projects/new", response_class=HTMLResponse)
async def project_new_form(request: Request):
    """Show the new project creation form."""
    return templates.TemplateResponse(
        "project_form.html",
        {
            "request": request,
            "error": None,
            "form_data": {}
        }
    )


@app.post("/projects/new")
async def project_create(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    status: str = Form("idea"),
    project_type: Optional[str] = Form(None),
    primary_language: Optional[str] = Form(None),
    stack: Optional[str] = Form(None),
    repo_url: Optional[str] = Form(None),
    scope_size: Optional[str] = Form(None),
    learning_goal: Optional[str] = Form(None),
    progress: Optional[int] = Form(0)
):
    """Handle project creation form submission."""
    # Validate required fields
    if not name or not name.strip():
        return templates.TemplateResponse(
            "project_form.html",
            {
                "request": request,
                "error": "Project name is required",
                "form_data": {
                    "name": name,
                    "description": description,
                    "status": status,
                    "project_type": project_type,
                    "primary_language": primary_language,
                    "stack": stack,
                    "repo_url": repo_url,
                    "scope_size": scope_size,
                    "learning_goal": learning_goal,
                    "progress": progress
                }
            },
            status_code=400
        )

    # Validate URL format if provided
    if repo_url and repo_url.strip():
        repo_url = repo_url.strip()
        if not (repo_url.startswith("http://") or repo_url.startswith("https://") or repo_url.startswith("git@")):
            return templates.TemplateResponse(
                "project_form.html",
                {
                    "request": request,
                    "error": "Repository URL must start with http://, https://, or git@",
                    "form_data": {
                        "name": name,
                        "description": description,
                        "status": status,
                        "project_type": project_type,
                        "primary_language": primary_language,
                        "stack": stack,
                        "repo_url": repo_url,
                        "scope_size": scope_size,
                        "learning_goal": learning_goal,
                        "progress": progress
                    }
                },
                status_code=400
            )

    # Clean up empty strings to None
    description = description.strip() if description and description.strip() else None
    project_type = project_type.strip() if project_type and project_type.strip() else None
    primary_language = primary_language.strip() if primary_language and primary_language.strip() else None
    stack = stack.strip() if stack and stack.strip() else None
    repo_url = repo_url.strip() if repo_url and repo_url.strip() else None
    scope_size = scope_size.strip() if scope_size and scope_size.strip() else None
    learning_goal = learning_goal.strip() if learning_goal and learning_goal.strip() else None
    
    try:
        # Create the project
        project_id = await models.create_project(
            name=name.strip(),
            description=description,
            status=status,
            project_type=project_type,
            primary_language=primary_language,
            stack=stack,
            repo_url=repo_url,
            local_path=None,
            scope_size=scope_size,
            learning_goal=learning_goal,
            progress=max(0, min(100, progress or 0))
        )
        
        # Redirect to the new project's detail page
        return RedirectResponse(url=f"/projects/{project_id}", status_code=303)
        
    except Exception as e:
        return templates.TemplateResponse(
            "project_form.html",
            {
                "request": request,
                "error": f"Error creating project: {str(e)}",
                "form_data": {
                    "name": name,
                    "description": description,
                    "status": status,
                    "project_type": project_type,
                    "primary_language": primary_language,
                    "stack": stack,
                    "repo_url": repo_url,
                    "scope_size": scope_size,
                    "learning_goal": learning_goal,
                    "progress": progress
                }
            },
            status_code=500
        )


@app.get("/projects/{project_id}/edit", response_class=HTMLResponse)
async def project_edit_form(request: Request, project_id: int):
    """Show the project edit form."""
    project = await models.get_project(project_id)

    if not project:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": f"Project {project_id} not found"
            },
            status_code=404
        )

    return templates.TemplateResponse(
        "project_edit.html",
        {
            "request": request,
            "error": None,
            "form_data": project,
            "project": project
        }
    )


@app.post("/projects/{project_id}/edit")
async def project_update(
    request: Request,
    project_id: int,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    status: str = Form("idea"),
    project_type: Optional[str] = Form(None),
    primary_language: Optional[str] = Form(None),
    stack: Optional[str] = Form(None),
    repo_url: Optional[str] = Form(None),
    scope_size: Optional[str] = Form(None),
    learning_goal: Optional[str] = Form(None),
    progress: Optional[int] = Form(0)
):  
    """Handle project edit form submission."""
    project = await models.get_project(project_id)
    if not project:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": f"Project {project_id} not found"
            },
            status_code=404
        )

    if not name or not name.strip():
        return templates.TemplateResponse(
            "project_edit.html",
            {
                "request": request,
                "error": "Project name is required",
                "form_data": {
                    "id": project_id,
                    "name": name,
                    "description": description,
                    "status": status,
                    "project_type": project_type,
                    "primary_language": primary_language,
                    "stack": stack,
                    "repo_url": repo_url,
                    "scope_size": scope_size,
                    "learning_goal": learning_goal,
                    "progress": progress
                },
                "project": project
            },
            status_code=400
        )

    if repo_url and repo_url.strip():
        repo_url = repo_url.strip()
        if not (repo_url.startswith("http://") or repo_url.startswith("https://") or repo_url.startswith("git@")):
            return templates.TemplateResponse(
                "project_edit.html",
                {
                    "request": request,
                    "error": "Repository URL must start with http://, https://, or git@",
                    "form_data": {
                        "id": project_id,
                        "name": name,
                        "description": description,
                        "status": status,
                        "project_type": project_type,
                        "primary_language": primary_language,
                        "stack": stack,
                        "repo_url": repo_url,
                        "scope_size": scope_size,
                        "learning_goal": learning_goal,
                        "progress": progress
                    },
                    "project": project
                },
                status_code=400
            )

    description = description.strip() if description and description.strip() else None
    project_type = project_type.strip() if project_type and project_type.strip() else None
    primary_language = primary_language.strip() if primary_language and primary_language.strip() else None
    stack = stack.strip() if stack and stack.strip() else None
    repo_url = repo_url.strip() if repo_url and repo_url.strip() else None
    scope_size = scope_size.strip() if scope_size and scope_size.strip() else None
    learning_goal = learning_goal.strip() if learning_goal and learning_goal.strip() else None

    try:
        updated = await models.update_project(
            project_id,
            name=name.strip(),
            description=description,
            status=status,
            project_type=project_type,
            primary_language=primary_language,
            stack=stack,
            repo_url=repo_url,
            local_path=None,
            scope_size=scope_size,
            learning_goal=learning_goal,
            progress=max(0, min(100, progress or 0)),
        )

        if not updated:
            return templates.TemplateResponse(
                "project_edit.html",
                {
                    "request": request,
                    "error": "No changes were saved",
                    "form_data": {
                        "id": project_id,
                        "name": name,
                        "description": description,
                        "status": status,
                        "project_type": project_type,
                        "primary_language": primary_language,
                        "stack": stack,
                        "repo_url": repo_url,
                        "scope_size": scope_size,
                        "learning_goal": learning_goal,
                        "progress": progress
                    },
                    "project": project
                },
                status_code=400
            )

        return RedirectResponse(url=f"/projects/{project_id}", status_code=303)

    except Exception as e:
        return templates.TemplateResponse(
            "project_edit.html",
            {
                "request": request,
                "error": f"Error updating project: {str(e)}",
                "form_data": {
                    "id": project_id,
                    "name": name,
                    "description": description,
                    "status": status,
                    "project_type": project_type,
                    "primary_language": primary_language,
                    "stack": stack,
                    "repo_url": repo_url,
                    "scope_size": scope_size,
                    "learning_goal": learning_goal,
                    "progress": progress
                },
                "project": project
            },
            status_code=500
        )


@app.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_detail(request: Request, project_id: int):
    """Show detailed view of a single project."""
    project = await models.get_project(project_id)
    
    if not project:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": f"Project {project_id} not found"
            },
            status_code=404
        )
    
    # Update last viewed timestamp
    try:
        await models.update_last_worked(project_id)
        # Refresh project data to get updated timestamp
        project = await models.get_project(project_id)
    except Exception as e:
        # Don't fail the request if touch fails, just log it
        print(f"Warning: Failed to update last_worked_at: {e}")
    
    # Get tags and notes via async client
    project_tags = await models.list_project_tags(project_id)
    notes = await models.list_notes(project_id)
    
    screenshots = get_project_screenshots(project_id)

    return templates.TemplateResponse(
        "project_detail.html",
        {
            "request": request,
            "project": project,
            "tags": project_tags,
            "notes": notes,
            "screenshots": screenshots,
        }
    )


@app.post("/projects/{project_id}/delete")
async def project_delete(project_id: int):
    """Delete a project."""
    try:
        await models.delete_project(project_id)
        return RedirectResponse(url="/projects", status_code=303)
    except Exception as e:
        return RedirectResponse(url="/projects", status_code=303)


@app.post("/projects/{project_id}/screenshots")
async def project_upload_screenshot(
    request: Request,
    project_id: int,
    file: UploadFile = File(...)
):
    """Handle screenshot upload."""
    try:
        # Create screenshots directory for project if it doesn't exist
        project_dir = SCREENSHOTS_DIR / str(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate file type
        if not file.content_type.startswith("image/"):
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "error": "File must be an image"
                },
                status_code=400
            )
            
        # Secure filename (simple version)
        filename = Path(file.filename).name
        file_path = project_dir / filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return RedirectResponse(url=f"/projects/{project_id}", status_code=303)
        
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": f"Error uploading screenshot: {str(e)}"
            },
            status_code=500
        )


@app.post("/projects/{project_id}/screenshots/{filename}/delete")
async def project_delete_screenshot(
    request: Request,
    project_id: int,
    filename: str
):
    """Handle screenshot deletion."""
    try:
        # Construct the file path
        project_dir = SCREENSHOTS_DIR / str(project_id)
        file_path = project_dir / filename
        
        # Security check: ensure the file is within the project directory
        if not file_path.resolve().is_relative_to(project_dir.resolve()):
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "error": "Invalid file path"
                },
                status_code=400
            )
        
        # Delete the file if it exists
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
        
        return RedirectResponse(url=f"/projects/{project_id}", status_code=303)
        
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": f"Error deleting screenshot: {str(e)}"
            },
            status_code=500
        )


@app.get("/tags", response_class=HTMLResponse)
async def tags_list(request: Request):
    """Browse all tags."""
    all_tags = await models.list_all_tags()

    return templates.TemplateResponse(
        "tags.html",
        {
            "request": request,
            "tags": all_tags
        }
    )


@app.get("/graph", response_class=HTMLResponse)
async def graph_view(request: Request):
    """Full project dependency graph visualization."""
    return templates.TemplateResponse(
        "graph.html",
        {
            "request": request
        }
    )


@app.get("/kanban", response_class=HTMLResponse)
async def kanban_board(request: Request):
    """Kanban board view - projects organized by status columns."""
    all_projects = await models.list_projects()

    columns = {
        "idea": [],
        "active": [],
        "paused": [],
        "archived": [],
    }

    for project in all_projects:
        status = project.get("status", "idea")
        if status in columns:
            columns[status].append(project)

    return templates.TemplateResponse(
        "kanban.html",
        {
            "request": request,
            "columns": columns,
        }
    )


@app.post("/api/kanban/move")
async def kanban_move(request: Request):
    """Update a project's status via drag-and-drop on the kanban board."""
    body = await request.json()
    project_id = body.get("project_id")
    new_status = body.get("status")

    valid_statuses = {"idea", "active", "paused", "archived"}
    if not project_id or new_status not in valid_statuses:
        return JSONResponse(
            {"error": "Invalid project_id or status"},
            status_code=400
        )

    try:
        updated = await models.update_project(int(project_id), status=new_status)
        if not updated:
            return JSONResponse(
                {"error": "Failed to update project"},
                status_code=500
            )
        return JSONResponse({"ok": True, "project_id": project_id, "status": new_status})
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
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
    uvicorn.run(app, host="127.0.0.1", port=8081)
