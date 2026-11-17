# Diagram Reliability and Readability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Use superpowers:subagent-driven-development only if the user chooses delegation. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the five confirmed React diagram defects without requiring the user's database or local Graphify server.

**Architecture:** Keep React Flow and Mermaid, separate view query lifecycles, initialize studio edits once, and share a deterministic graph layout. Separate full-graph Fit from reading controls and an unscaled project list. Implement Graphify/Project Brief later using the feature proposal in the companion design.

**Tech Stack:** React 18, TypeScript, React Flow 11, TanStack Query 5, Tailwind 4, Mermaid 12, Vitest/Testing Library, Playwright with Chromium for rendered checks.

**Spec:** [Diagram reliability design](../specs/2026-11-16-diagram-reliability-design.md). Read it and `AGENTS.md` before implementation.

## Global Constraints

- No database schema/API contract changes or new runtime dependencies for these five fixes. Keep the legacy Jinja frontend unchanged.
- Tests must run without a live database. Use Vitest/Testing Library for behavior and real-browser checks for layout and SVG readability.
- Do not overwrite newer sidebar/project-group/language-badge work.
- Keep generated screenshots, browser binaries, and dependency caches out of version control. Commit only deliberate source, tests, and docs.
- Execute in a feature branch in the next session; the user's exception to publish this planning handoff on main does not authorize publishing future implementation there.
- This is a plan, not completed work. All task checkboxes intentionally start unchecked.

## Review Focus

- StrictMode, tab switches, equivalent query refreshes, and theme changes must preserve unsaved graph edits (Tasks 1–2).
- Valid empty snapshots, malformed JSON, and blocked localStorage must not crash or silently regenerate discarded content (Task 1).
- Single, disconnected, cyclic, long-label, and 100-node graphs need stable placement and readable alternatives (Task 4).
- A hanging or failing inactive endpoint must not disable the healthy tab (Task 2).
- Stale Mermaid promises and dark-mode rerenders must not restore old SVG or bypass escaped-error rendering (Task 5).

## File map

Existing files to modify:
- `frontend/src/components/project/InteractiveMindmap.tsx`: studio initialization, edit lifecycle, canonical edge mapping, layout/view controls.
- `frontend/src/routes/Diagrams.tsx`: independent query/error state and mounted tab content.
- `frontend/src/routes/Graph.tsx`: shared layout, filtering/list, view controls, preserve project navigation.
- `frontend/src/components/Mermaid.tsx`: SVG dimensions and zoom/scroll controls; preserve render cancellation/security.
- `frontend/src/components/project/EditableNode.tsx`: wrap long labels and keep reading text at native readable size.
- `frontend/src/index.css`: only scoped viewer styles as necessary.

New modules and tests:
- `frontend/src/lib/mindmapStorage.ts` and `.test.ts`: snapshot parsing, validation, serialization without callbacks.
- `frontend/src/lib/graphLayout.ts` and `.test.ts`: deterministic positions and incident-edge filtering.
- `frontend/src/components/diagrams/GraphProjectList.tsx` and `.test.tsx`: search/status controls, readable project list/details.
- `frontend/src/components/diagrams/DiagramFrame.tsx` and `.test.tsx`: common viewport, optional native fullscreen, same mounted children.
- `frontend/src/components/project/InteractiveMindmap.test.tsx`, `frontend/src/routes/Diagrams.test.tsx`, and `frontend/src/routes/Graph.test.tsx`: user-facing regressions.
- Extend `frontend/src/components/Mermaid.test.tsx` for viewer controls and cancellation.
- `scripts/check_diagrams.py`: repeatable browser QA with synthetic API responses, screenshots written outside the repo.

## Start-of-session baseline

- [ ] Read the companion design and inspect `git status`, current branch, and remote main; preserve unrelated edits. Use the worktree skill if isolation is needed.
- [ ] From `frontend/`, run `npm ci`, `npm test`, and `npm run build`. From the repository root run `UV_CACHE_DIR=/tmp/contextgrid-uv-cache uv run pytest -q`. Save current results; historical counts are not assertions.
- [ ] Start `npm run dev -- --host 0.0.0.0` from `frontend/`. Use Browser tools if available; otherwise installed Playwright/Chromium. Do not connect a production database for this work.

### Task 1: Preserve local studio edits and saved snapshots

