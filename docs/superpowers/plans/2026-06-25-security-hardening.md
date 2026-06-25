# Security Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close six isolated security gaps (CORS, SVG uploads, upload/README size caps, Mermaid XSS, URL validation) without changing storage mechanics, schema, or user-facing behavior for legitimate use.

**Architecture:** Each fix is self-contained: config changes feed backend fixes (Tasks 1-5), the frontend fix (Task 6) is entirely independent. Tests are written before implementations throughout (TDD). All changes land on the existing `feat/security-hardening` branch.

**Tech Stack:** Python 3.8+, FastAPI, Pydantic v2, pytest (already a dev dep), React 18, TypeScript, Vitest, `@testing-library/react` (added in Task 6).

## Global Constraints

- Python `typing` module only — no PEP 585 built-in generics (`list[X]`, `tuple[X]` as annotations in function signatures or class bodies). Use `List`, `Optional`, `Tuple` from `typing`.
- Pydantic v2 (`from pydantic import field_validator`), but `.dict()` usage in existing code is fine (don't change call sites you're not otherwise touching).
- All backend tests go in `tests/` and use `pytest`. Run with `cd /path/to/contextgrid && python -m pytest tests/test_security.py -v`.
- All frontend tests use Vitest. Run with `cd frontend && npm test -- --run`.
- Branch: `feat/security-hardening`. Commit after every task.
- No new external Python dependencies — only stdlib and what's already in `pyproject.toml`.

---

## File Map

| File | Change |
|------|--------|
| `api/config.py` | Add `ALLOWED_ORIGINS`, `MAX_UPLOAD_BYTES`, `MAX_README_BYTES` |
| `.env.example` | Document the three new env vars |
| `api/server.py` | CORS middleware, SVG drop, upload cap, README cap |
| `api/models.py` | URL scheme validator on `ProjectBase.repo_url` and `LinkBase.url` |
| `tests/conftest.py` | Shared pytest fixtures (create new) |
| `tests/test_security.py` | All backend security tests (create new) |
| `frontend/src/components/Mermaid.tsx` | Replace `innerHTML` error path with React state |
| `frontend/src/components/Mermaid.test.tsx` | Vitest component test (create new) |

---

## Task 1: Config + env.example

**Files:**
- Modify: `api/config.py`
- Modify: `.env.example`

**Interfaces:**
- Produces: `config.ALLOWED_ORIGINS: List[str]`, `config.MAX_UPLOAD_BYTES: int`, `config.MAX_README_BYTES: int` — consumed by Tasks 2, 3, 4.

- [ ] **Step 1: Add imports and three new class attributes to `api/config.py`**

  Open `api/config.py`. Add `List` to the `from typing import Optional` import line, then add the three new attributes inside the `Config` class after the `UPLOADS_DIR` line:

  ```python
  from typing import Optional, List
  ```

  ```python
  # Security
  ALLOWED_ORIGINS: List[str] = [
      o.strip()
      for o in os.getenv(
          "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:8003"
      ).split(",")
      if o.strip()
  ]
  MAX_UPLOAD_BYTES: int = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))   # 10 MB
  MAX_README_BYTES: int = int(os.getenv("MAX_README_BYTES", str(1 * 1024 * 1024)))    # 1 MB
  ```

- [ ] **Step 2: Document in `.env.example`**

  Append to `.env.example` (after the existing content):

  ```
  # Security
  # Comma-separated CORS allowed origins. Default: localhost dev + prod ports.
  # ALLOWED_ORIGINS=http://localhost:5173,http://localhost:8003
  # Max screenshot upload size in bytes (default 10 MB).
  # MAX_UPLOAD_BYTES=10485760
  # Max README snapshot size in bytes (default 1 MB).
  # MAX_README_BYTES=1048576
  ```

- [ ] **Step 3: Verify config loads without error**

  ```bash
  python -c "from api.config import config; print(config.ALLOWED_ORIGINS, config.MAX_UPLOAD_BYTES, config.MAX_README_BYTES)"
  ```

  Expected output: `['http://localhost:5173', 'http://localhost:8003'] 10485760 1048576`

