"""
ContextGrid Web UI
FastAPI application for browsing and managing projects
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional
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
        total_count = models.get_projects_count(status=status, search=search)
        projects = models.search_projects(
            search,
            status=status,
            limit=per_page,
            offset=offset,
            sort_by=sort,
            sort_order=order
        )
    elif tag:
        total_count = models.get_projects_count(status=status, tag=tag)
        projects = models.list_projects_by_tag(
            tag,
            status=status,
            limit=per_page,
            offset=offset,
            sort_by=sort,
            sort_order=order
        )
    else:
        total_count = models.get_projects_count(status=status)
        projects = models.list_projects(
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
    all_tags = models.list_all_tags()
    
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
    local_path: Optional[str] = Form(None),
    scope_size: Optional[str] = Form(None),
    learning_goal: Optional[str] = Form(None)
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
                    "local_path": local_path,
                    "scope_size": scope_size,
                    "learning_goal": learning_goal
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
                        "local_path": local_path,
                        "scope_size": scope_size,
                        "learning_goal": learning_goal
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
    local_path = local_path.strip() if local_path and local_path.strip() else None
    scope_size = scope_size.strip() if scope_size and scope_size.strip() else None
    learning_goal = learning_goal.strip() if learning_goal and learning_goal.strip() else None
    
    try:
        # Create the project
        project_id = models.create_project(
            name=name.strip(),
            description=description,
            status=status,
            project_type=project_type,
            primary_language=primary_language,
            stack=stack,
            repo_url=repo_url,
            local_path=local_path,
            scope_size=scope_size,
            learning_goal=learning_goal
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
                    "local_path": local_path,
                    "scope_size": scope_size,
                    "learning_goal": learning_goal
                }
            },
            status_code=500
        )


@app.get("/projects/{project_id}/edit", response_class=HTMLResponse)
async def project_edit_form(request: Request, project_id: int):
    """Show the project edit form."""
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
    local_path: Optional[str] = Form(None),
    scope_size: Optional[str] = Form(None),
    learning_goal: Optional[str] = Form(None)
):
    """Handle project edit form submission."""
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
                    "local_path": local_path,
                    "scope_size": scope_size,
                    "learning_goal": learning_goal
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
                        "local_path": local_path,
                        "scope_size": scope_size,
                        "learning_goal": learning_goal
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
    local_path = local_path.strip() if local_path and local_path.strip() else None
    scope_size = scope_size.strip() if scope_size and scope_size.strip() else None
    learning_goal = learning_goal.strip() if learning_goal and learning_goal.strip() else None

    try:
        updated = models.update_project(
            project_id,
            name=name.strip(),
            description=description,
            status=status,
            project_type=project_type,
            primary_language=primary_language,
            stack=stack,
            repo_url=repo_url,
            local_path=local_path,
            scope_size=scope_size,
            learning_goal=learning_goal
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
                        "local_path": local_path,
                        "scope_size": scope_size,
                        "learning_goal": learning_goal
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
                    "local_path": local_path,
                    "scope_size": scope_size,
                    "learning_goal": learning_goal
                },
                "project": project
            },
            status_code=500
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
    uvicorn.run(app, host="127.0.0.1", port=8080)