**Files:** Modify `InteractiveMindmap.tsx`; create `InteractiveMindmap.test.tsx`, `lib/mindmapStorage.ts`, `lib/mindmapStorage.test.ts`.

**Interfaces:** Export `MindmapSnapshot` with `nodes: Node<CustomNodeData>[]` and `edges: Edge[]`; `parseMindmapSnapshot(raw: string | null): MindmapSnapshot | null`; `serializeMindmapSnapshot(snapshot: MindmapSnapshot): string`. Keep storage key `contextgrid_mindmap_layout_v1`. No serialized event callbacks.

- [ ] Add failing tests named `keeps edits after deselection`, `keeps newly added node`, `keeps edits after equivalent data refresh and theme change`, and `does not restore a deleted node`. Render under StrictMode, edit a node through properties, deselect/reselect, and assert the edited label and node counts remain correct. Exercise pending edits through a rerender with a newly allocated but equivalent API result.
- [ ] Add storage cases: valid old snapshot restores positions/edges, `{nodes: [], edges: []}` remains empty, malformed JSON/invalid positions return null, Save strips callbacks, localStorage read/write exceptions show recoverable state. Assert a save failure never displays success feedback.
- [ ] Run `npm test -- src/components/project/InteractiveMindmap.test.tsx src/lib/mindmapStorage.test.ts` in `frontend/`; verify regression failures before changing behavior.
- [ ] Make deletion independent of `selectedNodeId` using a functional selection update. Initialize once when actual API data first arrives, not on callback/theme/selection changes. Do not initialize against an undefined loading result. Restore valid storage first, otherwise build from API. Do not add an effect dependency suppression as the fix.
- [ ] Wire explicit Save and Reset to the snapshot helpers. Reset uses the latest API result and clears selection; Save/reload restores edited nodes, positions, colors, connections, and intentional empty state. A background API result is picked up by Reset, not by overwriting local edits.
- [ ] Run the focused tests and `npm run lint`; verify edits survive add/select/deselect/delete/save/reload/reset in a real browser. Commit as `fix: preserve mindmap edits across selection changes`.

### Task 2: Isolate diagram queries while preserving studio mounting

**Files:** Modify `routes/Diagrams.tsx`; create `routes/Diagrams.test.tsx`.

**Interfaces:** Keep `api.graph()`, `api.overviewMermaid()`, and their existing query keys. Consume the state-preserving studio from Task 1. Each tab renders its own query state and Retry button.

- [ ] Add failing tests `renders studio while mermaid fails`, `renders mermaid while graph fails`, `healthy tab works while other request never resolves`, `retries only the failed view`, and `retains unsaved studio edits across tab switches`. Use a QueryClient with retries disabled and stub the API, not global fetch where unrelated queries may be involved.
- [ ] Run `npm test -- src/routes/Diagrams.test.tsx`; confirm current combined `isLoading`/`error` gating fails these cases.
- [ ] Replace shared gating with tab-specific status. Enable each query on first visit. Keep the successfully mounted studio hidden when inactive rather than conditionally unmounting it. A tab switch must remain available while either view is loading or failed.
- [ ] Add explicit empty-state copy: a starter mindmap is labeled as starter content, and failed requests never masquerade as an empty workspace. Add empty-result assertions to the same tests.
- [ ] Re-run focused tests and `npm run lint`; manually switch both directions with each endpoint separately returning 503 or hanging. Commit as `fix: isolate diagram view loading and failures`.

### Task 3: Restore relationship labels and inferred-edge meaning

**Files:** Modify `InteractiveMindmap.tsx` and its test; consume `GraphData`/`GraphEdge` from `lib/api/types.ts`.

**Interfaces:** `InteractiveMindmapProps.initialData?: GraphData`; maintain snapshot compatibility with string node IDs. Map `GraphEdge.relationship_type` to labels `Depends on`, `Part of`, `Related to`; preserve the canonical type in edge data if needed. Custom edges with no type keep no label.

