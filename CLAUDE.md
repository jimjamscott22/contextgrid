# CLAUDE.md — ContextGrid AI Assistant Guide

This file provides essential context for AI assistants (Claude, etc.) working in this repository.

---

## Project Overview

**ContextGrid** is a personal, local-first project tracker for developers. It answers four questions:
- What am I building?
- Where does it live?
- What state is it really in?
- What's the next honest step?

It is **not** a SaaS clone or team tool — it's a single-user thinking tool with flexible deployment.

---

## Repository Structure

```
contextgrid/
├── api/                    # FastAPI REST API server
│   ├── server.py           # Main app, all route handlers (~1,018 lines)
│   ├── db.py               # MySQL database operations (~1,249 lines)
│   ├── models.py           # Pydantic request/response models (~400 lines)
│   └── config.py           # API configuration via env vars (~68 lines)
├── src/                    # CLI and client-side logic
│   ├── main.py             # CLI entry point (calls cli.py)
│   ├── cli.py              # All CLI subcommands (~966 lines)
│   ├── models.py           # Unified model interface (dual-mode: API or Direct)
│   ├── db.py               # Database abstraction (SQLite + MySQL backends)
│   ├── config.py           # CLI config via env vars
│   ├── api_client.py       # Sync HTTP client (requests)
│   ├── async_api_client.py # Async HTTP client (httpx)
│   └── async_models.py     # Async model wrappers
├── web/                    # Web UI (server-side rendered)
│   ├── app.py              # Uvicorn/Jinja2 web app (~807 lines)
│   ├── static/css/         # Stylesheets
│   └── templates/          # Jinja2 HTML templates (12 files)
├── scripts/                # Database setup and migration
│   ├── init_db.sql         # SQLite schema
│   ├── init_mysql.sql      # MySQL schema (8 tables)
│   ├── migrate_sqlite_to_mysql.py
│   └── init_database.py
├── tests/
│   ├── test_system.sh      # Integration test suite
│   └── test_db_abstraction.sh  # 16 database tests
├── pyproject.toml          # Project metadata and dependencies
├── .env.example            # Environment variable template
├── requirements.txt        # Pinned dependencies
└── uv.lock                 # uv lockfile (source of truth for deps)
```

---

## Development Environment

### Dependency Management

Uses **`uv`** (not pip, poetry, or pipenv). Always use `uv run` to execute scripts.

```bash
uv sync                  # Install dependencies from uv.lock
uv add <package>         # Add a new dependency
uv run python src/main.py list
```

### Running the Application

**Full Stack (API + Web UI):**
```bash
# Terminal 1: API server
uv run uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Web UI
uv run uvicorn web.app:app --host 0.0.0.0 --port 8001 --reload

# Terminal 3: CLI (uses API by default)
uv run python src/main.py list
```

**Direct Mode (no API server needed):**
```bash
USE_API=false uv run python src/main.py list
```

### Configuration

Copy `.env.example` to `.env` and fill in values:

```
API_HOST=0.0.0.0
API_PORT=8001
DB_HOST=localhost
DB_PORT=3306
DB_NAME=contextgrid
DB_USER=contextgrid_user
DB_PASSWORD=your_secure_password_here
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
```

Key environment variables:
- `USE_API` — `true` (default) routes CLI through API server; `false` connects CLI directly to DB
- `DB_TYPE` — `sqlite` (default local) or `mysql`

---

## Architecture: Dual-Mode Design

The most important architectural concept is the **dual-mode CLI**:

| Mode | How it works | Use case |
|------|-------------|----------|
| **API Mode** (`USE_API=true`) | CLI → HTTP → FastAPI → MySQL | Multi-device, shared server |
| **Direct Mode** (`USE_API=false`) | CLI → DB backend directly | Local-only, no server needed |

`src/models.py` acts as the unified interface — it auto-selects the backend:
```python
if config.USE_API:
    from api_client import get_api_client
    _client = get_api_client()
else:
    from db import get_database_backend
    _db_backend = get_database_backend()
```

**Database abstraction** in `src/db.py` uses an abstract base class:
- `DatabaseBackend` — ABC defining the interface
- `SQLiteBackend` — local SQLite implementation
- `MySQLBackend` — production MySQL implementation
- `get_database_backend()` — factory that auto-selects based on config

---

## Testing

Tests are shell script-based (not pytest), even though pytest is listed as a dev dependency.

```bash
bash tests/test_db_abstraction.sh  # 16 database layer tests
bash test_system.sh                 # System integration tests
```

**Current status:** 16/16 tests passing for SQLite + Direct mode.

When making changes to the database layer or models, run `test_db_abstraction.sh` to verify correctness.

---

## Code Conventions

### Python Style
- **Python 3.8+** — use `from typing import Optional, List, Dict, Tuple` (not PEP 585 built-ins like `list[str]`)
- **PEP 8** — no linter is configured, but follow it manually
- **Type hints** — required on all public functions
- **Docstrings** — required on public functions and classes
- No formatter (black, ruff) configured — maintain consistent style with existing code

