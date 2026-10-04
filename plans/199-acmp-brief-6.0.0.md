# Plan 199: the ACMP brief 6.0.0, every class replayed on a copy first

> Maintainer-executed, 2026-10-04. Batch record: [192-200-batch-prompts.md](192-200-batch-prompts.md).
> Rulings P9, R47 (the maintainer's recommendation marked), R53 (no report unless a class fails).
> Ledger first. Every class holds on a `git archive` copy of the field package before the brief is
> written (`plans/evidence/scripts-ste/acmp_replay11.py`). Strict mode (the brief is rostered).

## Status
- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (the first MAJOR brief with a migration since
  4.0.0; the field's package was last emitted under 5.0.0, its note is v5 and its guide the 5.8.1 body) - **DONE 2026-10-04**

## What this beat changes

- `plans/briefs/acmp-6.0.0.md`, strict, rostered by path (`check.py` lint 14; the 5.9.0 brief leaves
  the roster, `tests/test_check_lints.py` follows). Sections: errors owned; the upgrade and what a
  session meets; the classes (hold, or a feedback row); the STOP (approve the kickoff, bind the
  skill-half rows, fix the file-era sentences); not built; if a class fails.
- The classes, in the brief's order: update and client restart; `package_migrate` preview on a CLOSED
  package (four files -> four Proposed rows, `prm-next.md` the kickoff by the header's file name, the
  5.8.1 stock guide removed, the folder removed, `prompts-v5-backup/`); the confirm on the word; the
  STOP (the emit refuses while `PRT-001` is Proposed); the approval in place and the two bindings
  (`project-invariant-audit` -> `integrity-check`, `project-deferred-work-cautions` ->
  `replan-deferred`; `project-design-review` names no scenario skill that reads it);
  `handoff_emit(refresh_stock=true)` (the note v7 with the roster; the stale scan names
  `AGENTS.md:39`'s `tamheed-package/prompts/prm-next.md`; the guide reported `unchanged`, seeded by
  the migrate); the export (the Prompts section); readiness (`prompt-ids-resolve` and
  `prose-plain-english` over rows, G-SET); the wire (one description changed, `entity_query` gained
  `plugin_skill`); the hook over the v5 note and the v7 note.
- The field's own pointers the emit cannot see: `.claude/memory/prm-next-carried-rules.md:10`.

## Pin ledger

- The brief is a new file: `plans/evidence/scripts-ste/pins-199.md` records the pinned phrases that
  occur in it (quoted engine messages). No existing pin moved. The roster line in `check.py` and
  its test moved from the 5.9.0 brief to the 6.0.0 brief (the 5.9.0 brief leaves the roster).

## What landed, beyond the plan

- **The 5.9.0 brief is superseded on the day it was written.** Both releases shipped on 2026-10-04.
  The copy's page says `review_exported_by "5.8.1"` and its note is v5: the client the field last
  ran was 5.8.1. The brief says so, compares every "changed" claim with 5.8.1 (the advisor's
  catch: 8 descriptions differ from that client by the wire itself, not one), carries the 5.9.0 STOP as a pointer,
  and owns the 5.9.0 brief's file-era promises (O24).
- **A 6.0 server before the migration reads none of the field's prompt files** (O25): the rules are
  blind to them (1,286 texts, `prompt-ids-resolve` indeterminate) and G-SET passes vacuously because
  the registry gains `prompt` only at the migrate. The brief says it is the warning.
- **The kickoff's own body carries a file-era pointer** (`PRT-001.body:22`, to
  `tamheed-package/prompts/README.md`): the stale scan over rows named it beside `AGENTS.md:39`.
  The emit cannot see `.claude/memory/prm-next-carried-rules.md:10`; the brief names it.
- **The 5.9.0 counts return after the migrate.** Before it, `prose-plain-english` named 1,286 texts.
  After it, 1,294: the four rows' titles and bodies, the same eight texts the 5.9.0 rule read as
  files (3,602 / 2,342 / 631 / 1).
- **Class 7 and the recommendation agreed only after the advisor's read:** the class demanded the two
  stale pointers while §3 recommended rewriting them before the emit. The class now holds either
  way. G-IDS in class 5 was unmeasured until the replay observed it (pass).
- **A regex over the TOOLS table read 12 of the 19 descriptions** (seven span lines) and would have
  sent the field "3 changed". The wire (`tools/list` on the v5.8.1 bundle and on HEAD) is the
  instrument: 8.
- **The guard's batch message is generic** ("batch rolled back — one or more items violated
  constraints"); the item carries the rule. The brief says the guard refused `design-review`.
- **Nine of my sentences failed strict mode** (five semicolons in the classes table, three long
  sentences, the word `delete` twice); all fixed before the gate.

## Rulings taken at the review (2026-10-04)

- Approved and committed as staged.
- **P21:** the 5.9.0 brief is superseded by the 6.0.0 brief and is not executed (both releases shipped
  on 2026-10-04, the field's client was 5.8.1). The 6.0.0 brief says so in its preamble and carries
  the 5.9.0 brief's one STOP (the rewrite of the record's prose) as a one-line pointer to
  `acmp-5.9.0.md` §3, adding nothing to it. Every "changed" claim in a brief names its comparison
  base, and the base is the field's measured client.

## Validation

- `acmp_replay11.py` on the copy at `8b7d8bd1`: every class held (`acmp_replay11.out.txt`).
- `ste_lint --mode strict` on the brief: 0 hard. `python check.py`: ALL CHECKS PASSED (the brief is
  rostered; `test_current_brief_is_in_the_roster` on the 6.0.0 path).
