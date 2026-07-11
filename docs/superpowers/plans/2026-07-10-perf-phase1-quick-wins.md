# Performance Phase 1 Quick Wins Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land five low-risk performance quick wins (search debounce, Kanban refetch skip, note indexes, request timing logs, bundle visualizer baseline) without changing API contracts or schema semantics.

**Architecture:** Frontend-only UX/network reductions (Tasks 1–2), idempotent SQL index migrations for hot note/activity queries (Task 3), lightweight ASGI timing middleware (Task 4), and an opt-in Vite analyze build for measuring Phase 2 code-splitting gains (Task 5). Each task is independently shippable and measurable.

**Tech Stack:** React 18, TanStack Query v5, Vitest, FastAPI/Starlette, PyMySQL, MySQL + SQLite schema scripts, Vite 8, `rollup-plugin-visualizer`.

## Global Constraints

- Python 3.8+ typing: `from typing import Optional, List, Dict, Tuple` — no PEP 585 `list[str]` in public signatures.
- No new runtime Python dependencies — stdlib `logging` + existing FastAPI/Starlette only.
- Frontend: prefer a tiny local hook over adding a debounce library.
- Do **not** implement Phase 2 items here (connection pooling, cover_url N+1 fix, route lazy-loading, server-side search, `asyncio.to_thread`).
- Branch: `feat/perf-phase1-quick-wins` (create if missing). Conventional commits after every task.
- Backend tests: `uv run pytest tests/<file> -v`. Frontend tests: `cd frontend && npm test`.
- MySQL index migrations must be idempotent; extend `initialize_database()` to ignore duplicate-index error `1061` (already ignores duplicate-column `1060`).

---

## File Map

| File | Change |
|------|--------|
| `frontend/src/hooks/useDebouncedValue.ts` | Create debounce hook |
| `frontend/src/hooks/useDebouncedValue.test.ts` | Vitest coverage for hook |
| `frontend/src/routes/Projects.tsx` | Debounced search + `placeholderData` |
| `frontend/src/routes/Kanban.tsx` | Remove success-path `invalidateQueries` |
| `scripts/init_mysql.sql` | Add note indexes (idempotent ALTERs) |
| `scripts/init_db.sql` | Add matching SQLite indexes |
| `api/db.py` | Ignore MySQL error 1061 on schema init |
| `api/middleware.py` | Create request-duration logging middleware |
| `api/server.py` | Register timing middleware |
| `tests/test_request_timing.py` | Middleware duration / slow-log tests |
| `frontend/package.json` | Add `rollup-plugin-visualizer` + `build:analyze` |
| `frontend/vite.config.ts` | Opt-in visualizer when `ANALYZE=1` |
| `docs/perf-baselines.md` | Record how to capture / where to paste baseline numbers |

---

### Task 1: Debounce Projects search

**Files:**
- Create: `frontend/src/hooks/useDebouncedValue.ts`
- Create: `frontend/src/hooks/useDebouncedValue.test.ts`
- Modify: `frontend/src/routes/Projects.tsx`

**Interfaces:**
- Produces: `useDebouncedValue<T>(value: T, delayMs?: number): T` — default delay `200`.
- Consumes: existing `qk.projects`, `api.listProjects`, TanStack Query v5 `placeholderData`.

**Why:** `search` is in the query key today, so every keystroke refetches. Backend search is still a no-op (Phase 2), but debounce still cuts wasted round-trips and query-cache churn. `placeholderData` keeps the previous list visible while the debounced query loads.

- [ ] **Step 1: Write the failing hook test**

Create `frontend/src/hooks/useDebouncedValue.test.ts`:

```tsx
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useDebouncedValue } from "./useDebouncedValue";

describe("useDebouncedValue", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it("returns the initial value immediately", () => {
    const { result } = renderHook(() => useDebouncedValue("abc", 200));
    expect(result.current).toBe("abc");
  });

  it("does not update until delay elapses", () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebouncedValue(value, 200),
      { initialProps: { value: "a" } }
    );
    rerender({ value: "ab" });
    rerender({ value: "abc" });
    expect(result.current).toBe("a");
    act(() => {
      vi.advanceTimersByTime(199);
    });
    expect(result.current).toBe("a");
    act(() => {
      vi.advanceTimersByTime(1);
    });
    expect(result.current).toBe("abc");
  });

  it("resets the timer on each change", () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebouncedValue(value, 200),
      { initialProps: { value: "" } }
    );
    rerender({ value: "c" });
    act(() => {
      vi.advanceTimersByTime(150);
    });
    rerender({ value: "co" });
    act(() => {
      vi.advanceTimersByTime(150);
    });
    expect(result.current).toBe("");
    act(() => {
      vi.advanceTimersByTime(50);
    });
    expect(result.current).toBe("co");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && npm test -- src/hooks/useDebouncedValue.test.ts`

