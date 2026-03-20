# Project Guidelines

## Code Style
- **Python 3.8+** — use `from typing import Optional, List, Dict, Tuple` (not PEP 585 built-ins like `list[str]`)
- **PEP 8** — follow manually, no linter or formatter configured
- **Type hints & Docstrings** — required on all public functions/classes
- **Naming**: Classes: `PascalCase`, Functions/methods: `snake_case`, Constants: `UPPER_SNAKE_CASE`, Private: `_prefix`.
- **CLI Commands**: Handlers named `cmd_<name>(args) -> int` returning `0` (success) or `1` (error). Output to stdout, errors to stderr.
- **Pydantic**: Use `Field(pattern=...)` for enum strings. Inherit from `ProjectBase`.

## Architecture
- **Dual-Mode CLI**: Auto-selects based on `USE_API` environment variable:
  - `API Mode` (`USE_API=true`): CLI → HTTP → FastAPI → MySQL (runs via port 8000/8001)
  - `Direct Mode` (`USE_API=false`): CLI → DB backend directly
- **Database Abstraction**: `DatabaseBackend` ABC in `src/db.py` abstracts SQLite (local) and MySQL (production). `src/models.py` uses either API or Direct mode based on config.
- **Web UI**: Read-focused SSR via Jinja2 & Uvicorn (port 8001). Edits only done via CLI. See `web/templates/base.html` for global UI structures.

## Build and Test
- **Dependencies**: Use **`uv`** (not pip/poetry). Run scripts via `uv run`. 
  - Install: `uv sync`, Add: `uv add <package>`
- **Test**: Shell-script based (not pytest, despite pyproject). 
  - DB layer: `bash tests/test_db_abstraction.sh`
  - Integration: `bash test_system.sh`

## Conventions
- **Database**: 
  - Always use parameterized queries, NO f-strings for user data.
  - Use context managers for DB connection management.
- **Git workflow**: 
  - Use feature branches, no direct push to `master`. 
  - Conventional commits (`feat:`, `fix:`, `refactor:`, `docs:`).

## References
- See `README.md` for setup.
- See `API.md` for REST endpoints.
- See `IMPLEMENTATION_SUMMARY.md` and `MIGRATION_SUMMARY.md` for arch/DB migration context.
- See `ROADMAP.md` and `FUTURE_FEATURES.md` for planned features.
