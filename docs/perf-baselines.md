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
| 2026-07-10 | feat/perf-phase1-quick-wins @ d9e4a21 | index-B5y4T7Zs.js 1.2M (1,227.59 kB) | 355.35 kB | Monolithic App chunk; mermaid/reactflow/recharts eager |

## Phase 2 target (after route lazy-loading)

| Date | Branch / commit | Largest JS asset (raw) | Initial route JS (gzip) | Notes |
|------|-----------------|------------------------|-------------------------|-------|
| | | | | Graph/Analytics/Diagrams in separate chunks |