Expected: FAIL — cannot resolve `./useDebouncedValue` (or similar module-not-found).

- [ ] **Step 3: Implement the hook**

Create `frontend/src/hooks/useDebouncedValue.ts`:

```ts
import { useEffect, useState } from "react";

/**
 * Return `value` delayed by `delayMs` milliseconds.
 * Updates reset the timer so rapid changes only emit the latest value.
 */
export function useDebouncedValue<T>(value: T, delayMs: number = 200): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const id = window.setTimeout(() => setDebounced(value), delayMs);
    return () => window.clearTimeout(id);
  }, [value, delayMs]);

  return debounced;
}
```

- [ ] **Step 4: Run hook tests — expect PASS**

Run: `cd frontend && npm test -- src/hooks/useDebouncedValue.test.ts`

Expected: PASS (3 tests).

- [ ] **Step 5: Wire debounce + placeholderData into Projects**

In `frontend/src/routes/Projects.tsx`:

1. Add import:

```ts
import { useDebouncedValue } from "@/hooks/useDebouncedValue";
```

2. After `const [search, setSearch] = useState("");` add:

```ts
  const debouncedSearch = useDebouncedValue(search, 200);
```

3. Replace the `projectsQ` block with:

```ts
  const projectsQ = useQuery({
    queryKey: qk.projects({ search: debouncedSearch, status, tag }),
    queryFn: () =>
      api.listProjects({
        search: debouncedSearch || undefined,
        status: status || undefined,
        tag: tag || undefined,
        sort: "recent",
        limit: 50,
      }),
    placeholderData: (prev) => prev,
  });
```

Keep the Input bound to `search` / `setSearch` (immediate typing UX). Do not bind the Input to `debouncedSearch`.

- [ ] **Step 6: Typecheck**

Run: `cd frontend && npm run lint`

Expected: exit 0.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/hooks/useDebouncedValue.ts \
  frontend/src/hooks/useDebouncedValue.test.ts \
  frontend/src/routes/Projects.tsx
git commit -m "$(cat <<'EOF'
perf(frontend): debounce Projects search and keep prior list

EOF
)"
```

---

### Task 2: Skip Kanban refetch after successful optimistic drag

**Files:**
- Modify: `frontend/src/routes/Kanban.tsx` (the `updateMut` `onSuccess` block around lines 81–83)

**Interfaces:**
- Consumes: existing `onMutate` that already patches every `["projects"]` cache entry via `qc.setQueriesData`.
- Produces: drag success leaves optimistic cache as source of truth until natural `staleTime` (10s) expiry; error path still rolls back.

**Why:** `onSuccess → invalidateQueries({ queryKey: ["projects"] })` forces a full list refetch after every drop even though the cache was already updated. That adds latency and can fight the optimistic UI.

- [ ] **Step 1: Remove the success invalidation**

In `frontend/src/routes/Kanban.tsx`, change `updateMut` so it has **no** `onSuccess` handler. Keep `mutationFn`, `onMutate`, and `onError` unchanged. The mutation object should look like:

```ts
  const updateMut = useMutation({
    mutationFn: ({ id, status }: { id: number; status: ProjectStatus }) =>
      api.updateProject(id, { status }),
    onMutate: async ({ id, status }) => {
      await qc.cancelQueries({ queryKey: ["projects"] });
      const prev = qc.getQueriesData({ queryKey: ["projects"] });
      qc.setQueriesData({ queryKey: ["projects"] }, (old: unknown) => {
        const typed = old as { projects?: Project[]; total?: number } | undefined;
        if (!typed?.projects) return old;
        return {
          ...typed,
          projects: typed.projects.map((p) =>
            p.id === id ? { ...p, status } : p
          ),
        };
      });
      return { prev };
    },
    onError: (err, _vars, ctx) => {
      if (ctx?.prev) {
        for (const [key, value] of ctx.prev) qc.setQueryData(key, value);
      }
      toast(`Move failed: ${(err as Error).message}`, "error");
    },
  });
```

- [ ] **Step 2: Typecheck**

Run: `cd frontend && npm run lint`

Expected: exit 0.

- [ ] **Step 3: Manual smoke (if API + frontend running)**

1. Open `/kanban`.
2. Drag a project to another column.
3. Confirm Network tab: one `PUT /api/projects/{id}` and **no** follow-up `GET /api/projects?...` triggered by the drop.
4. Confirm Sidebar (if open) still shows the new status (optimistic patch covers `["projects"]` keys).
5. Force a failed update (optional: stop API mid-drag) and confirm the card rolls back.

If servers are not running, skip manual smoke and note it in the commit body; typecheck is the gate.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/routes/Kanban.tsx
git commit -m "$(cat <<'EOF'
perf(frontend): skip Kanban refetch after optimistic status move

EOF
)"
```

