# Plan 203: the figures folder, proven on the twelve workflow swimlanes

> Maintainer-executed, 2026-10-04. Batch record: [201-210-batch-guide-round-2.md](201-210-batch-guide-round-2.md).
> Rulings G12, G13, G17, G3; the round-1 bar. Ledger first. One commit.

## Status
- **Priority**: P1 - **Effort**: L - **Risk**: MEDIUM-HIGH (a new generated surface: sibling files the
  byte-twin must cover on Windows and Ubuntu; standalone SVGs carry their own colours and fonts; the
  swap script must keep the explicit theme toggle honest) - **DONE 2026-10-04**

## What this beat changes

- **The figures folder (G13).** `build.py` writes `docs/guide/figures/<id>-<lang>.svg` and
  `<id>-<lang>-dark.svg` for every per-item figure, LF, deterministic; `.gitattributes` pins the folder
  to LF; the byte-twin test compares the folder as it compares `index.html`; `--check` covers both. A
  standalone file embeds its own `<style>` with the theme's colour tokens resolved and the font stacks
  without the web fonts; the geometry lint runs on the model as for the inline figures.
- **`render.figure_file()`** emits `<figure><picture><source media="(prefers-color-scheme: dark)"
  srcset="…-dark.svg"><img src="…svg" alt="…" width height></picture><figcaption>…</figcaption></figure>`
  per language; `guide.js` swaps the two sources on the explicit theme toggle (system leaves the media
  query to the browser).
- **The twelve swimlanes (G12).** One per recipe of the Workflows section: three lanes (operator,
  agent, engine) drawn with the frame primitive, one node per step placed in the lane of the party
  that acts, the steps linked in order, the handoffs between lanes as the edges. Each step gets a
  short label EN + AR (`workflow.<slug>.s<k>.short`) beside its existing sentence.
- Captures: two swimlanes EN/AR light/dark, the swap observed on the toggle, 390 px.

## Pin ledger

- Before: `plans/evidence/scripts-ste/pins-203.md` (23 pinned phrases in the six guide files, none
  on the workflows). After: `pins_missing.py`: 0 missing.
- Invariants: `plans/evidence/scripts-ste/invariants-203.md` (5 files). The one modal drop, `only`
  4 -> 3 in `render.py`, is the slug `intake-only` leaving with the RECIPES table, not a hedge.

## What landed, beyond the plan

- **The primitives were proven on one recipe first** (new-project, both languages, both themes, the
  swap observed), then the other eleven were authored. The order paid: three defects surfaced on the
  first recipe and cost no labels.
- **The Arabic files lost their direction** (the advisor's call): an SVG loaded as an image inherits
  nothing, so the file style sets `direction` on the root. Then the Latin tokens inside Arabic lines
  came out bidi-reordered ("tamheed:tamheed/ mode full--"); the text helper now wraps every Latin run
  in a left-to-right isolate (U+2066 … U+2069) in the RTL copies, brackets left outside the run. The
  inline copies share the helper.
- **The file figures' labels were orphans** until `figure_file()` resolves them through the text table
  once (the build resolves them again when it writes the files).
- **The label-width rule** (`label_problems`, the file models only): a line must fit its box by the
  width estimate at its font size. It fired on 12, then 7, then 5, then 2 labels across the four
  builds; the columns now take the lane width over the step count (a six-step recipe has 135 px
  boxes, a four-step one 200 px), and the longest labels went to three lines.
- **The lane rule** (put to the operator): an operator's command or word is the operator's lane; a
  tool the agent calls, or a skill it runs, is the agent's; the engine's own behaviour (a hook, a
  refusal, a verdict, a sync) is the engine's. 61 step labels EN + AR, 3 lane titles, 1 caption;
  the alt text is the recipe's title and the caption.
- **The folder, measured:** 48 files (12 recipes x 2 languages x 2 themes), 312 KB, written exactly
  and strays removed; `build.py --check` says "index.html and 48 figure files are the fresh build";
  the Arabic files carry `direction:rtl`, every file `<style>` and no CR.
- **In the page, measured at 1280:** the image loads at its intrinsic 900 x 294 and renders at 888 x
  290; under the explicit toggle `currentSrc` moves between `wf-new-project-en.svg` and
  `wf-new-project-en-dark.svg` with the `<source>` media set to `not all`; at 390 px the image is 640
  px wide and scrolls inside its wrap, the page has no horizontal scroll (375 == 375).
- **The explicit-dark flash, disclosed:** the boot script sets the theme before paint, but the swap
  runs from the page script at the end of the body, so an explicit-dark reader sees the light figure
  for a frame. The cost of G13; 210 decides whether a fix is owed.
- **Lint 14 read the embedded style string as prose** (nine semicolons, a 49-word sentence): the
  style is built from declarations with the separator kept out of every literal.
- **Captures** under `plans/evidence/captures-203/`: new-project EN light, EN dark (the swap),
  AR light (after the isolate fix); release EN light; lock-recovery EN light; release at 390 px;
  D1 inline Arabic after the isolate helper (every Arabic SVG text on the page passes through it,
  the inline copies included). Every capture is of the staged build.

## Rulings taken at the review (2026-10-04)

- Approved and committed as staged.
- **G18, the lane rule:** a step sits in the lane of the party that acts. An operator's command or
  word is the operator's lane; a tool the agent calls, or a skill it runs, is the agent's; the
  engine's own behaviour (a hook, a refusal, a verdict, a sync) is the engine's. A step that reads
  wrong is fixed against the rule.
- **Three postures of G13 accepted:** the explicit-dark flash on the file figures (210 decides
  whether a fix is owed); the file figures render in the system serif, not the web font; every
  Arabic SVG text passes through the Latin-run isolate, a middle-dot list kept as one run.

## Validation

- `python docs/guide/build.py`: 1,455 ids, 0 missing, 0 orphans, the geometry lint and the label-width
  rule green on both copies of the twelve models; 48 figure files. `test_user_guide` OK (12 tests, the
  folder test in).
- `python check.py`: ALL CHECKS PASSED.
- The numbers above measured in the page at 1280 x 900 and 390 x 844.
