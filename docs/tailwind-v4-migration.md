# Tailwind 4 migration

The frontend uses Tailwind 4.3 through `@tailwindcss/vite`. This replaces the
Tailwind 3 PostCSS configuration that stopped working when Tailwind 4 was installed.

- [x] Register the Vite plugin and remove obsolete direct PostCSS dependencies.
- [x] Move the palette, radii, fonts, container customization, and dark variant
  into `frontend/src/index.css`; retain all named theme RGB values.
- [x] Share input/textarea declarations without applying a custom component class.
- [x] Preserve small shadows, backdrop blur, inner shadows, and transparent focus
  outlines used by existing components.
- [x] Upgrade `tailwind-merge` to its Tailwind 4 compatible major and add focused
  class-merging tests.
- [x] Preserve the existing Mermaid 12.2 and React Router DOM 7.18 upgrades.
- [x] Verify clean installation, type checking, 74 tests, production build, and
  a frontend npm audit with zero reported vulnerabilities.
- [x] Verify Chromium at 1440x1000 and 390x844: overview rendering, Light+/Dark+/
  Monokai/Rose theme selection, project dialog open/close, textarea dimensions,
  actual Mermaid SVG rendering, and mobile sidebar open/close. No browser console
  errors, Vite overlays, or horizontal overflow were observed in the final run.

Theme switching and responsive browser checks use local API fixtures; they do not
verify the live FastAPI/MySQL integration. The production build still reports
large JavaScript chunks. The npm script-policy and Recharts deprecation warnings
are separate from this migration.

Use Node 24.15 or later within the Node 24 series (verification also ran with
24.22). Run the following from `frontend/`:

```sh
npm ci
npm run lint
npm test
npm run build
npm audit
```

Tailwind 4 targets modern browsers: Safari 16.4+, Chrome 111+, and Firefox 128+.
See the [official upgrade guide](https://tailwindcss.com/docs/upgrade-guide).
