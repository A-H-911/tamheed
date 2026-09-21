# Plan 084: Release v4.10.0

> Reviewer-executed (maintainer-delegated), 2026-09-21. Batch map:
> [075-084-batch-findings-26.md](075-084-batch-findings-26.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW (the plan-058 recipe, plus one new step)
- **Depends on**: 075-083 DONE - **Planned at**: commit `4a0bbb9`

## Preconditions, verified before this plan ran

- Every plan of the batch is DONE in the index; CI green on each pushed commit.
- Acceptance: 20/20 on the batch tree and 0/20 on an extracted `v4.9.0` tree, each failure its
  own; nine suites clean under `error::DeprecationWarning`; self-test 19/19.
- Lab beat 17 (`4a0bbb9`) reviewed by re-running its done criteria, not by reading its report:
  the 12 new assertions each exit non-zero against the pre-beat fixture extracted from git
  (`git archive 37b6366`) and 0 against the fixture; `lab-tracker` 56/56; `python check.py`
  green on main after the fast-forward.

## The recipe (plan 058), as run

1. `plugin.json` 4.9.0 -> 4.10.0; the six stamp lines (`README.md` x2, `SKILL.md`,
   `prompts/README.md`, `artifact-catalog.md`, `server/README.md`).
2. CHANGELOG: `[Unreleased]` becomes `## [4.10.0] - 2026-09-21` under a MINOR lead-in; a fresh
   empty `[Unreleased]` above it.
3. `stock-history.json`: `README.md` re-set under `4.10.0` AFTER its version line moved
   (`register-liveness.md`'s `4.10.0` key was set by plans 075/079 and does not change).
4. **New step - the lab fixture follows the stamp (finding F-1).** See below.
5. `python check.py`; advisor review; commit from a message file; annotated tag `v4.10.0`; push
   with tags; CI green on the tagged commit.

## Finding F-1, and why the recipe gains a step

Found while beat 17 was running, by comparing the fixture's prompt guide with every recorded
body: it matched NONE. Beat 16 had refreshed it to the then-current stock; the 4.9.0 release
then moved the guide's version line and re-set the `4.9.0` history key, so the fixture held a
body no key records. The classifier is byte-equality against history, so the file read as
`customised` - and `refresh_stock` never touches a customised file, forever. Beat 17 cleared it
by tool (`force`, after verifying it was the only diverged file and differed by one line), but
this release would orphan it again by the same mechanism.

It is lab-only: a field package refreshes AFTER a release and receives the released body. The
fix is therefore not in the engine but in the order of the release: once the stamp has moved,
re-emit the fixture's guide by tool so it byte-equals the released body, re-export the review
page, and confirm gates, verify and `review_current`. The script refuses to force unless the
guide is the fixture's only diverged file and differs from stock by exactly the version line.

Not done, deliberately: recording pre-release bodies in the history (keys are release versions
and sort numerically; an in-between body is not a release).

## Done criteria

- [x] lints 4, 5, 8, 9 green inside `python check.py` -> `ALL CHECKS PASSED`
- [x] the fixture's `prompts/README.md` byte-equals the released stock body; `diverged: []`
- [ ] tag `v4.10.0` on the release commit; CI green on it
- [ ] master record status -> EXECUTED; index rows 083, 084 DONE; memory updated
