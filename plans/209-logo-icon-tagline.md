# Plan 209: the logo, the icon and the tagline

> Maintainer-executed, 2026-10-05. Batch record: [201-210-batch-guide-round-2.md](201-210-batch-guide-round-2.md).
> Rulings G11, G1, G16, G3. Ledger first. One commit.

## Status
- **Priority**: P2 - **Effort**: S - **Risk**: LOW (four SVGs, one data URI, three sentences; nothing
  the engine reads) - **DONE 2026-10-05**

## What this beat changes

- **The mark, two halves and a return arc.** The three ascending paving steps stay (the planning
  half climbs); a flat slab continues from the top step (the execution half walks the paved path);
  an arc returns from the slab to the first step (the record flows back: lessons, scope changes,
  verdicts). `icon.svg` is redrawn from it: today's icon is a Keystone arch, the project's old name.
- **The three lockups** (`logo.svg`, `logo-light.svg`, `logo-dark.svg`) carry the new mark and the
  reconsidered tagline; the wordmark Tamheed / تمهيد and the paved underline stay.
- **The guide's favicon** (the data URI in `render.py`) is the same mark on its violet tile.
- **The tagline, reconsidered.** "Ground work for execution" named one half. The lockups, the
  README's alt text, the guide's hero line and footer say the two: the built default is the first
  option of the review's question, the alternatives are there to pick.
- Captures: the three lockups on their backgrounds, the icon at 64 and 32 px, the guide header EN
  light and dark.

## Pin ledger

- Before: `plans/evidence/scripts-ste/pins-209.md` (23 pinned phrases in the guide files). After:
  `pins_missing.py`: 0 missing.
- Invariants: `plans/evidence/scripts-ste/invariants-209.md` (the content, the renderer, the two
  READMEs; the tagline's words new, "execution" gone from the footer and the hero line; no modal drop).

## What landed, beyond the plan

- **One drawing, four emissions.** `plans/evidence/scripts-209/make_209_assets.py` (committed: a
  drawing five surfaces derive from is not a one-off patch) draws the mark once as a function of origin, unit and palette and
  emits `icon.svg` (64, transparent), the three lockups (the 842 x 200 viewBox kept, the wordmark
  moved 12 px right and set at 92 to clear the longer mark) and the guide's favicon (32, on the
  violet tile, light stones). Dark palette: steps `#4c1d95 #7c3aed #a78bfa`, slab `#c4b5fd`, arc
  `#a78bfa`; light: steps `#a5b4fc #818cf8 #7c3aed`, slab `#a5b4fc`, arc `#7c3aed`.
- **The slab took a second cut.** At the top step's size and shade it read as a fourth step; it is
  now a thinner, longer path slab in the lightest tint, so the two halves read as a climb and a
  walk. The first regeneration missed it: an edit anchored on the slab line failed (the line had a
  different width), the generator ran unchanged, and the line was then replaced by its content.
- **The tagline on five surfaces:** the three lockups' text and `<desc>`, the README's alt text,
  the guide's hero line and footer in both languages (EN "Plan the ground, keep the record", AR
  "مهّد الأرض، واحفظ السجل"), the assets README. The old words survive only in CHANGELOG history
  and the plans.
- **The assets README was rostered by lint 14** and a 29-word sentence failed the gate; the file is
  rewritten in short sentences.
- **Captures** under `plans/evidence/captures-209/`: `logo-light.png`, `logo-dark.png` (the lockups on
  white and on a dark ground), `icon-sizes.png` (256, 64, 32, 16 px), `header-en-light.png`,
  `header-en-dark.png` (the guide's brand lockup), `favicon-sizes.png` (the tile at 64, 32, 16 px);
  `_logos.html` is the proof page the generator writes, with relative sources.
- **`icon.svg` is referenced by nothing in the repo today** (no `icon` field in `plugin.json` or the
  marketplace file); the assets README said "the plugin icon" and now says so.

## Rulings taken at the review (2026-10-05)

- Approved and committed as staged.
- **G28, the tagline:** "Plan the ground, keep the record" (AR "مهّد الأرض، واحفظ السجل", mirrored,
  not reviewed); "Pave the way, keep the record" and the old line were offered and not taken.
- **G29, the mark:** three ascending steps, a thinner path slab from the top step, an arc returning
  to the first step; drawn once by `plans/evidence/scripts-209/make_209_assets.py`, which is the
  source of the icon, the lockups and the favicon.

## Validation

- `python docs/guide/build.py`: 1,545 ids, 0 missing, 0 orphans; 724 figure files unchanged.
- `python check.py`: ALL CHECKS PASSED (lint 14 on the assets README included).
