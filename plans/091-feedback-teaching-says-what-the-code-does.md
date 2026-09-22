# Plan 091: The feedback teaching says what the code does

> Reviewer-executed (maintainer-delegated), 2026-09-22. Batch map:
> [091-099-batch-findings-28.md](091-099-batch-findings-28.md).

## Status

- **Priority**: P2 - **Effort**: XS - **Risk**: LOW (prose; one stock body) - **Planned at**: `38fe344`

## Why this matters (findings_28 §3a-§3c, `FB-013`; and two things the field could not do)

- A `local-tool` row has no draft stage: `tool_arrives` fires on the first insert, so the operator's
  word is a precondition of the insert. The 4.11.0 teaching said "born Proposed … Confirmed only
  with operator_confirm" of every row, and ACMP would have been refused nine times had it followed it.
- The prose named "a wrong doc"; the enum is `doc-error`. Nowhere did the teaching name the kinds.
- `FB-013`: the local-tool rule read "reads `exports/` only, writes nowhere tool-owned" as one test.
  Three of ACMP's registered tools read or write project-owned files under `tamheed-package/docs/`
  and never touch `exports/` - they meet the intent and fail the letter.
- The 4.11.0 brief said "put the export file in your findings"; `exports/` is gitignored at ACMP by
  their own DEC-139 d4. What travels is the quoted envelope and rows.
- ACMP bound thirteen rows to an unpushed sha and a rebase made it false (`PE-1347`); tamheed cannot
  see remotes, so the README says: bind a sha that is on origin.

## What changed

- The note's obligations row + `agent-control.template.md` (identity-tested): names the four
  draftable kinds; "a script is a `local-tool` row that CANNOT be a draft"; the two-clause rule.
- SKILL.md, `prompts/README.md` (key `4.12.0`), governance, catalog, SECURITY.md, the architecture
  diagram: the two-clause rule - *writes nothing tool-owned; if it reads the STORE, it reads
  `exports/` only*; no draft stage; the kinds; quote the envelope and rows; `resolved_in` and
  `upstream_ref` are bookkeeping.
- `handoff_emit`'s unexported warning: "QUOTE its envelope and rows in your findings (exports are
  point-in-time and may be untracked in your git)".
- `work_bind`'s README row: bind a sha that is on origin.
- NOT edited: `005_feedback.sql`'s header (a shipped migration is frozen); the CHANGELOG says it
  overstates the draft stage.

## Done criteria

- [x] identity test green; no old wording outside the frozen header
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green
