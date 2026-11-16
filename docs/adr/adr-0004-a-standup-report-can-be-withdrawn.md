---
status: Approved
date: 2026-11-16
id: ADR-0004
supersedes: ADR-0003 (partially — the clause that a recorded report never leaves the store)
superseded_by: none
---

# ADR-0004 — A standup report can be withdrawn

## Status

Approved (operator, 2026-11-16 — rulings R133, R134, R136, R139, R140, R142 and R144 in
`plans/evidence/field-round-6.7.0-record.md`; plan 246, release 6.7.0).

## Context

ADR-0003 made standup reports stored records. A trigger refused the removal of a recorded
report. The operator asked to delete a report and to regenerate one. The established pattern for
recorded events (Azure's Event Sourcing guidance, Fowler) never deletes an event: a compensating
record undoes it, and the original stays. A `Withdrawn` status would follow that pattern. But
6.6.0 loads every row under its own status CHECK, so it would refuse the whole store, and the way
back would break.

## Decision

- The newest place in the chain can be withdrawn whole (R144): the newest daily report
  together with every report it corrects, or an override report. A report that another
  report names stays. Withdrawn newest first down to none, the chain starts again with a
  first report.
- The tool checks every row that names the report, and it refuses while one is left. Migration
  012 replaces the trigger `trg_standup_reports_keep` under the same name, so a raw delete
  follows the same rule.
- The row leaves the store, and its page is removed. A journal note names the report, who and
  when. The operator's words are not stored (SR49): the row that held them is gone. Git history
  keeps the removed row, so a withdrawal is not erasure.
- A withdrawn id is never used again. The allocator also counts the ids that the journal notes
  name.
- Regenerate rebuilds the pages of recorded reports from their rows. No row changes.
- Neither a regenerate nor a correction changes the frozen facts. Fresh lists come only from
  withdrawing the newest daily report and drafting again, because the store keeps current state
  only (R142).
- A recorded report is still never edited: `trg_standup_reports_immutable` holds.

## Consequences

- Measured on 2026-11-16 (`plans/evidence/scripts-239/wayback_246.py`): after a withdrawal under
  6.7.0, the real 6.6.0 opens the store and verifies it clean. Its next draft takes the withdrawn
  id again, so the field briefs name that.
- The journal note is the compensating record. The store holds no row of the withdrawn report.

## Alternatives rejected

- **A `Withdrawn` status kept in the row:** 6.6.0 refuses the whole store on load.
- **Withdrawing any report:** later reports name it as their base, and the replay runs through it.
- **Keeping the operator's words in the note:** SR49 keeps words out of the journal.

## Confirmation

The four withdraw and regenerate tests of `StandupToolTest` in `tests/test_mcp_contract.py`, the
re-aimed trigger test of `StandupFamilyTest`, and the way-back measurement above.
