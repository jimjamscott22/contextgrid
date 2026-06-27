# Theme Picker Expansion — Design Spec

**Date:** 2026-06-26
**Status:** Approved

## Goal

Add 8 new "lifestyle" themes to the existing theme picker, organized alongside the current 8 "editor" themes via `<optgroup>` grouping in the navbar select.

## New Themes

| ID | Label | Mode |
|----|-------|------|
| `ocean-light` | Ocean Light | light |
| `ocean-dark` | Ocean Dark | dark |
| `coffee-light` | Coffee Light | light |
| `coffee-dark` | Coffee Dark | dark |
| `forest-light` | Forest Light | light |
| `forest-dark` | Forest Dark | dark |
| `cyberpunk` | Cyberpunk | dark |
| `rose` | Rose | light |

Ocean, Coffee, and Forest each have a light+dark pair. Cyberpunk is dark-only (neon aesthetic requires dark surface). Rose is light-only (blush palette doesn't suit dark mode).

## Color Palettes

All themes use the existing 14 semantic CSS tokens — no new tokens are introduced.

### Ocean Light
```css
--cg-bg: 240 249 255;
--cg-surface: 255 255 255;
--cg-surface-alt: 224 242 254;
--cg-border: 186 230 253;
--cg-fg: 12 74 110;
--cg-fg-soft: 3 105 161;
--cg-muted: 125 211 252;
--cg-primary: 14 165 233;
--cg-primary-fg: 255 255 255;
--cg-accent: 20 184 166;
--cg-success: 34 197 94;
--cg-warning: 234 179 8;
--cg-danger: 239 68 68;
color-scheme: light;
```

### Ocean Dark
```css
--cg-bg: 3 20 40;
--cg-surface: 5 30 58;
--cg-surface-alt: 7 40 75;
--cg-border: 15 70 110;
--cg-fg: 224 242 254;
--cg-fg-soft: 186 230 253;
--cg-muted: 56 189 248;
--cg-primary: 56 189 248;
--cg-primary-fg: 3 20 40;
--cg-accent: 45 212 191;
--cg-success: 74 222 128;
--cg-warning: 250 204 21;
--cg-danger: 248 113 113;
color-scheme: dark;
```

### Coffee Light
```css
--cg-bg: 250 245 235;
--cg-surface: 255 251 244;
--cg-surface-alt: 243 234 220;
--cg-border: 224 208 188;
--cg-fg: 68 40 20;
--cg-fg-soft: 101 65 35;
--cg-muted: 166 124 90;
--cg-primary: 161 98 7;
--cg-primary-fg: 255 251 244;
--cg-accent: 120 53 15;
--cg-success: 22 163 74;
--cg-warning: 217 119 6;
--cg-danger: 220 38 38;
color-scheme: light;
```

### Coffee Dark
```css
--cg-bg: 20 12 5;
--cg-surface: 30 18 8;
--cg-surface-alt: 42 25 12;
--cg-border: 70 45 22;
--cg-fg: 243 228 206;
--cg-fg-soft: 214 187 154;
--cg-muted: 156 124 89;
--cg-primary: 217 119 6;
--cg-primary-fg: 20 12 5;
--cg-accent: 249 115 22;
--cg-success: 74 222 128;
--cg-warning: 251 191 36;
--cg-danger: 248 113 113;
color-scheme: dark;
```

### Forest Light
```css
--cg-bg: 240 253 244;
--cg-surface: 255 255 255;
--cg-surface-alt: 220 252 231;
--cg-border: 187 247 208;
--cg-fg: 20 83 45;
--cg-fg-soft: 22 101 52;
--cg-muted: 134 239 172;
--cg-primary: 34 197 94;
--cg-primary-fg: 255 255 255;
--cg-accent: 20 184 166;
--cg-success: 22 163 74;
--cg-warning: 234 179 8;
--cg-danger: 239 68 68;
color-scheme: light;
```

### Forest Dark
```css
--cg-bg: 5 20 10;
--cg-surface: 10 30 15;
--cg-surface-alt: 15 40 22;
--cg-border: 30 70 40;
--cg-fg: 220 252 231;
--cg-fg-soft: 187 247 208;
--cg-muted: 74 222 128;
--cg-primary: 74 222 128;
--cg-primary-fg: 5 20 10;
--cg-accent: 45 212 191;
--cg-success: 34 197 94;
--cg-warning: 250 204 21;
--cg-danger: 248 113 113;
color-scheme: dark;
```

### Cyberpunk
```css
--cg-bg: 5 0 15;
--cg-surface: 13 5 30;
--cg-surface-alt: 25 10 50;
--cg-border: 80 20 160;
--cg-fg: 224 204 255;
--cg-fg-soft: 190 150 255;
--cg-muted: 130 80 200;
--cg-primary: 255 0 255;
--cg-primary-fg: 5 0 15;
--cg-accent: 0 255 255;
--cg-success: 0 255 128;
--cg-warning: 255 200 0;
--cg-danger: 255 50 50;
color-scheme: dark;
```

### Rose
```css
--cg-bg: 255 241 242;
--cg-surface: 255 255 255;
--cg-surface-alt: 255 228 230;
--cg-border: 254 205 211;
--cg-fg: 136 19 55;
--cg-fg-soft: 159 18 57;
--cg-muted: 251 113 133;
--cg-primary: 244 63 94;
--cg-primary-fg: 255 255 255;
--cg-accent: 236 72 153;
--cg-success: 34 197 94;
--cg-warning: 234 179 8;
--cg-danger: 239 68 68;
color-scheme: light;
```

## ThemeProvider Changes

- `ThemeId` union type gains 8 new string literals.
- `ThemeOption` interface gains a `group: "editor" | "lifestyle"` field.
- All existing 8 options get `group: "editor"`. All 8 new options get `group: "lifestyle"`.

## Navbar Changes

The flat `themes.map(option => <option>)` is replaced with two `<optgroup>` elements, each filtering `themes` by `group`. Labels: `"Editor Themes"` and `"Lifestyle Themes"`.

## Files Changed

1. `frontend/src/index.css` — 8 new `[data-theme]` blocks appended in the `@layer base` block.
2. `frontend/src/components/ThemeProvider.tsx` — updated `ThemeId`, `ThemeOption`, and `THEME_OPTIONS`.
3. `frontend/src/components/layout/Navbar.tsx` — `<optgroup>` split in the theme `<select>`.
