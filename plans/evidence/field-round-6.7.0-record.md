# Field round 6.7.0 - the record (Jisr's FB-015, FB-017 to FB-021, and two standup actions)

## Context

Jisr upgraded to 6.6.0 on 2026-11-16 and exported its feedback register: 21 rows, digest
`8e824cb8`. FB-001 to FB-011 were resolved in 6.5.0. Of the new rows FB-012 to FB-021, six ask
for work. ACMP's committed register (`8235a2f9`) holds nothing new. The operator added two
standup actions: withdraw a recorded report, and regenerate a report. The plan is
[239-field-round-6.7.0.md](../239-field-round-6.7.0.md).

## Triage

| Rows | State in the field | Action |
|---|---|---|
| FB-001 to FB-007, FB-009, FB-011 | Resolved in 6.5.0 | none |
| FB-008, FB-010, FB-012, FB-014, FB-016 | Confirmed local-tool registrations | none |
| FB-013 | Rejected by the field's operator | none |
| FB-015 | doc-error | three texts name an edge that the engine refuses for an entry that replaces a section |
| FB-017 | missing capability | `entity_export` cannot run `slate_read` |
| FB-018 | doc-error | the browser check refuses a page of one round, after it clears the page |
| FB-019 | missing capability | a closed set of a register field takes text only |
| FB-020 | question | the standup list of blocked work never reads the blocking row |
| FB-021 | question | the restated scan flags the entry and exit conditions of phase prompts |

## Measured before any change (2026-11-16, scratch copies only)

- The real `_restated_findings` gives the field 27 findings over its 10 Approved prompts: 24
  status claims and 3 id-dense. The kinds are kickoff 1, phase 6, situational 3. ACMP gives 0.
  The pinned stale case "SL-001-SL-019 is COMPLETE" fires. The plan-125 prose example
  "P1-P19 COMPLETE" fires under no rule, because its prefix has one letter.
- The field has 12 `blocked_by` edges, and all 15 of its dependencies are `Approved`, the met
  dependency too. No status means "met". ACMP has no `blocked_by` edge.
- In Python, `1 in [True]` and `{"a": True} == {"a": 1}` are both true.
- The browser check clears every answer before its shape guard, and again in its `finally`.
- The RPT allocator takes the highest id left in the table, so a removed report's id would come
  back. The migration head is applied at open and is written nowhere in a package.

## Rulings (operator, 2026-11-16; R120 was the last)

- **R121** FB-020: the standup list reads the far end of each `blocked_by` edge through one shared
  rule of when a row is settled. A met dependency takes `Implemented`.
- **R122** FB-021: in prompt rows, status claims are scanned in kickoff prompts only. CLAUDE.md,
  AGENTS.md and the package CLAUDE.md keep the full scan. An id-dense paragraph honours a label.
- **R123** FB-019: a closed set holds all text or all booleans, compared by type. A boolean set
  prints as `true / false`. The retire door compares by type too.
- **R124** FB-015: the texts are fixed. `supersedes` stays within one family. The 6.5.x briefs
  stay as history, and the field's brief names the correction.
- **R125** FB-017: `slate_read` joins the tools that `entity_export` runs. The docs say what its
  file holds: the answers files' own times, inputs outside the store, a digest of the store only.
  The agent still reads the transcript back to the operator.
- **R126** FB-018: the check reads the page's shape before it changes anything. A page of one
  round runs the checks it can and names each check it skips.
- **R127** The settled rule also feeds a readiness advisory.
- **R128** The round goes ahead without the field's DEC-172, which the export did not hold. The
  field's brief asks whether it changes anything.
- **R129** The settled table, reusing readiness's own predicates (the plan holds it).
- **R130** The advisory `blocks-lifted` lists open rows whose every blocker is settled: work that
  is free to start. The edge stays as history, and nothing is retired.
- **R131** The release is 6.7.0, a minor, built on `round/6.7.0`.
- **R132** Two field briefs, to the 6.6.0 standard.
- **R133** Withdraw takes the newest daily report or an override report. A correction is refused.
- **R134** A withdrawal needs the operator's confirm and words. A journal note names the report,
  who and when, never the words. A removed id is never used again.
- **R135** The edge cases of the settled table are accepted and written down: a Deferred question
  lifts its block; a discharged risk lifts it whatever its status; a met assumption or plan takes
  `Implemented`.
- **R136** Regenerate rebuilds the pages of recorded reports from their rows. The skill gains a
  step to redo a report by the existing correction.
- **R137** The release stays a minor with migration 012 (triggers only) and ADR-0004.
- **R138** The field's brief asks its operator to write the two retired `blocked_by` edges to the
  met dependency again, as history, and to move that dependency to `Implemented`.
- **R139** A withdrawal removes the row. The docs say it is not erasure: git history keeps it.
- **R140** The action is `withdraw`, and the vocabulary gains its row.
- **R141** (the security review of 243) An export refuses a target inside `slates/`, as it
  refuses `data/`.
- **R142** A correction and a regenerate keep a report's frozen facts. Fresh lists come only
  from withdrawing the newest report and drafting again.
- **R143** (2026-11-17, after the field's fresh export) The field's operator retired the two
  DEP-002 edges by their own ruling. Their brief OFFERS writing the edges again as history and
  moving the dependency to `Implemented`, and asks for a review of every dependency.
- **R144** (2026-11-17) Supersedes R133 in part: a withdrawal takes the newest place in the
  chain whole, the newest report with every report it corrects. An operator can withdraw
  newest first down to none, and the next draft is a first report computed from today.

The approval also covered eight defaults, listed in section 6 of the plan.
