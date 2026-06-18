# Keystone — Brand & Logo Assets

Visual identity for **Keystone**, the project-inception → planning → execution-handoff skill.
*Keystone turns a project description into an execution-ready plan and handoff package.*

This folder holds the canonical logo files. SVG is the source of truth; export PNGs from these SVGs as needed.

---

## Concept

A **keystone** is the wedge-shaped (trapezoidal) stone at the apex of an arch — the final piece that locks
all the other stones in place. Remove it and the arch falls; set it and the structure holds. That maps
directly onto what the skill does: it produces *the planning foundation that makes execution hold together*,
and it carries the architecture/governance theme at the heart of the methodology.

The mark is built from three clean geometric forms:

- an **amber trapezoidal keystone block** at the crown (the "piece that makes it hold" — given the one warm
  accent so the eye lands on it first), with two subtle vertical **block-joint lines** hinting at masonry
  segmentation;
- two **slate springing stones** angling away on either side (the voussoirs the keystone locks against); and
- a **simplified arch opening** beneath, drawn as a single rounded arc on two legs, so the whole reads as
  *architecture* rather than an abstract chevron.

Minimal, bold, and flat — no gradients, shadows, rasters, or vendor imagery. It stays legible down to 16px
and works on both light and dark backgrounds.

### Palette

| Role | Token | Hex | Notes |
|------|-------|-----|-------|
| Primary slate/indigo | `slate-700` | `#2B3A67` | Springers, arch, wordmark (neutral & light variants) |
| Deep slate (joints)  | `slate-900` | `#1E2A4A` | Joint lines; darker wordmark on light bg |
| Warm accent (amber)  | `amber-400` | `#E0A458` | The keystone block on light/neutral backgrounds |
| Warm accent (light)  | `amber-300` | `#F2B36B` | The keystone block on dark backgrounds (brighter for contrast) |
| Light slate (dark bg)| `slate-200` | `#C7D0E8` | Springers & arch on dark backgrounds |
| Near-white (dark bg) | `paper`     | `#F4F6FB` | Wordmark on dark backgrounds |

Two ideas only: a deep **slate/indigo** structure plus one **warm amber** accent on the locking stone.

### Typography

Wordmark "Keystone" is set in a common system sans stack at weight 600 with slight positive tracking:

```
'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif
```

No font files are required — the icon is purely geometric, and the wordmark uses live `<text>` with system
fonts so the SVGs stay self-contained. If you need a fully font-independent lockup (e.g. for environments
where the stack is unavailable), convert the wordmark to outlines/paths in a vector editor before export.

---

## Files in this folder

| File | viewBox | Use |
|------|---------|-----|
| `icon.svg` | `0 0 64 64` | Mark only, square. App icon / favicon / avatar. No text. Legible at 16px. |
| `logo.svg` | `0 0 320 96` | Primary horizontal lockup (mark + wordmark). Neutral slate that works on most light/mid-tone backgrounds. |
| `logo-light.svg` | `0 0 320 96` | Lockup tuned for **light** backgrounds (dark slate mark, near-black wordmark). |
| `logo-dark.svg` | `0 0 320 96` | Lockup tuned for **dark** backgrounds (light slate mark, near-white wordmark, brighter amber). |
| `README.md` | — | This file. |

All four SVGs are standalone, script-free, and render in browsers and in GitHub Markdown. Each carries
`role="img"`, an `aria-label`, and a `<title>`/`<desc>` for accessibility, and uses no external references,
fonts, or raster data.

---

## Generation / source design spec

So the identity can be reproduced or recreated in a vector editor (Figma, Illustrator, Inkscape) or with an
image model, here is the precise construction. Coordinates below are for the **64×64** icon grid; the
lockups reuse the same mark translated to `(16,16)` inside a `320×96` canvas with the wordmark baseline at
`x=104, y=58`.

- **Canvas:** 64×64, transparent. Centered, with a small optical margin.
- **Keystone block (apex wedge):** isosceles trapezoid, wider at the bottom, narrower at the top
  (so it visually "wedges" downward into the arch). Top edge `x: 24→40` at `y=22`; bottom edge `x: 21→43`
  at `y=35`. Fill amber `#E0A458`.
- **Joint lines:** two near-vertical lines splitting the block into three voussoirs, deep slate `#1E2A4A`,
  ~1.4px, ~55% opacity, rounded caps.
- **Springing stones:** two slim parallelograms flanking the keystone, slanting outward/downward, slate
  `#2B3A67`. Left ≈ points `(9,30)(24,22)(24,33)(9,44)`; right is its mirror about `x=32`.
- **Arch opening:** a single stroked path — two vertical legs rising from `y=52` to `y=41`, joined by a
  semicircular arc of radius 16 centered at `x=32`. Stroke slate `#2B3A67`, ~3.4px, round caps/joins,
  `fill="none"`.
- **Dark variant:** swap slate fills/strokes to light slate `#C7D0E8`, the keystone to brighter amber
  `#F2B36B`, and the wordmark to `#F4F6FB`. Keep the joint lines deep slate (they sit on the amber block).
- **Geometry rules:** strict left/right symmetry about `x=32`; flat fills only; no gradients/shadows/blur.

### One-paragraph generation prompt

