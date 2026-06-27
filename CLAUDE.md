# ContextGrid

Local-first personal project tracker. FastAPI backend + dual frontend (React SPA + legacy Jinja2 SSR).

## Commands

### API Server
```bash
# Windows
start.bat
# Linux/Mac
bash start.sh
# Direct
uv run uvicorn api.server:app --host 0.0.0.0 --port 8003
```

### Frontend (React SPA)
```bash
cd frontend
npm run dev        # Dev server on :5173, proxies /api/* to :8003
npm run build      # Type-check + Vite build → frontend/dist/
npm run lint       # tsc --noEmit only (no ESLint configured)
```

### Build for Production
```bash
bash scripts/build_frontend.sh   # npm install + npm run build
# Then serve via API server — SPA served from /, /api/* untouched
```

### Dependencies & CLI
```bash
uv sync                  # Install all deps
uv add <package>         # Add a dependency
uv run python src/main.py <cmd>   # Run CLI
python cg.py <cmd>                # Shortcut: root-level CLI entry point
```

### Tests
```bash
bash tests/test_db_abstraction.sh   # DB layer tests
bash test_system.sh                 # Integration tests
uv run pytest                       # Python unit/security tests (42 tests)
```

## Architecture

**Dual-Mode Backend** — controlled by `USE_API` env var:
- `USE_API=true` (default): CLI → HTTP → FastAPI → MySQL
- `USE_API=false`: CLI → DB directly (SQLite for local dev)

**Dual Frontend** — both consume the same FastAPI:
- `frontend/` — React SPA (Vite + TS + Tailwind + TanStack Query + dnd-kit). Full editing, Kanban drag-drop, optimistic mutations.
- `web/` — Legacy Jinja2 SSR on :8081. Read-focused; edits via CLI only.

**Key entry points:**
- `api/server.py` — FastAPI app (serves SPA in prod via catch-all to `index.html`)
- `api/db.py` / `api/models.py` — API-layer DB and Pydantic models
- `src/db.py` — `DatabaseBackend` ABC (SQLite + MySQL implementations)
- `src/models.py` — mode-switching models (API or Direct based on config)
- `src/cli.py` — CLI handlers (`cmd_<name>(args) -> int`)
- `frontend/src/App.tsx` — React router root

## Environment

Copy `.env.example` → `.env`:

| Variable | Purpose | Default |
|----------|---------|---------|
| `API_HOST` | Server bind host | `0.0.0.0` |
| `API_PORT` | Server port | `8003` (overrides example's 8001) |
| `USE_API` | Backend mode | `true` |
| `DB_HOST/PORT/NAME/USER/PASSWORD` | MySQL connection | — |
| `DB_POOL_SIZE` / `DB_MAX_OVERFLOW` | Connection pool | 5 / 10 |

## Code Style

- **Python 3.8+**: use `from typing import Optional, List, Dict` — not PEP 585 `list[str]`
- Type hints + docstrings required on all public functions/classes
- CLI handlers: `cmd_<name>(args) -> int`, return `0` success / `1` error; stdout for output, stderr for errors
- Pydantic models inherit from `ProjectBase`; use `Field(pattern=...)` for enum strings
- Always parameterized queries — no f-strings with user data
- Use context managers for DB connections

## Git Workflow

- Feature branches only — no direct push to `main`
- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`

## Gotchas

- The `.env` overrides `API_PORT` to `8003`; `.env.example` shows `8001` — trust `.env`
- `scripts/build_frontend.sh` must be run before the API server can serve the SPA in production
- `web/` (Jinja2) runs on :8081 separately from the API — it's not built, just served by its own process
- Shell scripts (`test_db_abstraction.sh`, `test_system.sh`) are integration tests; `tests/` also has pytest unit tests — run both suites
