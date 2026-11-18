---
status: Approved
date: 2026-11-18
id: ADR-0005
supersedes: ADR-0003 (partially — the clause that the standup page runs no script)
superseded_by: none
---

# ADR-0005 — The standup page is a delivery report and runs one hash-pinned script

## Status

Approved (operator, 2026-11-18 — rulings U1-U20 in `plans/249-field-round-6.8.0.md`; plan 251,
release 6.8.0). The operator read a mock of the page on real field data before the build.

## Context

The standup page of 6.6 and 6.7 printed lists: what moved, the decisions, the defects. The
operator read it on a field package and found it hard to read. Most readers do not know Tamheed,
and the page is a delivery report first. A reader needs to see, for the window and overall:
what was done, what is in progress, what comes next, and the challenges and decisions. One view
of the whole plan, with the phases as its root, was asked for, with filters by state, kind and
phase, and a text search.

ADR-0003 kept the page in the review page's frame: one escape point and no script. Filters and
search over a tree of hundreds of rows need a script. The interview page (v6.5, plan 227)
already runs one script under a content policy that names it by its SHA-256 hash.

## Decision

1. **One script, named by its hash.** The page inlines the bundled `standup.js`. Its content
   policy is `default-src 'none'; style-src 'unsafe-inline'; script-src 'sha256-…';
   base-uri 'none'; form-action 'none'`. No other script runs: an inline handler, a second
   script block and a script in a row's text are refused by the browser. The script loads
   nothing, sends nothing and writes no markup. It reads data attributes and sets `hidden`,
   `open`, `aria-pressed`, one status text, and one stored colour choice (`auto`, `light` or
   `dark`; any other stored value is ignored).
2. **The page works without the script.** It then shows every row, unfiltered, and the colour
   switch still works (CSS). The filters appear only when the script runs.
3. **One state per row.** `standup_facts.row_state` gives each task and acceptance check one
   state, in a fixed order: done this window, claimed this window, done earlier, blocked, in
   progress, next, not started (checks: failed, not checked yet; postponed is outside the
   counts). Every count on the page reads it, so the cards, the chips and the tree agree.
4. **The facts grow.** A report row freezes the whole plan tree, the rows worked on in the
   window, every list uncapped, and the full registers of decisions, defects, risks and
   questions. The operator accepted the growth (about 120 KB a row more on a large package).
   The draft result the agent reads stays trimmed.
5. **Rows of 6.7.0** have no plan tree. They keep the old layout and run no script.

## Consequences

- SECURITY.md describes the page's one script. The browser check
  (`tests/run_standup_browser_check.mjs`) runs in CI in a job of its own, `standup-browser`,
  because `check.py` stays stdlib.
- The page is no longer limited to 1,400 or 2,000 words: lists fold after 8 items instead.
- A 6.7.0 engine still draws a 6.8.0 row in its old look: the facts keep every 6.7.0 key.

## Confirmation

`tests/test_standup.py` pins the policy hash, the single script, the absence of inline
handlers, the state table and the agreement of every count. The browser check pins what the
script does in Chrome, the contrast in both themes, the phone width and print.
