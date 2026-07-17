# Plan 012 (B6): The HTML viewer — the operator's review surface

> **Executor instructions**: Build plan. Deliverable = `export_html` implementation + escaping
> tests. STOP conditions are binding — the security section is non-negotiable.
>
> **Drift check (run first)**: plans 007+008 landed; the migrated demo package from plan 010
> exists (it is the primary render fixture). Missing → use `tests/fixtures`-derived DB packages
> and note it.

## Status

- **Priority**: P2
- **Effort**: M
- **Risk**: MED (security surface)
- **Depends on**: plans/008-b3-mcp-server.md (010 preferred for the fixture)
- **Category**: build / dx
- **Planned at**: commit `0e055f6`, 2026-07-11

## Why this matters

Maintainer decision D-REVIEW: the human review surface for v2 packages is **HTML only** — no
derived-Markdown snapshots. The operator follows the package and its execution progress through a
generated view. That makes this exporter load-bearing for human oversight: if it is unreadable or
insecure, the human gate degrades.

## Security requirement (adversarial finding W-V2-6 — non-negotiable)

Package content includes **brief-derived and repo-derived text, which is untrusted** (safeguard
18). Rendering untrusted text to HTML that the operator opens in a browser is a stored-XSS path.
Mandates:

- Every data-derived string is HTML-escaped at render time (stdlib `html.escape`; attributes
  escaped with quote=True). No exceptions, including "obviously safe" IDs.
- No inline event handlers; no `javascript:` URLs; links from data get `rel="noopener"` and only
  http(s) schemes (else rendered as plain text).
- A restrictive CSP `<meta http-equiv="Content-Security-Policy">` (default-src 'none'; style
  inline allowed via a nonce or 'unsafe-inline' for the static stylesheet; img data: if needed;
  **no script-src** unless the viewer ships its own static JS, which must never evaluate data).
- The export is **self-contained static HTML** (single file or file+assets dir): no network
  fetches, no server.

## What it renders

From the DB via read tools/`store.py` (never by re-parsing text files):

1. **Overview**: package identity, profile, iteration, gate_run verdict summary (per-gate chips).
2. **Registers**: one section per entity family (requirements incl. provenance + status +
   introduced_in, decisions/ADRs with status history via supersession chains, risks, OQs/ASMs…).
3. **Traceability**: the `trace_edges` graph — at minimum a matrix-style table (requirement →
   decisions → work items → tests → ACs); a graph visual is optional polish, not required.
4. **Execution progress**: acceptance criteria × audit verdicts (Met/Partial/Not-met/Pending),
   progress-log timeline, scope-change history (the agile trail).
5. **Gap/screening notes**: injection-screen flags and adopt-mode gap reports, rendered
   prominently — these exist to be seen by the human.

Rendering approach: stdlib only (string templates or a small internal HTML-builder in
`plugins/tamheed/server/export_html.py`); deterministic output (stable ordering — same DB state ⇒
byte-identical HTML). **The export is COMMITTED to the package's repo by default** (maintainer,
2026-07-17): determinism makes its diffs meaningful, and reviewers open the review surface
without running anything.

**Field-evidence renders (2026-07-17)**: every view shows its **freshness stamp** (C1 — three
real projects were misled by stale "derived" artifacts claiming currency); registers show
per-entity **last-referenced** (C3 — surfacing load-bearing vs forgotten rows); the roadmap
view shows **design-ahead lead** (C9 — approved-but-unimplemented as an explicit, healthy
state, per Marid's PH-7 pattern); status renders use the three-axis model (lifecycle / verdict /
disposition) from plan 007.

## Deliverables

1. `plugins/tamheed/server/export_html.py` + wiring into the `export_html` tool stub.
2. `plugins/tamheed/server/viewer.css` (static, embedded at export time).
3. `tests/test_export_html.py`: (a) renders the migrated demo (or fixture-derived package) →
   output contains the five sections; (b) **hostile-content test**: an entity whose statement
   contains `<script>`, an `onerror=` attribute payload, and a `javascript:` link → the output
   contains NONE of them unescaped (assert on the raw HTML string); (c) determinism: two exports
   of the same DB are byte-identical.
4. One usage paragraph in `plugins/tamheed/server/README.md`.

## Commands

`python tests/test_export_html.py` → exit 0; all prior suites green.

## Scope

**In scope**: the four deliverables + `plans/README.md`. **Out of scope**: committing exports of
real packages (optional per-user), any JS charting library (violates self-containment and the
security mandate), Markdown export (explicitly rejected by D-REVIEW).

## Steps

1. Build the renderer section by section against the fixture package; escape-first discipline
   (write the `esc()` helper before the first template string).
2. Hostile-content test (deliverable 3b) — write it BEFORE polishing visuals.
3. Determinism pass (stable ordering everywhere).
4. Wire the tool stub; extend MCP contract test.

**Verify** per Commands after each step.

## Done criteria

- [ ] All three test groups pass (sections, hostile-content, determinism)
- [ ] CSP meta present; grep for `onerror`/`<script>` in output of hostile test → only escaped forms
- [ ] Tool stub replaced; contract tests green; `plans/README.md` updated

## STOP conditions

- Any section seems to need JavaScript that evaluates data — redesign to static rendering or
  report; never weaken the security mandate for a visual.
- The migrated demo fixture is absent AND fixture-derived packages can't exercise all five
  sections — report which sections lack coverage.

## Maintenance notes

- Every new entity family (community extensions, plan 015) needs a renderer registration — keep
  a single section-registry in `export_html.py` so additions are one entry.
- Reviewer scrutiny: the escaping tests' payload list; determinism (dict ordering) on Python 3.10+.
