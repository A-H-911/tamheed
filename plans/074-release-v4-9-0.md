# Plan 074: Cut v4.9.0 - the findings_25 batch (plans 063-073)

> Reviewer-executed (maintainer-delegated), 2026-09-21, on the maintainer's interview answer
> "v4.9.0 with lab beat 16". The plan-058 recipe. Batch map:
> [063-074-batch-findings-25.md](063-074-batch-findings-25.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW (mechanical; lints 4, 5, 8, 9 enforce every step)
- **Depends on**: 063-073 DONE - **Category**: release - **Planned at**: the beat-16 merge

## Why MINOR

A new tool (`package_unlock`, 19 tools), new result fields on five tools, a new advisory rule and
one advisory that can now read `indeterminate`. All additive; no store shape, identifier scheme or
handoff contract change; no schema migration. -> 4.9.0.

## Steps (as executed)

1. `plugin.json` -> `4.9.0`; the six stamp lines (`README.md` x2, `SKILL.md`, `prompts/README.md`,
   `artifact-catalog.md`, `server/README.md`).
2. `stock-history.json["README.md"]["4.9.0"]` re-set to the stamped body (plan 071 had set the key
   before the version line moved). The diff is `1 insertion, 1 deletion`, not plan 058's 2/1:
   the key already existed, so the release replaced its body rather than adding a key.
3. CHANGELOG: `## [4.9.0] - 2026-09-21` with the MINOR lead-in; the `[Unreleased]` `### Added` /
   `### Fixed` / `### Changed` lists fall under it unchanged; `[Unreleased]` empty again.
4. `python check.py` -> `ALL CHECKS PASSED`; one commit; annotated tag `v4.9.0`; push with tags; CI
   fires on the push.

## Acceptance for the batch (063-073)

- A 20-check black-box script: 20/20 on the batch tree, 0/20 on an extracted copy of the pre-batch
  commit `dc4c5eb`, each pre-batch failure for its own reason (the missing key, argument or rule).
- Four suites green under `PYTHONWARNINGS=error::DeprecationWarning`; `--selftest` 19/19.
- CI 9/9 (Ubuntu + Windows, 3.10-3.13, plus the smoke job) on every plan commit.
- Lab beat 16, agent-driven in-process, reviewed by rerunning its done criteria: 44 assertions
  pass, gates ready, store verified; the fixture's data diff is one defect and two journal rows.
- Reviewers: a security and a Python reviewer on 063, 064 and 065 before commit. They found, and
  the plans closed: an `OverflowError` masking the lock refusal, an unbounded pid, a racing
  unlock that could remove a live writer's lock, an export that could delete another package's
  CSVs in a shared output directory, and a case-insensitive-filesystem self-deletion.

## Beat 16's observation, recorded not fixed

A whole-rule waiver (`WVR-002`, no `applies_to`) waived the beat's new low defect the instant it
existed. That is the documented meaning of a rule-scoped waiver and it is reported, never silent -
but it keeps absorbing rows written long after the operator approved it. Recorded as a future
option (an expiry, or a nudge when a whole-rule waiver absorbs a row newer than itself).

## Known, harmless lag in the fixture

Beat 16 ran before the bump, so the committed `exports/beat16-defects.json` envelope stamps
`"version": "4.8.1"` and the fixture's `prompts/README.md` reads one version line behind. No
lint or assertion reads either; beat 15's fixture lagged the same way. Not a finding.

## Done criteria

- [ ] `grep -n '"version"' plugins/tamheed/.claude-plugin/plugin.json` -> `4.9.0`
- [ ] `python check.py` -> `ALL CHECKS PASSED`
- [ ] `git tag -l v4.9.0` -> the tag; `gh run list --limit 1` -> `push`, success