- [ ] **Step 4: Commit**

  ```bash
  git add api/config.py .env.example
  git commit -m "feat: add ALLOWED_ORIGINS, MAX_UPLOAD_BYTES, MAX_README_BYTES config"
  ```

---

## Task 2: CORS lockdown

**Files:**
- Modify: `api/server.py` (lines 92–99)
- Create: `tests/conftest.py`
- Create: `tests/test_security.py`

**Interfaces:**
- Consumes: `config.ALLOWED_ORIGINS` from Task 1.
- Produces: `api_client` pytest fixture (in conftest.py) consumed by all remaining backend test tasks.

- [ ] **Step 1: Create `tests/conftest.py` with the shared TestClient fixture**

  ```python
  # tests/conftest.py
  import pytest
  from unittest.mock import patch
  from fastapi.testclient import TestClient


  @pytest.fixture(scope="module")
  def api_client():
      """FastAPI TestClient with DB mocked out — no real database required."""
      with (
          patch("api.db.test_connection", return_value=(True, None)),
          patch("api.db.initialize_database", return_value=None),
          patch("api.config.Config.validate", return_value=(True, None)),
      ):
          from api.server import app
          with TestClient(app) as client:
              yield client
  ```

- [ ] **Step 2: Write the failing CORS tests in `tests/test_security.py`**

  ```python
  # tests/test_security.py


  # ── CORS ──────────────────────────────────────────────────────────────────

  def test_cors_disallowed_origin_not_echoed(api_client):
      resp = api_client.options(
          "/api/health",
          headers={
              "Origin": "http://evil.example.com",
              "Access-Control-Request-Method": "GET",
          },
      )
      assert resp.headers.get("access-control-allow-origin") != "http://evil.example.com"


  def test_cors_allowed_origin_echoed(api_client):
      resp = api_client.options(
          "/api/health",
          headers={
              "Origin": "http://localhost:5173",
              "Access-Control-Request-Method": "GET",
          },
      )
      assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"


  def test_cors_credentials_not_sent(api_client):
      resp = api_client.options(
          "/api/health",
          headers={
              "Origin": "http://localhost:5173",
              "Access-Control-Request-Method": "GET",
          },
      )
      # allow_credentials=False means this header must not say "true"
      assert resp.headers.get("access-control-allow-credentials") != "true"
  ```

- [ ] **Step 3: Run to confirm they fail**

  ```bash
  python -m pytest tests/test_security.py -v -k "cors"
  ```

  Expected: all three FAIL (CORS is still `*` / `credentials=True`).

- [ ] **Step 4: Implement the fix in `api/server.py`**

  Replace the existing `app.add_middleware(CORSMiddleware, ...)` block (around line 93) with:

  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=config.ALLOWED_ORIGINS,
      allow_credentials=False,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

- [ ] **Step 5: Run to confirm they pass**

  ```bash
  python -m pytest tests/test_security.py -v -k "cors"
  ```

  Expected: all three PASS.

- [ ] **Step 6: Commit**

  ```bash
  git add api/server.py tests/conftest.py tests/test_security.py
  git commit -m "fix: lock CORS to allowlist, disable allow_credentials"
  ```

---

## Task 3: Drop SVG + upload size cap

**Files:**
- Modify: `api/server.py` (lines 1068, 1148–1168)
- Modify: `tests/test_security.py`

**Interfaces:**
- Consumes: `config.MAX_UPLOAD_BYTES` from Task 1, `api_client` from Task 2's conftest.py.