---

### Task 3: Add indexes for note activity and task filters

**Files:**
- Modify: `scripts/init_mysql.sql` (Migrations section)
- Modify: `scripts/init_db.sql` (Indexes section)
- Modify: `api/db.py` (`initialize_database` error handling)

**Interfaces:**
- Produces indexes:
  - MySQL: `idx_project_notes_created_at` on `project_notes(created_at)`
  - MySQL: `idx_project_notes_task_status` on `project_notes(task_status)`
  - MySQL: `idx_project_notes_project_created` on `project_notes(project_id, created_at)`
  - SQLite: same three names via `CREATE INDEX IF NOT EXISTS`
- Consumes: existing heatmap / notes / tasks query patterns in `api/db.py` (`ORDER BY created_at`, `WHERE task_status`, `WHERE created_at >= ...`).

**Why:** Heatmap and note lists filter/sort on `created_at`; `/api/tasks` filters on `task_status`. Today only `project_id` is indexed on `project_notes`.

- [ ] **Step 1: Extend MySQL init to ignore duplicate-index errors**

In `api/db.py`, update the `except` block inside `initialize_database` so both duplicate-column (`1060`) and duplicate-key/index (`1061`) are ignored:

```python
            except pymysql.err.OperationalError as e:
                # Ignore duplicate column (1060) and duplicate key/index (1061)
                # so re-running init is always safe.
                if e.args[0] in (1060, 1061):
                    pass
                else:
                    raise
```

- [ ] **Step 2: Add MySQL index migrations**

Append to the Migrations section of `scripts/init_mysql.sql` (after the existing `ALTER TABLE` lines, before the README Snapshots section):

```sql
-- Performance indexes for notes / activity / tasks (idempotent via 1061 ignore)
CREATE INDEX idx_project_notes_created_at ON project_notes (created_at);
CREATE INDEX idx_project_notes_task_status ON project_notes (task_status);
CREATE INDEX idx_project_notes_project_created ON project_notes (project_id, created_at);
```

Do **not** put these inside the original `CREATE TABLE project_notes` block — existing databases already have that table, so only `CREATE INDEX` / `ALTER` statements run as migrations.

- [ ] **Step 3: Add SQLite indexes**

Append to the Indexes section of `scripts/init_db.sql`:

```sql
CREATE INDEX IF NOT EXISTS idx_project_notes_created_at ON project_notes(created_at);
CREATE INDEX IF NOT EXISTS idx_project_notes_task_status ON project_notes(task_status);
CREATE INDEX IF NOT EXISTS idx_project_notes_project_created ON project_notes(project_id, created_at);
```

- [ ] **Step 4: Verify init is idempotent against a live MySQL (if available)**

If MySQL is configured via `.env`:

```bash
uv run python -c "from api import db; db.initialize_database(); db.initialize_database(); print('ok')"
```

Expected: prints `ok` with no traceback (second run hits 1061 and continues).

If MySQL is unavailable, skip and rely on code review of the 1061 handling.

- [ ] **Step 5: Commit**

```bash
git add api/db.py scripts/init_mysql.sql scripts/init_db.sql
git commit -m "$(cat <<'EOF'
perf(db): index project_notes created_at and task_status

EOF
)"
```

---

### Task 4: Request-duration logging middleware

**Files:**
- Create: `api/middleware.py`
- Modify: `api/server.py` (register middleware after CORS)
- Create: `tests/test_request_timing.py`

**Interfaces:**
- Produces: `RequestTimingMiddleware` — logs `method path status duration_ms` at INFO; logs at WARNING when `duration_ms >= SLOW_REQUEST_MS` (default `200`, overridable via env `SLOW_REQUEST_MS`).
- Register with `app.add_middleware(RequestTimingMiddleware)` **after** CORS so timing wraps the app innermost relative to CORS (Starlette: last added = outermost). Add timing **before** CORS in source order so CORS stays outermost:

```python
app.add_middleware(RequestTimingMiddleware)  # added first → inner
app.add_middleware(CORSMiddleware, ...)      # added second → outer
```

If CORS is already registered, insert the timing middleware registration **above** the existing `app.add_middleware(CORSMiddleware, ...)` block and leave CORS as-is.

