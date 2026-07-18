# Tamheed — Brand & Logo Assets

Visual identity for **Tamheed** (Arabic: **تمهيد**, *"paving the way / groundwork"*), the
planning → execution-handoff skill. This folder holds the canonical logo files; SVG is the
source of truth — export PNGs from these SVGs as needed.

## Concept

*Tamheed* is the groundwork laid before building — exactly what the skill produces: the
validated planning package an executing agent walks on. The mark reads left to right as that
story:

- **three ascending paving-step blocks** (the groundwork being laid, step by step) — sized to
  the wordmark's cap height and sharing its baseline;
- the **two-tone wordmark** — "Tam" in deep indigo `#312e81`, "heed" in violet `#7c3aed` —
  and the Arabic **تمهيد** on the same shared baseline (bilingual identity, one line);
- a **paved-path underline** running from the first step to the end of the Arabic word,
  fading forward into an **arrow** (the path handed to execution);
- the tagline **GROUND WORK FOR EXECUTION**, centered on the path.

Palette: indigo/violet family (`#312e81` · `#7c3aed` · `#818cf8` · `#a5b4fc`; dark-mode
`#e0e7ff` · `#a78bfa` · `#4c1d95`). Arabic and Latin text render via system font stacks
(`Segoe UI` / `Noto Naskh Arabic` / `Geeza Pro`), so the SVGs stay small and editable.

## Files

| File | Use |
|---|---|
| `logo.svg` | Default / fallback (light-background colorway) |
| `logo-light.svg` | Explicit light-background version |
| `logo-dark.svg` | Dark-background version (used via `<picture>` `prefers-color-scheme`) |
| `icon.svg` | Plugin icon (square) |

The repo README consumes them with a `<picture>` element so GitHub serves the right colorway
per theme.

## History

≤ v1.0.x this project was **Keystone**, and the mark was an amber keystone wedge locking a
slate arch — see the [keystone repository](https://github.com/A-H-911/keystone) for that
identity. The Tamheed mark (v2.0, 2026-07-18) replaced it when the capability was
re-architected and renamed.