- [ ] **Step 1: Write failing tests — append to `tests/test_security.py`**

  ```python
  import io
  from unittest.mock import patch


  # ── SVG rejection ─────────────────────────────────────────────────────────

  def test_svg_rejected_by_extension(api_client):
      resp = api_client.post(
          "/api/projects/1/screenshots",
          files={"file": ("diagram.svg", b"<svg/>", "image/png")},
      )
      assert resp.status_code == 400


  def test_svg_rejected_by_content_type(api_client):
      resp = api_client.post(
          "/api/projects/1/screenshots",
          files={"file": ("diagram.svg", b"<svg/>", "image/svg+xml")},
      )
      assert resp.status_code == 400


  # ── Upload size cap ───────────────────────────────────────────────────────

  def test_upload_over_cap_returns_413(api_client, tmp_path):
      from api.config import config as api_config

      large = b"x" * (10 * 1024 * 1024 + 1)  # 10 MB + 1 byte
      with patch.object(api_config, "UPLOADS_DIR", tmp_path / "uploads"):
          resp = api_client.post(
              "/api/projects/1/screenshots",
              files={"file": ("shot.png", large, "image/png")},
          )
      assert resp.status_code == 413


  def test_upload_at_cap_succeeds(api_client, tmp_path):
      from api.config import config as api_config

      at_cap = b"x" * (10 * 1024 * 1024)  # exactly 10 MB
      with patch.object(api_config, "UPLOADS_DIR", tmp_path / "uploads"):
          resp = api_client.post(
              "/api/projects/1/screenshots",
              files={"file": ("shot.png", at_cap, "image/png")},
          )
      assert resp.status_code == 200


  def test_upload_over_cap_leaves_no_partial_file(api_client, tmp_path):
      from api.config import config as api_config

      upload_dir = tmp_path / "uploads"
      large = b"x" * (10 * 1024 * 1024 + 1)
      with patch.object(api_config, "UPLOADS_DIR", upload_dir):
          api_client.post(
              "/api/projects/1/screenshots",
              files={"file": ("shot.png", large, "image/png")},
          )
      # No partial file should exist
      project_dir = upload_dir / "1"
      png_files = list(project_dir.glob("*.png")) if project_dir.exists() else []
      assert png_files == []
  ```

- [ ] **Step 2: Run to confirm they fail**

  ```bash
  python -m pytest tests/test_security.py -v -k "svg or upload"
  ```

  Expected: SVG tests FAIL (`.svg` still allowed), size-cap tests FAIL (no cap enforced).

- [ ] **Step 3: Remove `.svg` from `ALLOWED_IMAGE_EXTS` in `api/server.py`**

  Find the line (around line 1068):
  ```python
  ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
  ```
  Replace with:
  ```python
  ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
  ```

- [ ] **Step 4: Add explicit `image/svg+xml` rejection and size cap to `upload_screenshot` in `api/server.py`**

  The current function body (around line 1148) reads:
  ```python
  async def upload_screenshot(project_id: int, file: UploadFile = File(...)):
      """Upload a screenshot for a project."""
      if not file.content_type.startswith("image/"):
          raise HTTPException(status_code=400, detail="File must be an image")

      filename = Path(file.filename).name
      if not filename or Path(filename).suffix.lower() not in ALLOWED_IMAGE_EXTS:
          raise HTTPException(status_code=400, detail="Invalid image file type")

      project_dir = config.UPLOADS_DIR / str(project_id)
      project_dir.mkdir(parents=True, exist_ok=True)

      file_path = project_dir / filename
      if not file_path.resolve().is_relative_to(project_dir.resolve()):
          raise HTTPException(status_code=400, detail="Invalid filename")

      with open(file_path, "wb") as buffer:
          shutil.copyfileobj(file.file, buffer)

      return MessageResponse(message=f"Screenshot '{filename}' uploaded successfully")
  ```

  Replace with:
  ```python
  async def upload_screenshot(project_id: int, file: UploadFile = File(...)):
      """Upload a screenshot for a project."""
      if not file.content_type.startswith("image/") or file.content_type == "image/svg+xml":
          raise HTTPException(status_code=400, detail="File must be a raster image")

      filename = Path(file.filename).name
      if not filename or Path(filename).suffix.lower() not in ALLOWED_IMAGE_EXTS:
          raise HTTPException(status_code=400, detail="Invalid image file type")

      project_dir = config.UPLOADS_DIR / str(project_id)
      project_dir.mkdir(parents=True, exist_ok=True)

      file_path = project_dir / filename
      if not file_path.resolve().is_relative_to(project_dir.resolve()):
          raise HTTPException(status_code=400, detail="Invalid filename")

      _CHUNK = 65536  # 64 KB
      written = 0
      try:
          with open(file_path, "wb") as buffer:
              while True:
                  chunk = await file.read(_CHUNK)
                  if not chunk:
                      break
                  written += len(chunk)
                  if written > config.MAX_UPLOAD_BYTES:
                      raise HTTPException(
                          status_code=413,
                          detail=f"Upload exceeds maximum allowed size of {config.MAX_UPLOAD_BYTES} bytes",
                      )
                  buffer.write(chunk)
      except HTTPException:
          file_path.unlink(missing_ok=True)
          raise

      return MessageResponse(message=f"Screenshot '{filename}' uploaded successfully")
  ```

  Also remove the `import shutil` line if it's only used in the old `shutil.copyfileobj` call — check the file first. (If `shutil` is used elsewhere, leave it.)

