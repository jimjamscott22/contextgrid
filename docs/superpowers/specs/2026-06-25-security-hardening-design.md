# Security Hardening Pass — Design Spec

**Date:** 2026-06-25
**Status:** Approved (pending written-spec review)
**Source:** Findings in [`docs/repomix-review.md`](../../repomix-review.md), section 3 (Security Concerns)

## Goal

Close the high-value, low-risk security gaps in the ContextGrid API and React
frontend without changing storage mechanics, database schema, or application
behavior for legitimate use. This is a hardening pass, not a refactor.

## Scope

Six isolated fixes:

1. CORS lockdown
2. Drop SVG screenshot uploads
3. Upload size cap
4. README content-size cap
5. Mermaid `innerHTML` XSS fix
6. Backend URL validation

### Explicitly out of scope (future specs)

- API ↔ frontend contract fixes (`search`/`include_archived`/`kanban`, real `total`, PEP 585 cleanup)
- Splitting `api/server.py` into routers/services
- Unifying `api/db.py` + `src/db.py` and adding migrations
- Net-new features (global search, saved views, export/import)
- Legacy Jinja template (`web/templates/project_detail.html`) attribute-escaping

## Configuration changes

All new tunables follow the existing env-driven pattern in
[`api/config.py`](../../../api/config.py).

| Config | Env var | Default | Purpose |
|--------|---------|---------|---------|
| `ALLOWED_ORIGINS` | `ALLOWED_ORIGINS` | `http://localhost:5173,http://localhost:8003` | Comma-separated CORS allowlist, parsed into a list |
| `MAX_UPLOAD_BYTES` | `MAX_UPLOAD_BYTES` | `10485760` (10 MB) | Max screenshot upload size |
| `MAX_README_BYTES` | `MAX_README_BYTES` | `1048576` (1 MB) | Max stored README snapshot size |

`ALLOWED_ORIGINS` parsing: split on comma, strip whitespace, drop empties.
Document the three new vars in `.env.example`.

## Detailed design

### 1. CORS lockdown

**File:** [`api/server.py:93-99`](../../../api/server.py#L93), `api/config.py`

- Replace `allow_origins=["*"]` with `allow_origins=config.ALLOWED_ORIGINS`.
- Set `allow_credentials=False`. There is no auth or cookie usage anywhere in
  the app, and the `origin="*"` + `credentials=True` combination is rejected by
  browsers regardless — so this is both a security fix and a correctness fix.
- Keep `allow_methods=["*"]` and `allow_headers=["*"]`.

**Acceptance:** A request with a disallowed `Origin` header does not receive an
`Access-Control-Allow-Origin` echo for that origin; an allowed origin does.

### 2. Drop SVG screenshot uploads

**File:** [`api/server.py:1068`](../../../api/server.py#L1068), [`api/server.py:1148-1168`](../../../api/server.py#L1148)

- Remove `.svg` from `ALLOWED_IMAGE_EXTS`. New set:
  `{".png", ".jpg", ".jpeg", ".gif", ".webp"}`.
- In `upload_screenshot`, explicitly reject `image/svg+xml` content-type with
  `400` as defense-in-depth (the extension check already covers it).

**Storage note:** The upload/serve mechanism is unchanged — files still land in
`config.UPLOADS_DIR / <project_id> / <filename>` and are served from the
`/uploads` mount. Existing `.svg` files (if any) remain on disk but stop
appearing in `list_screenshots` because the listing filters by
`ALLOWED_IMAGE_EXTS`. User confirmed no SVG screenshots exist, so no migration
step is required.

**Acceptance:** Uploading a `.svg` file or `image/svg+xml` body returns `400`;
raster formats still succeed.

### 3. Upload size cap

**File:** [`api/server.py:1148-1168`](../../../api/server.py#L1148), `api/config.py`

- Enforce `MAX_UPLOAD_BYTES` during the actual file copy, not via the
  `Content-Length` header (which is spoofable).
- Stream the upload in chunks, counting bytes written. If the running total
  exceeds the cap, stop, delete the partial file, and raise
  `413 Payload Too Large`.

**Acceptance:** An upload exceeding the cap returns `413` and leaves no partial
file on disk; an upload under the cap succeeds.

### 4. README content-size cap

**File:** [`api/server.py:1328-1347`](../../../api/server.py#L1328) (`_fetch_github_readme` / `attach_readme`), `api/config.py`

- After fetching README content, if `len(content.encode("utf-8"))` exceeds
  `MAX_README_BYTES`, raise `413` **before** storing the snapshot. Reject rather
  than truncate, so the stored snapshot is never a silently-cut document.

**Acceptance:** Attaching a README larger than the cap returns `413` and stores
nothing; a normal README attaches successfully.

### 5. Mermaid `innerHTML` XSS fix

**File:** [`frontend/src/components/Mermaid.tsx:45-51`](../../../frontend/src/components/Mermaid.tsx#L45)

- Replace the catch-branch `ref.current.innerHTML = \`<pre>...${err}\`` with
  React state: add `const [error, setError] = useState<string | null>(null)`,
  call `setError(String(err))` in the catch and `setError(null)` on success.
- Render the error through JSX (`{error && <pre className="text-danger text-xs">{error}</pre>}`),
  which auto-escapes text — raw error strings can no longer inject markup.
- The success path keeps writing Mermaid's own output. Mermaid is already
  initialized with `securityLevel: "strict"`, so the rendered SVG is sanitized.
  Writing that sanitized SVG via `innerHTML` remains acceptable.

**Acceptance:** When `mermaid.render` rejects with an error string containing
HTML (e.g. `<img onerror=...>`), the text is displayed escaped and no element is
injected into the DOM.

### 6. Backend URL validation

**File:** [`api/models.py`](../../../api/models.py) (`ProjectBase.repo_url`, `LinkCreate.url`)

- Add a shared Pydantic validator rejecting any URL whose scheme is not `http`
  or `https`. This blocks `javascript:`, `data:`, `file:`, etc. at the API
  boundary.
- `repo_url` stays `Optional` — `None`/empty remains valid. `link.url` is
  required and must pass validation.

**Acceptance:** Creating/updating a project with `repo_url="javascript:alert(1)"`
or a link with such a URL returns `422`; valid `http(s)` URLs succeed.

## Testing

The repo's existing tests are shell-based ([`tests/`](../../../tests/)), but
`pytest` is already a dev dependency and Vitest was recently added to the
frontend. Add focused automated tests:

**Backend (`pytest`, new module under `tests/`):**
- Disallowed CORS origin is not echoed; allowed origin is.
- `.svg` upload and `image/svg+xml` body are rejected with `400`.
- Over-cap upload returns `413` and leaves no partial file.
- Over-cap README returns `413` and stores nothing.
- `repo_url` / `link.url` with a non-http(s) scheme returns `422`.

**Frontend (Vitest):**
- Mermaid error path renders the error string as escaped text content, not as
  injected markup.

## Risks & mitigations

- **CORS too strict for a user's setup** — mitigated by `ALLOWED_ORIGINS` being
  env-configurable with sensible localhost defaults.
- **Upload cap too low** — env-configurable; default 10 MB comfortably covers
  high-res screenshots (user confirmed).
- **Existing `.svg` files disappearing from listings** — confirmed none exist;
  files remain on disk regardless.
