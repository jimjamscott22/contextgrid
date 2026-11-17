# Diagram reliability and readability: handoff design

## Intent and scope

Make the React `/diagrams` and `/graph` pages dependable and readable on
desktop and mobile. This document records proposed implementation decisions
for the five confirmed audit findings. The user requested a committed plan
to execute in a new session; none of these fixes has been implemented here.

The earlier browser audit used synthetic API responses, Chromium, desktop
1440×1000 and mobile 390×844. With 24 projects, React Flow rendered roughly
6px labels and clipped projects; Mermaid mobile labels were roughly 4px.
Studio selection changes discarded edits and additions, connections lacked
relationship labels, and either API failing blocked both views. Historical
suite results were 74 frontend and 253 backend tests passing; re-establish
the baseline on the current checkout rather than expecting those counts.
Temporary screenshots/scripts from that session are not durable dependencies.

## Required behavior

1. **Keep studio edits.** Selecting/deselecting nodes, changing theme,
   expanding the viewer, and background query refreshes must not replace
   in-memory node labels, colors, positions, custom nodes, or connections.
   Save persists a snapshot; reload restores it; Reset explicitly discards
   local edits and rebuilds from the latest API graph. Save is browser-local,
   not a server project mutation. Keep the existing storage key and read
   valid existing snapshots, including an intentionally empty node list.
   Invalid or inaccessible storage must not crash the studio.
2. **Provide both overview and readable views.** Replace the expanding
   radial default with a deterministic status-column layout for unsaved
   graphs. Fit must actually contain every displayed node. An explicit
   Readable view restores 100% zoom around the selected or first node.
   A searchable project list and selected-node details use at least 14px
   text at both target viewports. It is acceptable for Fit to use small
   labels on large datasets; do not present that as the reading mode.
   Preserve valid saved positions until Reset. Show an explanatory prompt
   when zoom makes canvas labels smaller than 12px.
3. **Make Mermaid readable.** Add named Zoom in, Zoom out, Fit diagram,
   and Actual size controls, a visible zoom percentage, and a scrollable
   viewport. At Actual size, retain Mermaid's native SVG dimensions and
   typography rather than shrinking the whole SVG to the card width.
   Support 25%–200% zoom; Fit can go below 25% to contain a large graph,
   with the same readability prompt. Keep source expansion, dark/light
   rendering, strict Mermaid security, and escaped errors working.
4. **Keep relationship meaning.** Consume canonical `GraphData` and
   `GraphEdge` types. Studio edges read `relationship_type`, retain arrow
   direction, show human-readable labels, and distinguish inferred edges
   with a dashed stroke and a legend. Newly drawn custom connections may
   have no relationship type; never invent a project relationship for them.
5. **Isolate view failures.** Each tab owns its query, loading, error,
   empty state, and Retry action. Fetch a view when first visited, but keep
   the interactive studio mounted after it loads so switching tabs preserves
   unsaved edits. An unavailable or indefinitely loading endpoint must not
   prevent use of the healthy tab. A successful empty graph is different
   from a failed request; label any starter mindmap as a starter, not data.

## Constraints

- React 18, TypeScript, React Flow 11, TanStack Query 5, Tailwind 4,
  Mermaid 12; reuse existing components and tokens.
- No database schema/API contract changes or new runtime dependencies
  for these five fixes. Keep the legacy Jinja frontend unchanged.
- Tests must run without a live database. Use Vitest/Testing Library for
  behavior and real-browser checks for layout and SVG readability.
- Python work, if needed for test infrastructure, follows AGENTS.md:
  Python 3.8+ syntax, type hints/docstrings, execution via `uv run`.
- Do not overwrite newer sidebar/project-group/language-badge work.
- Keep generated screenshots, browser binaries, and dependency caches out
  of version control. Commit only deliberate source, tests, and docs.

## Approaches and decisions

These are author recommendations for the next implementer, not a claim that
the user separately approved a UI design. A font-only adjustment does not
solve clipping or the radial layout's growing bounds. A new graph/layout
library adds migration work without fixing the state-reset defect. Use the
existing graph tools, a small deterministic layout helper, and explicit
Fit/Readable controls plus a list that remains readable at every scale.

Initialize studio content once on the first successful graph result, not
whenever a callback identity changes. Stabilize callbacks using functional
state updates. Handle data refresh explicitly through Reset in this release;
automatic merging of local edits and changed server data is out of scope.

Keep the same graph DOM mounted when opening an expanded native fullscreen
view. Offer Expand only when `fullscreenEnabled` is supported; scrolling,
zoom, and the list remain the mobile fallback. Native Escape exits fullscreen.

## Follow-on proposal: Project Brief and Graphify artifacts

This is a proposed feature, not another confirmed defect or a prerequisite
for the five fixes. The user uses a local Graphify MCP server and wants its
HTML graph artifact and Markdown report. No live Graphify integration or
artifact-format validation was performed in this session.

After the fixes, design a Project Brief tab with purpose, next task,
blockers, recent activity, repo/deployment/command links, and an artifacts
section. Start with user-selected `.html`/`.md` uploads, project association,
original filename, import timestamp, optional generated timestamp/commit,
replace/download/remove actions, and independent empty/error states. Do not
replace the project's README snapshot with its Graphify report.

Reuse `components/Markdown.tsx` for reports. Render the HTML artifact in a
sandboxed viewer with scripts permitted only as necessary, no same-origin
privilege, and no app credentials. Confirm behavior with a real artifact,
including whether assets are self-contained or reference local files/CDNs.
File paths on the user's computer are not readable by a cloud server;
upload must transfer bytes. Decide storage, size limits, authentication,
deletion, and server migration details in a separate feature plan before
implementation. A later local importer may refresh exports; automatic MCP
sync is not part of the first artifact viewer.