> A minimal, bold, flat vector logo of an architectural **keystone** — the wedge-shaped trapezoidal stone at
> the apex of an arch. Center an amber trapezoid (wider at the bottom, narrowing toward the top) as the
> keystone block, with two faint vertical joint lines suggesting masonry segments. Flank it with two slim
> slate-indigo springing stones angled outward, and draw a single simplified rounded arch opening beneath on
> two short legs, so the whole reads clearly as architecture and "the piece that locks the structure
> together." Use a deep slate/indigo (#2B3A67) for the structure and one warm amber accent (#E0A458) for the
> keystone only. Strictly symmetric, clean geometric shapes, generous negative space, no gradients, no
> shadows, no text, no 3D, no photorealism, no AI/brand/vendor imagery. Designed to stay legible as a 16px
> favicon and to work on both light and dark backgrounds. Square 1:1 composition, transparent background,
> SVG-style vector art.

---

## Recommended file formats & export sizes

- **SVG is primary** — ship and reference the SVGs directly wherever vectors are supported (web, GitHub,
  docs). They are tiny (~1 KB each) and resolution-independent.
- **PNG** for raster contexts (social cards, app stores, OS icon slots, email). Export from `icon.svg` on a
  transparent background at:

  | Size | Typical use |
  |------|-------------|
  | 512×512 | High-res app icon / store listing |
  | 256×256 | App icon, large avatar |
  | 64×64 | Standard icon |
  | 32×32 | Favicon (`favicon-32x32.png`) |
  | 16×16 | Favicon (`favicon-16x16.png`) / browser tab |

  Suggested export command (using a vector rasterizer such as `rsvg-convert` or `inkscape`):

  ```bash
  for s in 512 256 64 32 16; do rsvg-convert -w $s -h $s icon.svg -o icon-${s}.png; done
  ```

- **ICO** (optional): bundle 16/32/48 into `favicon.ico` for legacy browsers.
- Lockup PNGs: export `logo-light.svg` / `logo-dark.svg` at 2× and 3× the 320×96 box (e.g. 640×192,
  960×288) for crisp raster use; keep transparent backgrounds.

Keep SVGs optimized (this set already is): no editor metadata, no embedded rasters, no `<script>`.

---

## Recommended repository paths

```
docs/assets/icon.svg          # mark only (source for favicons & app icons)
docs/assets/logo.svg          # neutral primary lockup
docs/assets/logo-light.svg    # light-background lockup
docs/assets/logo-dark.svg     # dark-background lockup
docs/assets/README.md         # this brand guide
```

Suggested PNG exports (generated, not hand-authored):

```
docs/assets/png/icon-512.png  icon-256.png  icon-64.png  icon-32.png  icon-16.png
docs/assets/favicon.ico
```

In the top-level project `README.md`, prefer the theme-aware lockup so it adapts to GitHub's light/dark UI:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-dark.svg">
  <img alt="Keystone" src="docs/assets/logo-light.svg" width="320">
</picture>
```

For the favicon in a docs site `<head>`:

```html
<link rel="icon" type="image/svg+xml" href="/docs/assets/icon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/docs/assets/png/icon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/docs/assets/png/icon-16.png">
```

---

## Light / dark usage guidance

- **Light backgrounds (white, paper, light gray):** use `logo-light.svg` (or `logo.svg`, which is neutral
  slate and reads well on most light/mid-tone surfaces). Dark slate mark + amber keystone provide strong
  contrast.
- **Dark backgrounds (near-black, deep slate, dark UI):** use `logo-dark.svg`. The mark switches to light
  slate and a brighter amber so it holds contrast; the wordmark is near-white.
- **Unknown / mixed backgrounds:** default to `logo.svg`. If you need a single mark that flips with the host
  theme, you can recolor the structure to `currentColor` and inherit the surrounding text color (keep the
  amber keystone fixed as the brand accent).
- **Clear space:** keep padding around the lockup at least the height of the keystone block (≈ the cap
  height of the wordmark) on all sides.
- **Minimum sizes:** icon down to **16px**; full lockup no smaller than **~120px** wide (below that, use the
  icon alone).
- **Don'ts:** don't recolor the keystone away from the warm accent, don't add gradients/shadows/3D, don't
  rotate or shear the mark, don't place the light lockup on light or the dark lockup on dark, and don't
  stretch — scale proportionally.

---

## Accessibility — ALT text

Use concise, purpose-appropriate alternative text. For a site header/wordmark, the brand name is usually
sufficient; richer descriptions suit documentation or first-use contexts.

| Asset | Recommended `alt` (concise) | Descriptive alternative |
|-------|------------------------------|--------------------------|
| `icon.svg` | `Keystone icon` | `Keystone icon: an amber keystone block locked at the crown of a slate arch.` |
| `logo.svg` | `Keystone` | `Keystone logo: an amber keystone block at the apex of a slate arch, beside the wordmark "Keystone".` |
| `logo-light.svg` | `Keystone` | `Keystone logo on a light background: dark slate arch with an amber keystone block and the wordmark "Keystone".` |
| `logo-dark.svg` | `Keystone` | `Keystone logo on a dark background: light slate arch with an amber keystone block and the wordmark "Keystone".` |

Notes:
- Each SVG already includes an internal `<title>`/`<desc>` and `role="img"` + `aria-label`, so inline SVG is
  announced correctly by screen readers even without an `alt`.
- When the logo is purely decorative and adjacent text already says "Keystone," use empty alt (`alt=""`) to
  avoid redundant announcements.