- [ ] **Step 5: Run to confirm they pass**

  ```bash
  python -m pytest tests/test_security.py -v -k "svg or upload"
  ```

  Expected: all five tests PASS.

- [ ] **Step 6: Commit**

  ```bash
  git add api/server.py tests/test_security.py
  git commit -m "fix: drop SVG uploads, enforce 10 MB upload size cap"
  ```

---

## Task 4: README content-size cap

**Files:**
- Modify: `api/server.py` (function `attach_readme`, around line 1380)
- Modify: `tests/test_security.py`

**Interfaces:**
- Consumes: `config.MAX_README_BYTES` from Task 1, `api_client` from Task 2's conftest.py.

- [ ] **Step 1: Write failing tests — append to `tests/test_security.py`**

  ```python
  from unittest.mock import AsyncMock


  # ── README size cap ───────────────────────────────────────────────────────

  def test_readme_over_cap_returns_413(api_client):
      big_content = "x" * (1024 * 1024 + 1)  # 1 MB + 1 byte
      with (
          patch(
              "api.server._fetch_github_readme",
              new_callable=AsyncMock,
              return_value=(big_content, "main"),
          ),
          patch(
              "api.db.get_project",
              return_value={"id": 1, "repo_url": "https://github.com/test/repo"},
          ),
      ):
          resp = api_client.post("/api/projects/1/readme/attach")
      assert resp.status_code == 413


  def test_readme_under_cap_stores_snapshot(api_client):
      content = "# Test README"
      with (
          patch(
              "api.server._fetch_github_readme",
              new_callable=AsyncMock,
              return_value=(content, "main"),
          ),
          patch(
              "api.db.get_project",
              return_value={"id": 1, "repo_url": "https://github.com/test/repo"},
          ),
          patch("api.db.upsert_readme_snapshot", return_value=None),
          patch(
              "api.db.get_readme_snapshot",
              return_value={
                  "project_id": 1,
                  "content": content,
                  "source_ref": "main",
                  "fetched_at": "2026-01-01T00:00:00",
              },
          ),
      ):
          resp = api_client.post("/api/projects/1/readme/attach")
      assert resp.status_code == 200
  ```

- [ ] **Step 2: Run to confirm they fail**

  ```bash
  python -m pytest tests/test_security.py -v -k "readme"
  ```

  Expected: `test_readme_over_cap_returns_413` FAIL (no cap exists), `test_readme_under_cap_stores_snapshot` may PASS already — that's fine, keep it as a regression guard.

- [ ] **Step 3: Add the size check in `attach_readme` in `api/server.py`**

  Inside `attach_readme`, after the `if content is None:` block and before `db.upsert_readme_snapshot(...)`:

  ```python
  content, ref = await _fetch_github_readme(owner, repo)
  if content is None:
      raise HTTPException(
          status_code=404,
          detail=f"README.md not found in {owner}/{repo} (tried branches: main, master)"
      )

  # ↓ Add this block:
  if len(content.encode("utf-8")) > config.MAX_README_BYTES:
      raise HTTPException(
          status_code=413,
          detail=f"README exceeds maximum allowed size of {config.MAX_README_BYTES} bytes",
      )

  db.upsert_readme_snapshot(project_id, content, ref)
  ```