- [ ] Add failing cases for all three relationship types, directed endpoints, dashed inferred connections, explicit solid connections, and custom unlabeled edges after save/reload. Assert semantic edge data with a narrowly scoped React Flow mock; do not substitute this for the browser label check.
- [ ] Run `npm test -- src/components/project/InteractiveMindmap.test.tsx` and verify the current `e.label` mapping fails.
- [ ] Replace the permissive `OverviewData` interface with the canonical graph input and map `relationship_type`. Give edge labels contrasting backgrounds and readable native text; add a visible explicit/inferred legend. Keep user-created snapshot edges compatible.
- [ ] Re-run tests and `npm run lint`; inspect real rendered arrows, labels, and legend in light/dark themes. Commit as `fix: preserve relationship meaning in mindmap edges`.

### Task 4: Replace radial defaults and add readable graph navigation

**Files:** Create `lib/graphLayout.ts`, its test, `components/diagrams/GraphProjectList.tsx`, `DiagramFrame.tsx`, and their tests; modify both graph consumers, `EditableNode.tsx`, and scoped styles. Create `routes/Graph.test.tsx`.

**Interfaces:** `layoutGraphNodes(nodes: GraphNode[]): Map<string, {x: number; y: number}>`; `filterGraph(data: GraphData, search: string, status: ProjectStatus | "all"): GraphData`. Export `GraphProjectList({data, onSelect}: {data: GraphData; onSelect: (id: string) => void})` and `DiagramFrame({title, children}: {title: string; children: ReactNode})`.

- [ ] Write failing layout cases for zero/one/24/100 nodes, reordered input, cycles, disconnected nodes, and long duplicate labels with distinct IDs. Assert one unique finite position per ID, stable positions for the same node set regardless of input order, and no edge with an excluded endpoint after filtering.
- [ ] Run `npm test -- src/lib/graphLayout.test.ts`; verify the missing helper causes failure before implementing it.
- [ ] Implement layout as four status columns in order active/idea/paused/archived, sorted within each by label then ID. Use 292px column stride, 112px row stride, and nodes at most 260px wide with wrapping. This avoids topology-dependent placement and requires no extra package. Preserve existing saved studio positions; only new graphs and Reset use these defaults.
- [ ] Add consumer tests for case-insensitive search, status filtering, clearing filters, readable selected details, and unchanged `/projects/:id` navigation. Filtering studio content is a presentation operation, not deleting nodes/edges or resetting the underlying edit state; custom nodes without project status remain available in All.
- [ ] Run the new consumer/frame tests before implementing those controls and confirm the missing behavior fails.
- [ ] Add the shared frame and list. The list/details render at least 14px text and show the full selected label. Native fullscreen uses the same mounted DOM; hide Expand when unsupported, handle rejected fullscreen requests, and remove event listeners on unmount. Test those cases with a mocked Fullscreen API.
- [ ] Configure React Flow with `minZoom={0.05}`, `maxZoom={2}`, Fit padding 0.15 and fitting max zoom 1. Add Readable view at zoom 1 centered on selected/first displayed node. Refit after filtering and Reset, not every edit. Hide the minimap on small screens and wrap controls. Show a reading prompt below 12px effective canvas label size. Empty filtering results get a Clear filters action.
- [ ] Run `npm test -- src/lib/graphLayout.test.ts src/components/diagrams src/routes/Graph.test.tsx src/components/project/InteractiveMindmap.test.tsx` and `npm run lint`. In Chromium, Fit all 24 node bounds inside the canvas at both target viewports; verify Readable view and list text remain legible. Fit may shrink text; the prompt/list must explain and resolve that state. Commit as `fix: add readable graph layouts and navigation`.

### Task 5: Add a usable Mermaid SVG viewport

**Files:** Modify `components/Mermaid.tsx`, its existing test, `routes/Diagrams.tsx`, and scoped styles; reuse `DiagramFrame` from Task 4.

**Interfaces:** Retain `<Mermaid chart={string} id={optionalString} />`. Keep SVG rendering and dimensions internal so existing consumers remain compatible. Toolbar names: `Zoom in`, `Zoom out`, `Fit diagram`, `Actual size`.