**Why:** No observability today. Duration logs give a Phase 1 baseline and catch regressions before Phase 2 pooling work.

- [ ] **Step 1: Write failing middleware tests**

Create `tests/test_request_timing.py`:

```python
"""Tests for request-duration logging middleware."""
from typing import List
import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.middleware import RequestTimingMiddleware


def _make_app(slow_ms: int = 200) -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestTimingMiddleware, slow_ms=slow_ms)

    @app.get("/api/fast")
    async def fast():
        return {"ok": True}

    @app.get("/api/slow")
    async def slow():
        import time
        time.sleep(0.05)
        return {"ok": True}

    return app


def test_logs_duration_for_successful_request(caplog):
    app = _make_app()
    client = TestClient(app)
    with caplog.at_level(logging.INFO, logger="api.timing"):
        response = client.get("/api/fast")
    assert response.status_code == 200
    matching: List[str] = [
        r.getMessage() for r in caplog.records if r.name == "api.timing"
    ]
    assert matching, "expected a timing log record"
    msg = matching[-1]
    assert "GET" in msg
    assert "/api/fast" in msg
    assert "200" in msg
    assert "ms" in msg


def test_warns_when_request_exceeds_threshold(caplog):
    app = _make_app(slow_ms=10)
    client = TestClient(app)
    with caplog.at_level(logging.WARNING, logger="api.timing"):
        response = client.get("/api/slow")
    assert response.status_code == 200
    warnings: List[str] = [
        r.getMessage()
        for r in caplog.records
        if r.name == "api.timing" and r.levelno >= logging.WARNING
    ]
    assert warnings, "expected a slow-request warning"
    assert "/api/slow" in warnings[-1]
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `uv run pytest tests/test_request_timing.py -v`

Expected: FAIL — `ModuleNotFoundError: No module named 'api.middleware'` (or import error for `RequestTimingMiddleware`).

- [ ] **Step 3: Implement middleware**

Create `api/middleware.py`:

```python
"""ASGI middleware for ContextGrid API performance observability."""

from typing import Callable, Optional
import logging
import os
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("api.timing")


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Log method, path, status, and duration for every HTTP request."""

    def __init__(self, app, slow_ms: Optional[int] = None):
        """
        Args:
            app: ASGI application.
            slow_ms: Duration threshold for WARNING logs. Defaults to
                ``SLOW_REQUEST_MS`` env (200 if unset).
        """
        super().__init__(app)
        if slow_ms is None:
            slow_ms = int(os.getenv("SLOW_REQUEST_MS", "200"))
        self.slow_ms = slow_ms

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Measure wall-clock time around the downstream app."""
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000.0
        msg = (
            f"{request.method} {request.url.path} "
            f"{response.status_code} {duration_ms:.1f}ms"
        )
        if duration_ms >= self.slow_ms:
            logger.warning("slow request: %s", msg)
        else:
            logger.info(msg)
        return response
```

- [ ] **Step 4: Register middleware in `api/server.py`**

1. Add import near the other `api` imports:

```python
from api.middleware import RequestTimingMiddleware
```

2. **Above** the existing `app.add_middleware(CORSMiddleware, ...)` block, add:

```python
# Innermost relative to CORS: records full handler + DB time
app.add_middleware(RequestTimingMiddleware)
```

Leave the CORS block unchanged and immediately below.

- [ ] **Step 5: Run middleware tests — expect PASS**

Run: `uv run pytest tests/test_request_timing.py -v`

Expected: PASS (2 tests).

- [ ] **Step 6: Document the env knob in `.env.example`**

Append:

```
# Log WARNING for requests slower than this many milliseconds (default 200).
# SLOW_REQUEST_MS=200
```

- [ ] **Step 7: Commit**

```bash
git add api/middleware.py api/server.py tests/test_request_timing.py .env.example
git commit -m "$(cat <<'EOF'
perf(api): log request duration and warn on slow handlers

EOF
)"
```

---

### Task 5: Bundle visualizer baseline

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/vite.config.ts`
- Create: `docs/perf-baselines.md`

**Interfaces:**
- Produces: `npm run build:analyze` → writes `frontend/dist/stats.html` when `ANALYZE=1`.
- Does **not** change default `npm run build` output (visualizer off unless env set).

**Why:** Phase 2 code-splitting needs a before/after number. Capture once now; paste sizes into `docs/perf-baselines.md`.

- [ ] **Step 1: Install the visualizer as a frontend devDependency**

Run from `frontend/`:

```bash
npm install -D rollup-plugin-visualizer
```

- [ ] **Step 2: Gate the plugin on `ANALYZE=1`**

Update `frontend/vite.config.ts` to:

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { visualizer } from "rollup-plugin-visualizer";
/// <reference types="vitest" />

