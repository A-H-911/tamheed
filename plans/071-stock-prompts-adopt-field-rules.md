# Plan 071: Stock prompts adopt the portable field rules - and drop two stale teachings

> Reviewer-executed (maintainer-delegated), 2026-09-21. Batch map:
> [063-074-batch-findings-25.md](063-074-batch-findings-25.md). Depends on 064, 066-070
> (lint 9b: a prompt may only teach vocabulary the engine has).

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: LOW (prose; needle-pinned; history-keyed)
- **Category**: teaching surface - **Planned at**: commit `0a27713`

## Why this matters

ACMP's lessons register holds rules the field paid for that are true of ANY tamheed package, and
three of its project prompts carry text its own authors call generic. Reading the stock library
to place them surfaced two teachings that were **wrong**, both in `prompts/README.md`:

1. "delete `data/.lock` when EITHER proves staleness" - the hand-run two-discriminator test that
   plan 064 replaced with `package_unlock`.
2. "Repair from `data/*.jsonl` ... never from `entity_query` output - a full-row upsert rebuilt
   from a truncated query round-trip re-commits the damage." `entity_query` truncates no field
   (its own docstring says so), and `orient-resume.md` in the same library says never to read
   `data/*.jsonl`. The field's version of this claim "pushed this project onto the JSONL for
   three weeks" (their words), cost 78 ad-hoc scripts and an integrity audit.

## What changed (four stock prompts; each body appended to `stock-history.json` under `4.9.0`)

- `README.md`: the lock section teaches the observation and `package_unlock` (operator's words;
  refuses on `alive`/`unobservable`; the manual path stays for what this host cannot see). A new
  **Asking the operator** section - the operator-authored interview spec: homework first, one
  decision per question, **show the record with its id**, **ask every time**. The repair rule
  becomes "build the payload from a read made FOR transmission" (`entity_export`, or a whole
  `entity_query` result) "never from a display"; the verifier re-reads through the tools.
- `integrity-check.md`: **What a green run does not prove** - every gate is row-level; report
  each rule's `population` and every `discriminating: false`, the `narrated` verdicts, and
  `prose-ids-resolve`; a vacuous pass is a finding.
- `replan-deferred.md`: for every FIRED trigger, say **which words of the trigger** matched; a
  row never started is not a gap to fill.
- `orient-resume.md`: a refused open names the observation and `package_unlock` (never the
  agent's call); **search finds candidates, an exact read decides** (`matched`,
  `omitted_columns`; project to enumerate, never to answer a state question).

## Tests

`test_stock_prompts_teach_the_field_rules` pins every addition by needle and asserts the three
stale sentences are gone. RED before, GREEN after. Lint 9 (stock history current, 83 bodies) and
lint 9b (teaching surface speaks only engine vocabulary) green. One first-run failure was a line
wrap splitting the already-pinned phrase "Never auto-clear".

## Consequence, stated

A package that customised `integrity-check.md` or `orient-resume.md` does not receive these by
refresh (customising opts a file out, by design); `handoff_emit` names how far its stock moved.

## Done criteria

- [x] `python tests/test_mcp_contract.py` -> OK (153); `python check.py lint` -> no FAIL
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`. **Four stock prompts changed**, each with
its `4.9.0` history key in this commit; plan 074 re-sets `README.md`'s key after the version
line moves. The lab fixture's prompt copies are refreshed by beat 16.