- [ ] **Step 4: Run to confirm they pass**

  ```bash
  python -m pytest tests/test_security.py -v -k "readme"
  ```

  Expected: both PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add api/server.py tests/test_security.py
  git commit -m "fix: reject README snapshots exceeding 1 MB"
  ```

---

## Task 5: Backend URL validation

**Files:**
- Modify: `api/models.py`
- Modify: `tests/test_security.py`

**Interfaces:**
- Produces: `_validate_http_scheme` shared validator applied to `ProjectBase.repo_url` and `LinkBase.url`.

- [ ] **Step 1: Write failing tests — append to `tests/test_security.py`**

  ```python
  import pytest
  from pydantic import ValidationError


  # ── URL scheme validation ─────────────────────────────────────────────────

  def test_repo_url_rejects_javascript_scheme():
      from api.models import ProjectBase
      with pytest.raises(ValidationError):
          ProjectBase(name="Test", repo_url="javascript:alert(1)")


  def test_repo_url_rejects_data_scheme():
      from api.models import ProjectBase
      with pytest.raises(ValidationError):
          ProjectBase(name="Test", repo_url="data:text/html,<h1>XSS</h1>")


  def test_repo_url_accepts_https():
      from api.models import ProjectBase
      p = ProjectBase(name="Test", repo_url="https://github.com/test/repo")
      assert p.repo_url == "https://github.com/test/repo"


  def test_repo_url_accepts_none():
      from api.models import ProjectBase
      p = ProjectBase(name="Test")
      assert p.repo_url is None


  def test_link_url_rejects_javascript_scheme():
      from api.models import LinkCreate
      with pytest.raises(ValidationError):
          LinkCreate(title="Bad", url="javascript:void(0)", link_type="other")


  def test_link_url_accepts_https():
      from api.models import LinkCreate
      link = LinkCreate(title="GitHub", url="https://github.com", link_type="repo")
      assert link.url == "https://github.com"
  ```

- [ ] **Step 2: Run to confirm they fail**

  ```bash
  python -m pytest tests/test_security.py -v -k "url"
  ```

  Expected: the four "rejects" tests FAIL (no validation exists), the "accepts" tests PASS.

- [ ] **Step 3: Add the validator to `api/models.py`**

  At the top of `api/models.py`, add `field_validator` to the pydantic import and `urllib.parse` to stdlib imports:

  ```python
  from pydantic import BaseModel, Field, field_validator
  from urllib.parse import urlparse
  ```

  Then add the shared helper function just before the `ProjectBase` class definition:

  ```python
  def _validate_http_scheme(v: Optional[str]) -> Optional[str]:
      """Reject URLs with non-http(s) schemes (blocks javascript:, data:, file:, etc.)."""
      if v is None:
          return v
      if urlparse(v).scheme.lower() not in ("http", "https"):
          raise ValueError("URL must use http or https scheme")
      return v
  ```

  Inside `ProjectBase`, add the validator after the field declarations:

  ```python
  class ProjectBase(BaseModel):
      """Base model for project data."""
      name: str = Field(..., min_length=1, max_length=255)
      description: Optional[str] = None
      status: str = Field(default="idea", pattern="^(idea|active|paused|archived)$")
      project_type: Optional[str] = Field(None, pattern="^(web|cli|library|school|homelab|desktop|llm-integrated|other)?$")
      primary_language: Optional[str] = None
      stack: Optional[str] = None
      repo_url: Optional[str] = None
      local_path: Optional[str] = None
      scope_size: Optional[str] = Field(None, pattern="^(tiny|medium|long-haul)?$")
      learning_goal: Optional[str] = None
      progress: int = Field(default=0, ge=0, le=100)
      folder_structure: Optional[str] = Field(None, max_length=65535)
      folder_structure_img_url: Optional[str] = Field(None, max_length=2000)

      @field_validator("repo_url")
      @classmethod
      def validate_repo_url(cls, v: Optional[str]) -> Optional[str]:
          return _validate_http_scheme(v)
  ```

  Inside `LinkBase`, add the validator after the field declarations:

  ```python
  class LinkBase(BaseModel):
      """Base model for project link data."""
      title: str = Field(..., min_length=1, max_length=255)
      url: str = Field(..., min_length=1, max_length=2000)
      link_type: str = Field(default="other", pattern="^(docs|deployment|design|board|repo|other)$")

      @field_validator("url")
      @classmethod
      def validate_url(cls, v: str) -> str:
          return _validate_http_scheme(v)
  ```

- [ ] **Step 4: Run to confirm they pass**

  ```bash
  python -m pytest tests/test_security.py -v -k "url"
  ```

  Expected: all six PASS.

- [ ] **Step 5: Run the full backend security suite to confirm no regressions**

  ```bash
  python -m pytest tests/test_security.py -v
  ```

  Expected: all tests PASS.

- [ ] **Step 6: Commit**

  ```bash
  git add api/models.py tests/test_security.py
  git commit -m "fix: reject non-http(s) URLs in repo_url and link.url"
  ```

---

## Task 6: Mermaid `innerHTML` XSS fix

**Files:**
- Modify: `frontend/src/components/Mermaid.tsx`
- Create: `frontend/src/components/Mermaid.test.tsx`

**Interfaces:**
- No cross-task dependencies. This task is entirely frontend-only.

- [ ] **Step 1: Install testing deps**

  ```bash
  cd frontend && npm install --save-dev @testing-library/react @testing-library/dom jsdom
  ```

  Verify install:
  ```bash
  npm ls @testing-library/react jsdom
  ```

  Expected: both listed without errors.

- [ ] **Step 2: Add Vitest test environment config to `frontend/vite.config.ts`**

  The existing config has no `test` key. Add it:

  ```ts
  import { defineConfig } from "vite";
  import react from "@vitejs/plugin-react";
  import path from "node:path";

  export default defineConfig({
    plugins: [react()],
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

- [ ] **Step 3: Write failing Vitest test in `frontend/src/components/Mermaid.test.tsx`**

  ```tsx
  import { describe, it, expect, vi, beforeEach } from "vitest";
  import { render, waitFor } from "@testing-library/react";

  // Mock mermaid before importing the component
  vi.mock("mermaid", () => ({
    default: {
      initialize: vi.fn(),
      render: vi.fn(),
    },
  }));

  vi.mock("@/components/ThemeProvider", () => ({
    useTheme: () => ({ themeMode: "light" }),
  }));

  import mermaid from "mermaid";
  import { Mermaid } from "@/components/Mermaid";

  const mockMermaid = mermaid as unknown as {
    initialize: ReturnType<typeof vi.fn>;
    render: ReturnType<typeof vi.fn>;
  };

  describe("Mermaid component error rendering", () => {
    beforeEach(() => {
      vi.clearAllMocks();
      mockMermaid.initialize.mockImplementation(() => {});
    });

    it("renders error as escaped text — XSS payload is not injected as markup", async () => {
      const xssPayload = '<img src=x onerror="alert(1)">';
      mockMermaid.render.mockRejectedValue(new Error(xssPayload));

      const { container } = render(<Mermaid chart="invalid" id="test-mermaid" />);

      await waitFor(() => {
        const pre = container.querySelector("pre");
        expect(pre).not.toBeNull();
        // Text content is the raw error string (correct)
        expect(pre!.textContent).toContain("img src=x");
        // If XSS worked, innerHTML would contain a literal <img ...> tag
        // React escapes it to &lt;img ..., so the img element is never created
        expect(pre!.innerHTML).not.toContain("<img");
      });

      // If the payload were injected as HTML, an img element would exist in the document
      expect(document.querySelector("img")).toBeNull();
    });

    it("renders mermaid SVG on success without error element", async () => {
      mockMermaid.render.mockResolvedValue({ svg: "<svg><text>diagram</text></svg>" });

      const { container } = render(<Mermaid chart="graph TD; A-->B" id="test-mermaid-2" />);

      await waitFor(() => {
        const div = container.querySelector(".overflow-x-auto");
        expect(div?.innerHTML).toContain("diagram");
        // No error pre element on success
        expect(container.querySelector("pre")).toBeNull();
      });
    });
  });
  ```

- [ ] **Step 4: Run to confirm the tests fail**

  ```bash
  cd frontend && npm test -- --run src/components/Mermaid.test.tsx
  ```

  Expected: first test FAIL (current code uses `innerHTML` so the `<img>` tag gets injected). Second test may PASS — that's fine.

- [ ] **Step 5: Implement the fix in `frontend/src/components/Mermaid.tsx`**

  Replace the entire file with:

  ```tsx
  import { useEffect, useRef, useState } from "react";
  import mermaid from "mermaid";
  import { useTheme } from "@/components/ThemeProvider";

  let initialized = false;

  interface MermaidProps {
    chart: string;
    id?: string;
  }

  export function Mermaid({ chart, id }: MermaidProps) {
    const ref = useRef<HTMLDivElement>(null);
    const { themeMode } = useTheme();
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
      if (!initialized) {
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: "strict",
          theme: themeMode === "dark" ? "dark" : "default",
        });
        initialized = true;
      } else {
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: "strict",
          theme: themeMode === "dark" ? "dark" : "default",
        });
      }
    }, [themeMode]);

    useEffect(() => {
      let cancelled = false;
      if (!ref.current) return;
      const renderId = id || `mermaid-${Math.random().toString(36).slice(2)}`;
      mermaid
        .render(renderId, chart)
        .then(({ svg }) => {
          if (!cancelled && ref.current) {
            ref.current.innerHTML = svg;
          }
          if (!cancelled) setError(null);
        })
        .catch((err) => {
          if (!cancelled) {
            setError(String(err));
          }
        });
      return () => {
        cancelled = true;
      };
    }, [chart, id, themeMode]);

    return (
      <>
        <div ref={ref} className="overflow-x-auto" />
        {error && <pre className="text-danger text-xs">{error}</pre>}
      </>
    );
  }
  ```

- [ ] **Step 6: Run to confirm they pass**

  ```bash
  cd frontend && npm test -- --run src/components/Mermaid.test.tsx
  ```

  Expected: both PASS.

- [ ] **Step 7: Run full frontend test suite to confirm no regressions**

  ```bash
  cd frontend && npm test -- --run
  ```

  Expected: all tests PASS (including existing `activity.test.ts`).

- [ ] **Step 8: Commit**

  ```bash
  git add frontend/src/components/Mermaid.tsx frontend/src/components/Mermaid.test.tsx frontend/vite.config.ts frontend/package.json frontend/package-lock.json
  git commit -m "fix: replace Mermaid innerHTML error path with React state to prevent XSS"
  ```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task covering it |
|-----------------|-----------------|
| CORS lockdown — env-driven allowlist, `allow_credentials=False` | Task 2 |
| Drop SVG from allowed types | Task 3 |
| Explicit `image/svg+xml` content-type rejection | Task 3 |
| Upload size cap (10 MB default, env-configurable) | Tasks 1, 3 |
| README size cap (1 MB default, env-configurable) | Tasks 1, 4 |
| Mermaid error path uses React state, not `innerHTML` | Task 6 |
| URL scheme validator on `repo_url` and `link.url` | Task 5 |
| Document new env vars in `.env.example` | Task 1 |
| Pytest tests for all backend fixes | Tasks 2, 3, 4, 5 |
| Vitest test for Mermaid fix | Task 6 |

**Placeholder scan:** No "TBD", "TODO", or vague steps found.

**Type consistency:** `_validate_http_scheme` defined in Task 5 and applied to both `repo_url` (Optional[str]) and `url` (str). Return types match. `config.ALLOWED_ORIGINS` defined as `List[str]` in Task 1 and consumed as `allow_origins=config.ALLOWED_ORIGINS` (FastAPI accepts `List[str]`) in Task 2.

All clear.
