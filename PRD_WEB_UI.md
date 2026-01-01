# Product Requirement Document: ContextGrid Web UI

**Version:** 1.0  
**Date:** 2026-01-01  
**Status:** In Progress  

---

## 1. Overview

Build a local-first web interface for ContextGrid that provides a modern, intuitive way to view and manage projects while keeping all data local (no cloud, no authentication).

### Core Principles
- **Local-first**: All data stays in local SQLite database
- **Modern & Clean**: Simple, beautiful UI with good UX
- **Read-heavy focus**: Prioritize viewing/browsing over complex editing
- **Progressive enhancement**: Start simple, add features incrementally

---

## 2. Tech Stack

Following your rule #1 (mainstream tech stack):

### Backend
- **FastAPI** - Modern Python web framework (fast, easy, well-documented)
- **Uvicorn** - ASGI server
- Reuse existing `db.py` and `models.py` logic

### Frontend
- **HTML/CSS/Vanilla JS** - Keep it simple, zero build step
- **Modern CSS** (Grid/Flexbox) - No framework needed initially
- Optional later: Add Alpine.js or HTMX for interactivity

### Why this stack?
- ✅ You already know Python
- ✅ FastAPI is beginner-friendly and powerful
- ✅ Can start with simple HTML templates
- ✅ Easy to run locally (`uvicorn main:app`)
- ✅ Zero external dependencies for frontend

---

## 3. Implementation Plan

### Phase 1: Basic FastAPI Setup ✅ (Step 1.1 - 1.3)
**Goal**: Get a working web server serving basic pages

- **Step 1.1**: Install FastAPI and dependencies
- **Step 1.2**: Create basic FastAPI app structure
- **Step 1.3**: Add home page and project list endpoint

### Phase 2: Core Views (Step 2.1 - 2.4)
**Goal**: Display all essential project information

- **Step 2.1**: Project list view (all projects with filters)
- **Step 2.2**: Project detail view (single project with notes)
- **Step 2.3**: Tag browsing view (list tags, filter by tag)
- **Step 2.4**: Status dashboard (overview by status)

### Phase 3: Styling & UX (Step 3.1 - 3.2)
**Goal**: Make it look good and feel modern

- **Step 3.1**: Add modern CSS styling
- **Step 3.2**: Make it responsive (mobile-friendly)

### Phase 4: Basic Interactions (Step 4.1 - 4.3)
**Goal**: Add simple editing capabilities

- **Step 4.1**: Quick actions (touch timestamp, change status)
- **Step 4.2**: Add new project form
- **Step 4.3**: Add note to project

### Phase 5: Polish (Step 5.1 - 5.2)
**Goal**: Make it production-ready

- **Step 5.1**: Error handling and validation
- **Step 5.2**: Add instructions to README

---

## 4. Page Structure (Initial)

### Pages to Build

1. **Home** (`/`)
   - Dashboard overview
   - Quick stats (X active, Y ideas, etc.)
   - Recent activity
   - Quick links

2. **Projects List** (`/projects`)
   - All projects in a grid/list
   - Filter by status, tag
   - Search box
   - Sort options

3. **Project Detail** (`/projects/{id}`)
   - Full project details
   - All metadata
   - Recent notes
   - Quick actions (touch, change status)

4. **Tags** (`/tags`)
   - All tags with counts
   - Click to filter projects

5. **Add Project** (`/projects/new`)
   - Simple form to create project
   - All fields optional except name

---

## 5. API Endpoints Needed

### Read Endpoints
- `GET /` - Home page
- `GET /projects` - List projects (with query params for filtering)
- `GET /projects/{id}` - Project details
- `GET /tags` - List all tags
- `GET /api/projects` - JSON endpoint for AJAX

### Write Endpoints (Phase 4)
- `POST /projects` - Create project
- `POST /projects/{id}/touch` - Update timestamp
- `POST /projects/{id}/notes` - Add note
- `POST /projects/{id}/tags` - Add tag
- `PATCH /projects/{id}` - Update project

---

## 6. Out of Scope (For Now)

These are NOT part of the initial implementation:
- ❌ Authentication/users (it's personal, local-only)
- ❌ Real-time updates / WebSockets
- ❌ Complex editing (use CLI for that)
- ❌ Deleting projects (safety first)
- ❌ Deployment/hosting (local only)
- ❌ Build pipeline/webpack

---

## 7. Success Criteria

The UI is "done" when:
- ✅ Can view all projects with filters
- ✅ Can view individual project details
- ✅ Can browse by tags
- ✅ Can create new projects via web form
- ✅ Can add notes to projects
- ✅ Looks modern and clean
- ✅ Works on mobile devices
- ✅ CLI still works alongside web UI

---

## 8. Next Steps

**START HERE**: 
- Step 1.1: Install FastAPI and create basic app structure
- Test that server runs
- Create simple "Hello World" page

After Step 1.1-1.3 are working, we'll move to a new chat for Step 2.1.

---

## Notes
- Keep the CLI! Web UI is an addition, not a replacement
- All changes should be on the `feature/web-ui` branch
- Test after each step before moving forward
- Bugs compound, so fix them early