### Naming
- Classes: `PascalCase` (e.g., `ProjectCreate`, `DatabaseBackend`)
- Functions/methods: `snake_case` (e.g., `get_project`, `list_projects`)
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_prefix` (e.g., `_db_backend`)
- CLI command handlers: `cmd_<name>` (e.g., `cmd_add`, `cmd_list`)

### CLI Conventions
- Each subcommand is a function named `cmd_<name>(args) -> int`
- Return `0` for success, `1` for error
- Print errors to `sys.stderr`
- Print output to `sys.stdout`

### Error Handling
```python
try:
    result = do_operation()
    return 0
except Exception as e:
    print(f"[ERROR] {e}", file=sys.stderr)
    return 1
```

### Database Queries
- Always use parameterized queries (never f-strings with user data) to prevent SQL injection
- Use context managers for connection management
- Return consistent dict-like structures across SQLite and MySQL backends

### Pydantic Models (API layer)
- Inherit from `ProjectBase` or relevant base class
- Use `Field(pattern=...)` for enum-like string validation
- Status values: `"idea"`, `"active"`, `"paused"`, `"archived"`
- Project types: `"web"`, `"cli"`, `"library"`, `"script"`, `"other"`

---

## Database Schema

8 tables in MySQL (4 base tables in SQLite):

| Table | Purpose |
|-------|---------|
| `projects` | Core project records |
| `project_notes` | Notes per project (CASCADE delete) |
| `project_tags` | Many-to-many tag junction table |
| `project_relationships` | Self-referencing project links |
| `project_links` | External resource URLs |
| `project_commands` | Saved shell commands per project |
| `project_templates` | Template definitions |
| `project_tag_definitions` | Tag metadata |

Key fields in `projects`:
- `status` — `idea | active | paused | archived`
- `progress` — integer 0–100
- `last_worked_at` — timestamp (updated via `touch` command)
- `folder_structure` — text representation of project file tree

---

## API Endpoints

The FastAPI server runs on port 8000 by default. Key endpoints:

```
GET    /api/projects              # List projects (filter/sort via query params)
POST   /api/projects              # Create project
GET    /api/projects/{id}         # Get single project
PUT    /api/projects/{id}         # Full update
PATCH  /api/projects/{id}         # Partial update
DELETE /api/projects/{id}         # Delete project

GET    /api/projects/{id}/notes   # List notes
POST   /api/projects/{id}/notes   # Add note

GET    /api/projects/{id}/tags    # List tags
POST   /api/projects/{id}/tags    # Add tag
DELETE /api/projects/{id}/tags/{tag}  # Remove tag

POST   /api/projects/{id}/touch   # Update last_worked_at timestamp

GET    /api/tags                  # All tags across projects
GET    /api/roadmap               # Roadmap data
GET    /health                    # Health check
```

See `API.md` for full documentation.

---

## Web UI

The web app runs on port 8001 and provides a read-focused UI:
- `/` — Dashboard / home
- `/projects` — Project listing with filters
- `/projects/{id}` — Project detail view
- `/kanban` — Kanban board (drag-and-drop by status)
- `/analytics` — Charts and activity heatmap
- `/graph` — Project relationship graph
- `/tags` — Tag management

Templates are in `web/templates/` using Jinja2. All edits are done via CLI — the web UI is read-only.

---

## Key Files to Know

| File | Why it matters |
|------|---------------|
| `src/models.py` | Entry point for all data operations — routes to API or DB |
| `src/db.py` | Database abstraction — add new DB features here |
| `api/server.py` | All REST endpoints |
| `api/db.py` | All MySQL queries |
| `src/cli.py` | All CLI subcommands |
| `api/models.py` | Pydantic schemas for validation |
| `web/app.py` | Web UI routes and rendering |
| `scripts/init_mysql.sql` | Authoritative schema definition |

---

## What Not to Do

- Do **not** use `pip install` — use `uv add` or `uv sync`
- Do **not** use f-strings with user-controlled data in SQL queries
- Do **not** add linting/formatting configs without discussion — none are currently configured
- Do **not** break the dual-mode design — changes to `src/models.py` must work in both API and Direct modes
- Do **not** use Python 3.10+ type hint syntax (`list[str]`, `str | None`) — project targets 3.8+
- Do **not** push to `master` or `main` directly — use feature branches

---

## Git Workflow

```bash
git checkout -b feature/my-feature
# ... make changes ...
git add <specific-files>
git commit -m "feat: describe what and why"
git push -u origin feature/my-feature
```

Commit message style (mixed in history, but prefer conventional):
- `feat:` — new feature
- `fix:` — bug fix
- `refactor:` — code restructure
- `docs:` — documentation only

---

## Documentation Files

| File | Contents |
|------|---------|
| `README.md` | Setup, architecture, quick-start guides |
| `API.md` | Complete REST API reference |
| `IMPLEMENTATION_SUMMARY.md` | Architecture decisions and database abstraction details |
| `MIGRATION_SUMMARY.md` | SQLite → MySQL migration guide |
| `FUTURE_FEATURES.md` | Planned features and completed milestones |
| `ROADMAP.md` | Auto-generated active project snapshot |
