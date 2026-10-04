# Plans 201-210: the user guide round 2 (v6.1.0), the batch record

> Maintainer-executed, opened 2026-10-04 after the v6.0.0 tag (G15). The approved plan lives in the
> operator's plan file (sections 5.7 and 5.8); this file is the durable record in the repository:
> the rulings, the beat map, what shipped per plan, the errors owned, what was not built. One plan
> and one commit per beat (G3). Batch A (plans 192-200, the prompts family) is the record this one
> follows: [192-200-batch-prompts.md](192-200-batch-prompts.md).

## 0. Why

Plan 175 round 2 opened with thirteen notes from the operator on the generated user guide
(`index.html`): D1 showed Claude Code only as the executor and "two agents" where there is one agent
in two halves; D3's loop arrows; a figure per workflow; per-family relation and flow figures; D5's
left column; per-tool, per-gate and per-skill figures; the pager that differed between the two
languages; the left nav. The prompts question among those notes became batch A. This batch draws
the engine as it is after 6.0.0.

## 1. Rulings (interview 2026-10-04, carried from the batch A record, and this batch's own)

| # | Ruling |
|---|---|
| G1 | One agent, two halves: D1 and D2 show the operator on top, one "Claude Code + Tamheed" box with two lanes (the planning half, stages 1-20 and its tools; the execution half, stages 21-22 and its tools), the handoff as the arrow between the lanes, the MCP server and the package below. The README overview image follows D1. |
| G3 | Protocol: one plan and one commit per beat; ledger first; `check.py` green; the geometry lint green on both copies; captures EN/AR, light/dark, 390 px where a page changes; advisor read; the operator's ruling by question; one commit. |
| G4 | Per family: a relations figure plus three flow figures (lifecycle, data path, trace path); stage legs from a parser over workflow.md's `**Writes:**` lines. |
| G5 | D3: the three dashed loop-back arcs become orthogonal dashed returns in a channel above their lane. |
| G6 | The pager (D7, D8) in rem units, identical in both languages. |
| G7 | Tools: an effects canvas and a call-sequence strip per tool (19 x 2), the effects hand-authored with a server line per claim. |
| G8 | Gates: the pipeline figure, one per mechanical gate, one per judgment and warn gate. |
| G9 | Skills: the lifecycle map, the discipline citation matrix (derived), one strip per skill (27). |
| G10 | Nav: numbered sections, a two-level TOC, sharper titles, visible chapter structure. |
| G11 | Logo and icon: the two-half paving mark with a return arc; `icon.svg` redrawn from it; the tagline reconsidered. |
| G12 | Workflows: one three-lane swimlane per recipe (operator / agent / engine). |
| G13 | Per-item figures as sibling files (`docs/guide/figures/*.svg`) via `<picture>` and the script swap; D1-D8 inline; the byte-twin covers the folder; LF-pinned. |
| G16 | The word is "half": the planning half, the execution half; lanes labelled "Planning" and "Execution". |
| G17 | (plan 201 review) A **frame** is a region, not an object: a dashed box drawn behind the edges with a short top-left title, never a click target. The geometry lint checks it stays on the canvas and that every member it names lies inside it, and skips it for crossings, borders and label touches. The fallback declined: two adjacent lane boxes with no frame. |
| G18 | (plan 203 review) The lane rule of a swimlane: a step sits in the lane of the party that acts. An operator's command or word is the operator's; a tool the agent calls, or a skill it runs, is the agent's; the engine's own behaviour is the engine's. Three postures of G13 accepted: the explicit-dark flash on file figures (210 decides a fix), the system serif in file figures, the Latin-run isolate in every Arabic SVG text. |

## 2. The beat map

| # | Beat | Status |
|---|---|---|
| 201 | D1 and D2 as one agent with two halves; the README overview image | DONE 2026-10-04 |
| 202 | The chrome: the two-level nav, D3's returns, D5's header pills, the pager in rem | DONE 2026-10-04 |
| 203 | The figures folder proven on the twelve workflow swimlanes (`<picture>`, the swap, the LF rule, the folder byte-twin) | DONE 2026-10-04 |
| 204 | Family relations figures | planned |
| 205 | Family flow figures with the Writes parser | planned |
| 206 | Tool figures | planned |
| 207 | Gate figures | planned |
| 208 | Skill figures | planned |
| 209 | Logo, icon, tagline | planned |
| 210 | Release 6.1.0 | planned |

## 3. What shipped, per plan

- **201 — D1 and D2 as one agent with two halves.** (the commit this record lands in) The frame
  primitive with its lint rule and test (G17); D1: the operator, the frame with the planning and
  execution lanes, the handoff, the server, the package, the review page; D2: the same shape with
  what each party may do, the isolate by party kept; the captions and labels EN + AR; six overview
  labels retired; the README alt text and image re-exported; captures EN/AR light/dark and 390 px.
- **202 — the chrome.** (the commit this record lands in) Numbered sections with the chapter as
  the kicker; the two-level TOC (each section's H3s get ids, a closed `<details>` per section the
  script opens for the active one, the summary a floating count and chevron); the nav fits 1280 x
  900 closed (754 px); D3's three loop-backs as orthogonal dashed returns in a channel above the
  lane; D5's row headers as boxes; the pager in rem with mono digits, identical in both languages
  (945 x 32, buttons 38.4 x 32); three titles sharpened; captures.
- **203 — the figures folder on the twelve swimlanes.** (the commit this record lands in) The
  per-item figures are sibling files under `docs/guide/figures/` (one per language and theme, LF,
  written exactly by the build, covered by the byte-twin and `--check`), embedded through
  `<picture>` with the script swap on the explicit toggle; a standalone file embeds the theme's
  tokens and its language's direction; the twelve recipes as three-lane swimlanes (the frame
  primitive, one node per step in the acting party's lane, 61 short labels EN + AR); the
  label-width rule for file figures; Latin runs isolated in RTL text.

## 4. Errors owned

- **201.** The frame label id was written without the `dia.` prefix the label helper adds (an
  orphan and two missing strings until renamed). The alt text carried three semicolons and a caption
  one 26-word sentence. The first README capture showed the page background behind the widened SVG.
- **202.** The first nav did not fit 1280 x 900 (the summaries took a line each); the desktop nav CSS
  would have swallowed the sub-lists until scoped; the tools section's pre-id'd H3s were left out of
  the sub-list at first; the Arabic numbers sat flush against their titles (a logical margin on an
  LTR element); two shell heredocs mangled backslashes again (scripts from files).
- **203.** The file figures' labels were orphans at first; the Arabic files reordered Latin tokens
  until the isolate; 26 label lines failed the width rule across four builds; the embedded style
  string tripped lint 14, then one label's semicolon; one import was missing on the first build.

## 5. Not built, by ruling or on purpose

(filled at the close)
