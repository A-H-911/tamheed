# Plan 212 -- the repository is wired to its package at birth

> Status: DONE 2026-10-08 (maintainer-executed, the operator's rulings by question).
> Engine change, additive: a MINOR, released by plan 213 as 6.2.0. The approved plan with its two
> devil's-advocate reviews is the operator's plan file; this ledger is the repo's record.

## The gap, as observed and measured (2026-10-08)

The operator ran `/tamheed:tamheed` in `C:\Users\ahammo\Repos\jisr`, a repository with no `CLAUDE.md`.
The planning half read the brief, created `tamheed-package/` (188 rows when read, the lock held by the
live session, `entry_point: null`) and wrote a `handoff` journal entry, PE-003: "Resume at: stage 7
(clarification). The first interview round was put to the operator and not yet answered...". No root
`CLAUDE.md` exists, and the engine creates none before stage 20's `handoff_emit`.

- The SessionStart hook (`server/resume_hook.py`, `find_note` L73-87) finds a package only through the
  note span in the root `CLAUDE.md` or one `@` import. Without a root file it prints nothing. Every
  new session, `/clear`, compaction or fork in `jisr` gets no resume block, although PE-003 is exactly
  the block the hook prints.
- Seventeen scenario skills resolve "the package this project's `CLAUDE.md` Tamheed note names"; none
  covers a project with no note.
- `handoff_emit` on an absent root (L4417-4500) reads `""` and appends the note, so the first
  `CLAUDE.md` a repository gets is the Tamheed note alone.
- The pointer pattern (`handoff.md` L143-146: a root heading plus `@<package>/CLAUDE.md`, the span in
  the package's own file) was written by hand in the field (ACMP, August) and in every lab setup
  script. The engine recognised it and never wrote it.

## Rulings

- **R67 (2026-10-08): birth and open.** `package_create` and `package_adopt` wire the repository;
  `package_open` wires an unwired root (idempotent). `jisr` is wired by its next open under 6.2.0.
- **R68: append the pointer section** (heading + import, three lines) to a root `CLAUDE.md` that has
  no Tamheed section; content outside the section is never touched; the result reports `root: appended`.
- From the reviews, not put to the operator (engine facts): the wiring runs only in a served process
  (`_WIRE_ROOT`, set in `main()`), because `evals/pkg_check.py` and six test files open packages
  in-process on committed fixtures; the stub imports `AGENTS.md` only when the file exists (the vendor's
  table: a `CLAUDE.md` beside an `AGENTS.md` makes Claude read the `CLAUDE.md` only, unless it imports
  the other); the package planning note is written only when the root's section is the pointer, never
  beside an inline span.

## The mechanism, as landed

`_wire_project(pkg_dir, name, conn)` beside `_emit_prompt_library` in `tamheed_server.py`, called by
`package_create` (after the stock guide), `package_adopt` (on post-flight, inside its own store
context) and `package_open` (after the store opens). It returns `None` unless `_WIRE_ROOT` is true,
which `main()` sets after `PACKAGE_ROOT` resolves and the selftest check: only a served process writes
the project's root. Order: the root first, then the package file only when the root's section is the
pointer. The root `CLAUDE.md`: absent → `_root_stub(title, name, agents)` (the `packages` row's title,
the operator's comment with `@AGENTS.md` in backticks, the bare `@AGENTS.md` import only when that
file exists, the heading, `@<name>/CLAUDE.md`) → `created`; present without the heading → three
lines appended → `appended`; present with the heading → `present`, and the package file is written
only when the section is the pointer (import line, no inline span). The package file: no span and no
heading → `_planning_note(name)` (the heading, one `v7` span whose first sentence is `_PKG_RE`'s
phrase and whose marker words are `_PLANNING_MARK`) → `planning`; else `present`. The result key is
`wiring`. `handoff_emit`: `_apply_note` replaces a span carrying `_PLANNING_MARK` with the warning
"the planning-era note in <path> was replaced by the operating note" instead of the hand-edit one;
a root whose first non-blank line is the heading is reported "note-only", never rewritten.
`_resume_block`: `half` from `packages.entry_point` (null → planning), a planning `next` that names
`/tamheed:tamheed` and opens "No handoff recorded" when there is none; the execution wording is
unchanged. Four descriptions name the wiring; "CLAUDE.md note" stays literal in the emit's. The
selftest reads 19/19, the longest description 387 characters.

## Pin ledger

- `plans/evidence/scripts-ste/pins-212.md` (16 pinned phrases over `handoff.md`, `workflow.md`, the
  agent-control template); `pins_missing.py`: 0 no longer occur.
- The guide's hand maps cite server lines; the engine patch inserted lines, so every citation was
  re-aimed by a difflib line map from HEAD (`plans/evidence/scripts-ste/labrun-212/shift_212.py`,
  committed: a hand map of server lines moves with every insertion above it, so the re-aim is a
  tool, not a one-off; one citation, `@resume`, sat on a changed line and was set by hand to 1406). `tests/test_user_guide.py` pinned four server lines by number
  (the views call, the two lesson events, the Superseded retirement) and was re-aimed the same way.

## Tests

Red first (nine errors and one failure against the unchanged engine), then green. `WiredAtBirthTest`
in `tests/test_mcp_contract.py`: the stub and the planning note on an empty root (and the no-`@`
rule, and `resume.half`); the `@AGENTS.md` import when the file exists; the appended pointer on a root
without the section; a root with an inline span left alone and no package note; open wires once and
reports `present/present` after; adopt wires on confirm; the emit replaces the planning note (one
span, the marker gone, the root byte-equal, the "replaced" warning, no "tool-owned", no "note-only",
the plan-125 scans quiet on the stub, `half` execution); a note-only root on a foreign target is
reported and not rewritten; in-process callers write nothing. `tests/test_resume_hook.py`: a
birth-wired planning package resumes through the hook with the planning `next`. Existing tests did
not move: `DEMO_DATA` carries `entry_point: "PRT-002"` (execution), and the planning no-handoff
sentence still opens "No handoff recorded". Whole suites on the final tree: contract `Ran 217 tests`
(the nine new ones inside), hook `Ran 18 tests`, user guide `Ran 16 tests`, round-trip and export
OK, `check.py` ALL CHECKS PASSED.

## The lab beat 35

`plans/evidence/lab-continuation-report-212-2026-10-08.md`; the scripts and outputs under
`plans/evidence/scripts-ste/labrun-212/`. A scratch repository from the lab seed with no `CLAUDE.md`,
three turns by a real agent (Opus 5.5, the headless harness), each a new process: T1 the birth
(`wiring: created/planning`, the stub and the planning note quoted whole, `PE-001`; 8 turns, $0.23);
T2 the hook in a new process (the block printed through the pointer with `PE-001`'s text and the
planning `next`, trace `status=printed` after T1's `status=silent`; `wiring: present/present`, `half`
planning; 4 turns); T3 the emit (the "planning-era note ... replaced" warning, "the root file was
left untouched", `unchanged: ["CLAUDE.md"]`, one span, the marker gone, the root byte-equal, `half`
execution; 19 turns, $0.70 cumulative, one denial: the agent's own `git status` under the harness's
permission mode). The plugin refused nothing in any turn. `lab/scenario.md` beat 35 records the
scratch phase; the recorded fixture does not move. **A method change from the approved plan:** the
plan's run A said "the kickoff as the whole prompt" (the front door skill); the beat used the
operator's words naming `package_create`, so the front door was never invoked. The mechanism was
exercised by a real agent through the served process either way; the posture is put to the operator
at the review.

## Captures

`plans/evidence/captures-212/`: the eight figure ids this beat changed (the three effects canvases
that gain a `CLAUDE.md` write; the five gate figures whose labels carry server line numbers),
EN/AR x light/dark, 32 files, by `capture_212.py` through the Python Playwright runtime (the MCP
browser servers did not connect this session). A capture includes its caption.

## Not built, by ruling or on purpose

- Wiring at `package_migrate`: a migrated package's repository is already wired (ACMP's is);
  `package_open` covers one that is not.
- A generated root `CLAUDE.md` body beyond the stub: ASM-B stands (repository scaffolding was removed
  in v2); the project's rules are the operator's, the template is `AGENTS.md`.
- A change to the hook: one import level already reaches the span.
- Six doc sentences that stay true after the change, each a strict-roster edit with pins, deferred:
  `agent-control.template.md` L4-7 ("hand-maintained") against L22 ("regenerated each update cycle");
  `templates/README.md:30` ("`CLAUDE.md` + `AGENTS.md` ... Derived"); the three "prints nothing in a
  project whose `CLAUDE.md` carries no tamheed note" sentences (`docs/install.md:98`, `SECURITY.md:32`,
  `docs/architecture.md:259`).