export default defineConfig({
  plugins: [
    react(),
    process.env.ANALYZE === "1" &&
      visualizer({
        filename: "dist/stats.html",
        gzipSize: true,
        brotliSize: true,
        open: false,
      }),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    host: "0.0.0.0",
    proxy: {
      "/api": {
        target: process.env.API_ENDPOINT || "http://localhost:8003",
        changeOrigin: true,
      },
      "/uploads": {
        target: process.env.API_ENDPOINT || "http://localhost:8003",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
  test: {
    environment: "jsdom",
    globals: true,
  },
});
```

- [ ] **Step 3: Add the analyze script**

In `frontend/package.json` `scripts`, add:

```json
    "build:analyze": "ANALYZE=1 tsc -b && ANALYZE=1 vite build"
```

Keep existing `build`, `dev`, `lint`, `test` scripts unchanged.

- [ ] **Step 4: Create baseline doc**

Create `docs/perf-baselines.md`:

```markdown
# Performance Baselines

Capture numbers before/after optimization work. Do not commit generated
`frontend/dist/stats.html` (build artifact).

## How to capture frontend bundle baseline

```bash
cd frontend
npm run build:analyze
ls -lh dist/assets/*.js
# Open dist/stats.html in a browser for the treemap
```

## Phase 1 baseline (pre code-splitting)

| Date | Branch / commit | Largest JS asset (raw) | Largest JS asset (gzip, from stats.html) | Notes |
|------|-----------------|------------------------|------------------------------------------|-------|
| YYYY-MM-DD | feat/perf-phase1-quick-wins | _fill after build:analyze_ | _fill_ | Monolithic App chunk; mermaid/reactflow/recharts eager |

## Phase 2 target (after route lazy-loading)

| Date | Branch / commit | Largest JS asset (raw) | Initial route JS (gzip) | Notes |
|------|-----------------|------------------------|-------------------------|-------|
| | | | | Graph/Analytics/Diagrams in separate chunks |
```

- [ ] **Step 5: Run analyze build and fill the Phase 1 row**

Run:

```bash
cd frontend && npm run build:analyze
ls -lh dist/assets/*.js
```

Edit `docs/perf-baselines.md` Phase 1 table with the real date, commit SHA (or `WIP`), largest asset size from `ls`, and gzip size from `dist/stats.html` if available.

Confirm `dist/stats.html` exists. Do **not** `git add` `frontend/dist/`.

- [ ] **Step 6: Ensure dist stays ignored**

Confirm `frontend/dist` (or `dist`) is covered by `.gitignore`. If `stats.html` would be committed, do not add it.

- [ ] **Step 7: Typecheck + default build still works**

```bash
cd frontend && npm run lint && npm run build
```

Expected: exit 0; no `stats.html` required for default build (ANALYZE unset).

- [ ] **Step 8: Commit**

```bash
git add frontend/package.json frontend/package-lock.json \
  frontend/vite.config.ts docs/perf-baselines.md
git commit -m "$(cat <<'EOF'
chore(frontend): add opt-in bundle visualizer for perf baselines

EOF
)"
```

---

## Verification (end of Phase 1)

Run the full quick-win gate before merging or pausing:

```bash
# Backend
uv run pytest tests/test_request_timing.py -v

# Frontend
cd frontend && npm test && npm run lint && npm run build
```

Optional manual checks:

| Check | Expected |
|-------|----------|
| Type in Projects search | Network quiet for ~200ms, then one list request |
| Kanban drag | PUT only; no immediate projects GET |
| API request log | `GET /api/health 200 X.Xms` lines in uvicorn output |
| `npm run build:analyze` | `frontend/dist/stats.html` + filled baseline row |

---

## Out of scope (defer to Phase 2+)

- MySQL connection pooling (`DB_POOL_SIZE` wiring)
- Screenshot / cover_url N+1 fix
- Route-level `React.lazy` for Graph / Analytics / Diagrams
- Server-side project search + honest `total` pagination
- `asyncio.to_thread` for sync DB calls
- TTL caches for analytics / heatmap / graph
- Skeleton loaders / Home progressive render

---

## Self-review checklist

| Spec item (Phase 1 review) | Task |
|----------------------------|------|
| Debounce Projects search | Task 1 |
| Kanban skip invalidate on success | Task 2 |
| Note/activity indexes | Task 3 |
| Request-duration logging | Task 4 |
| vite visualizer baseline | Task 5 |
| No Phase 2 scope creep | Explicit out-of-scope section |
| Idempotent MySQL indexes | Task 3 steps 1–2 (1061) |