- [ ] Extend existing tests with zoom percentage/dimension updates, Fit measurement via mocked viewport dimensions, Actual size restoration, disabled boundary controls, and overflow instead of page-wide horizontal scrolling. Retain the XSS escaped-error test.
- [ ] Add asynchronous cases: rapid chart A→B resolves B then A, unmount before resolution, and theme change. Only the latest render may remain visible, no stale error should replace a successful current chart, and render failures must not leave an old chart looking current.
- [ ] Run `npm test -- src/components/Mermaid.test.tsx`; confirm missing controls/dimensions fail before implementation.
- [ ] On successful render, derive native dimensions from SVG viewBox (or finite width/height fallback). Apply pixel width/height based on zoom, overriding Mermaid's responsive max-width only inside this viewport. Use scrollable overflow and bounded height. Implement 25%–200% manual zoom in 25-point steps; Actual size is 100%; Fit computes the smaller viewport/content ratio and may go below 25% with a readable-view prompt.
- [ ] Keep Mermaid `securityLevel: "strict"`, render cancellation, theme rerendering, and React-escaped errors. Recalculate Fit when the viewport resizes without overriding a manually chosen zoom on unrelated rerenders. Keep Show source outside the scrolling SVG viewport.
- [ ] Update the existing successful-render assertion to target the SVG viewport semantically if its old `.overflow-x-auto` wrapper changes; preserve the SVG content assertion rather than retaining an implementation-specific class just for the test.
- [ ] Run focused tests and `npm run lint`; check scroll, zoom, Fit, Actual size, source, dark mode, and native fullscreen with real Mermaid SVG at 390×844 and 1440×1000. Commit as `fix: add readable zoom and scrolling to mermaid diagrams`.

### Task 6: Preserve a repeatable cloud browser regression check

**Files:** Create `scripts/check_diagrams.py`; update this plan's completion checkboxes only when evidence exists.

**Interfaces:** CLI `uv run --with playwright python scripts/check_diagrams.py --base-url http://127.0.0.1:5173 --output-dir /tmp/contextgrid-diagram-qa`. Optional `--chromium-path` selects installed Chromium. Return nonzero on an assertion failure. Importing the module must not launch a browser.

- [ ] Build deterministic fixtures containing 0, 1, 6, 24, and 100 projects, long labels, all statuses/relationship types, and inferred edges. Intercept only URLs whose parsed pathname starts `/api/`, not the glob `**/api/**`, which also matches Vite source modules under `/src/lib/api/`. No live API or database requests should be made.
- [ ] Script actual editing, deselection, Add Node, deleting, save/reload, Reset, theme changes, switching views, graph project navigation, search/filter, Fit/Readable, Mermaid controls/source, and supported fullscreen. Check DOM state after each action; no unconditional long sleeps.
- [ ] Assert page identity, meaningful content, no framework overlay, no unexpected console/page errors, and screenshots at both target viewports. For Fit, measure node bounds against the canvas with a small rounding tolerance; for readable mode/list, inspect effective rendered font sizes. Use browser-level checks for SVG dimensions rather than treating jsdom as layout evidence.
- [ ] Add separate failure scenarios for graph-only 503, Mermaid-only 503, delayed/hanging endpoints, and retries. Allow only the deliberately injected network errors; do not globally suppress console errors. On failure, preserve a screenshot and diagnostic JSON outside the repository.
- [ ] Run the browser command against the dev server. If browser dependencies are absent, use the skill's supported setup process; keep downloads outside committed source and record the browser/version and all remaining limitations.
- [ ] Run `npm test`, `npm run build`, and root `UV_CACHE_DIR=/tmp/contextgrid-uv-cache uv run pytest -q`. Run `git diff --check`. Review React best practices after the component edits. Commit the harness as `test: cover diagram editing and readability in browser`.

## Completion and next-session handoff

- [ ] Record current verification results and remaining risks in the implementation PR; attach screenshots as review evidence, not checked-in binaries.
- [ ] Verify all five findings against their original triggers. Do not call work complete based on a passing build or mocked SVG tests alone.
- [ ] Keep Project Brief/Graphify artifacts in a separate follow-on plan. Read the proposal in the companion design; obtain a real `.html`/`.md` export pair before promising compatibility. No direct access to the local MCP server is required for file imports.
- [ ] Do not treat this planning commit as an implemented fix or an authorization to deploy/merge the future implementation.

Suggested next-session prompt:

> Implement `docs/superpowers/plans/2026-11-16-diagram-reliability-plan.md`
> task by task, starting with its companion design. Fix the five confirmed
> React diagram issues on a feature branch, preserve unrelated changes,
> and verify with mocked APIs plus real-browser desktop/mobile checks.
> Leave Project Brief/Graphify implementation for a separate follow-on.