- Rewording the stock guide's four "the target's `CLAUDE.md` note" lines: still true (the note is
  reached through the root file); lint 9 and 213's stamp assert the body does not move before the key.

## Rulings taken at the review

- **R69 (2026-10-08): the lab's words route accepted.** Beat 35 ran by a real agent through the
  served process on the operator's words naming `package_create`, not by invoking `/tamheed:tamheed`
  as the plan's run A said. The engine's path is the same; the front door's own route to
  `package_create` stays unmeasured, said here and in the report.
- **The commit as staged**, 93 files. No push: plan 213 releases 6.2.0 and asks before the push.

## Validation

- `python check.py lint` on the first pass (the lint roster includes the server's own strings and
  descriptions, so a tool description is prose too): in the server two long sentences and two
  semicolons; `handoff.md:139` one long sentence and the vocabulary hit `gets`; one long sentence
  each in `workflow.md:16`, `README.md:236` and later `migrate-from-keystone.md:109`; four in the
  design-decisions entry; in the guide's new prose one EN and two AR. Every finding split or
  reworded. Then `python check.py`: ALL CHECKS PASSED (lint 8 unchanged at 6.1.0; lint 14 at 0 hard;
  the guide byte-twin; `build.py --missing` 0 over 1,546 ids; the evals).
- `git status --porcelain` after the gate: the intended files only, no fixture `CLAUDE.md`.
- `uv run plugins/tamheed/server/tamheed_server.py --selftest` on the final descriptions: 19/19,
  "longest 387 characters (the client's cap: 2048)".
