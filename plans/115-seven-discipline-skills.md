# Plan 115: seven discipline skills, adopted from ACMP's promoted skills under tamheed names

> Reviewer-executed (maintainer-delegated), 2026-09-24. Batch map:
> [112-119-batch-findings-31.md](112-119-batch-findings-31.md).

## Status

- **Priority**: P1 - **Effort**: L - **Risk**: MEDIUM (a standing-instruction surface every enabled session sees)

## Why this matters

ACMP's operator distilled ten project skills from 100 confirmed lessons; seven are generic tamheed discipline every package would want (interview: four package-facing, three evidence-facing; the three engineering-only stay ACMP's). Plugin-shipped, one source, updated by the plugin.

## What changes

`package-writes` (writing-to-the-package + the note's cheat-sheet rules; points at the note's table), `reading-the-record` (before-you-cite-a-record), `operator-interview` (interviewing-the-operator), `written-claims` (keeping-written-claims-true steps 1/3/5/7), `test-evidence` (trusting-a-green-test), `measurement-evidence` (trusting-a-measurement steps 1-3/5/8), `ci-evidence` (steps 1/5). Procedure + anonymised field evidence; stack-neutral; standing instructions.

## Done criteria

- [x] lint 12 clean (name, description, ≤ 500 lines, denylist)
- [x] a reviewer pass: security (standing-instruction surface) and neutrality (principle 9)
- [x] `python check.py`
- [ ] CI green

## Execution note (2026-09-24/25)

An independent reviewer read the seven bodies against `tamheed_server.py`, the DDL and the references
and returned 16 findings (2 HIGH, 6 MEDIUM, 8 LOW); every engine claim it verified as correct is listed
in its report. Verified in source and fixed: **HIGH 1** — the flush sentence named `export_html` and
`handoff_emit` as JSONL flushers; only `entity_upsert`, `progress_update`, `audit_record`, `work_bind`,
`package_verify(record=true)`, `package_unlock(confirm=true)` and `package_close` reach `_commit()`
(the two emitters write other package files; the "tree is dirty" conclusion held). The note has carried
that mechanism since plan 039 and ACMP's AGENTS.md repeats it — the v5 rebuild (plan 116) corrects the
note, the guide and the template; the brief owns it. **HIGH 2** — the defect status set is
`Fixed`/`Won't-fix`/`Duplicate` (ACMP's own skill text carried `Won't-do`/`Obsolete`). MEDIUM/LOW:
`substitute` is an item shape not a tool; only `go_no_go` is the gated header field; the ceremony list
made complete ("Among …" + the lesson-off-Approved, feedback-withdrawal and `package_adopt` words);
the branch-workflow sentences made stack-neutral; the lock sentence no longer licenses a hand removal;
the re-run refusal stated exactly and the refusal count dropped; the CLR-flavoured idioms neutralised;
the two verdict-recording sections no longer echo the obligations table's field list; cross-references
name skills. **Partially accepted:** the footers now say the instances are illustrative and anonymised;
the anecdote figures stay (the interview chose evidence over bare procedure). **Reconciled, not
changed:** `package_verify(record=true)` is not engine-gated on the operator's word (the reviewer is
right about the mechanism); the skill now states the mechanism and keeps the doctrine as advice
("journal a verification when the operator wants the record").
