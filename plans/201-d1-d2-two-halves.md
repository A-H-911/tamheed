# Plan 201: D1 and D2 show one agent with two halves; the README overview image follows

> Maintainer-executed, 2026-10-04. Batch B (the user guide round 2, plans 201-210 -> v6.1.0) opens
> after the v6.0.0 tag (G15). Rulings G1, G16, G3; the round-1 bar (the diagram geometry lint on
> both language copies, fade not draw, RTL anchors). Ledger first. One commit.

## Status
- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (the two figures a reader meets first; the
  click-to-isolate script on D2; the README image is hand-exported today) - **DONE 2026-10-04**

## What this beat changes

- **D1 (overview):** the operator on top; one box "Claude Code + Tamheed" with two lanes, the
  planning half (stages 1-20 and its tools) and the execution half (stages 21-22 and its tools); the
  handoff as the arrow between the lanes; the MCP server and the package below, the one write path;
  `review.html` and the readiness verdict where they belong. Labels EN + AR, the caption rewritten.
- **D2 (the operator and the two halves):** the same shape with what each party may do; the
  click-to-isolate keeps working per party (operator, planning half, execution half, the store).
- The D2 table's column header (`ui.col.actor`, used by that table alone): "Actor" -> "Party",
  "الفاعل" -> "الطرف". The section title was retitled in 197; the only other visible "actor" on the
  page is the engine's `actor` column and the brief-review wording. `index.html` rebuilt.
- `docs/assets/tamheed-overview.png` re-exported from the new D1 (light theme, the README's image).
- Tests: `test_user_guide` holds (the geometry lint runs in `build.py` and the suite; both copies).

## Pin ledger

- Before: `plans/evidence/scripts-ste/pins-201.md` (22 pinned phrases in the three guide files, none
  on the D1/D2 labels). After: `pins_missing.py`: 0 missing.
- Invariants: `plans/evidence/scripts-ste/invariants-201.md` (4 files). The two `until` drops: the
  staged diff shows them in the removed README alt text and the removed D1 caption (`git diff
  --cached -U0 | grep until`), both replaced whole.

## What landed, beyond the plan

- **The frame primitive (G17).** A model-level `frame(key, x, y, w, h, label, members)`, drawn before
  the edges with no fill and a dashed stroke, its title at the top-left (`start`, mirrored for RTL),
  never a click target. The lint: on the canvas, every member inside; exempt from crossings, borders
  and label touches. `test_diagrams_draw_cleanly` holds a member-outside case and asserts the frame is
  no obstacle. The 203 swimlanes can reuse it.
- **The frame title is short by design.** "Claude Code + Tamheed" alone: a longer title at the top-left
  would have lain under the operator's left edge, which drops at the planning lane's centre. "one
  agent, two halves" went to the captions.
- **Six overview labels left** (`understand`, `explore`, `plan`, `executor`, `readiness`, `close`):
  the phases live in the planning lane's second line, the readiness verdict in the operator's label.
  The orphan check demanded the removal.
- **The README image recipe:** the page served over HTTP (the browser blocks `file:`), English, light,
  a 2560 x 1800 viewport with `document.documentElement.style.zoom = '2'` (the page lays out as at
  1280 and scales whole, so nothing overflows its container), the D1 `svg.dia[lang="en"]` element
  captured at CSS scale. The first two attempts widened the element past its figure and caught the
  page background behind it (a band, then a hairline). Not a byte-twin surface; 209 repeats the recipe.
- **Captures** under `plans/evidence/captures-201/`: D1 and D2 in English light and dark and Arabic
  light at 1280, D1 at 390 (no horizontal page scroll: `scrollWidth == clientWidth`).
- **The isolate, measured in the page:** a click on the planning lane's rect sets `dim` on the SVG,
  `data-active` on the lane and its pill, none on the execution lane; a click on the frame's rect
  clears `dim` (the frame carries no key).
- Lint 14 caught the alt text (three semicolons) and one 26-word caption sentence; fixed.

## Rulings taken at the review (2026-10-04)

- Approved and committed as staged.
- **G17:** the frame primitive as built: a region, not an object. Drawn behind the edges with no
  fill and a short top-left title, never a click target. The lint checks it stays on the canvas and
  holds every member it names, and skips it for crossings, borders and label touches. The fallback
  (two adjacent lane boxes, no frame) declined. The 203 swimlanes reuse it.

## Validation

- `python docs/guide/build.py`: 1,391 ids, 0 missing, 0 orphans, the geometry lint green on both copies
  (the frame rule included). `test_user_guide` OK (10 tests, the frame case in).
- `python check.py`: ALL CHECKS PASSED.
- Captures as listed; the README image re-exported.
