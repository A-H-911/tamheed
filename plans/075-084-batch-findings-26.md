# Plans 075–084: the findings_26 batch → v4.10.0 (master record)

> The approved batch plan, verbatim, after a devil's-advocate review. Each numbered plan gets
> its own record before its code is written; this file is the map and the resume point.

Status: **EXECUTED 2026-09-21 — released as v4.10.0** (approved by the maintainer the same
day; per-plan status lives in the index rows). Produced from a full read of ACMP's
`findings_26.md`, read-only source inspection at `v4.9.0`, three read-only measurement scripts
(writing only to temp directories), and two advisor passes. Both repos are untouched.

Interview rulings (2026-09-21): one batch including the three held plans, shipping as v4.10.0;
every query-built rule reads `indeterminate` over zero rows, **except** that a recorded omission
for the family is a deliberate zero and reads `pass`; retiring a binding lesson requires the
operator's confirmation.

---

## 1. Weaknesses of the original plan

1. **Plan 075 fixed the wrong thing, and only half of it.** I assumed ACMP completed a
   supersession and the note ignored it. A scratch test shows the sanctioned exit works today:
   flipping the old lesson to `Superseded` drops it from the note AND from
   `entity_query("lesson", status="Approved")`. ACMP set only the `superseded_by` pointer. My
   fix filtered the note alone, leaving the second binding surface — the query
   `orient-resume.md` tells every session to run — still returning the false lesson, and it
   created two representations of one fact.
2. **A security hole I had not noticed.** Binding a lesson needs the operator's confirmation;
   retiring one needs nothing. An agent can unbind any approved lesson unattended.
3. **Plan 078's mechanism fails on the case that motivated it.** ACMP's hand-merged
   `integrity-check.md` is not a line-superset of stock (38 of 68 stock lines absent). The
   containment heuristic would still call it unmerged.
4. **Plan 077's size was understated.** "Many small packages" is, measured, 17 of 21 rules on a
   fresh package and 7 on one fixture, with a permanent amber wherever a family is legitimately
   empty — the very trap I cited against plan 070.
5. **Plan 076's width rule could hide a real slip** (`DEF-82` typed for `DEF-082`) and removes
   nothing on today's corpus, so its benefit was asserted, not measured.
6. **Plan 080's `if_match` was speculative.** The store has a single-writer lock, so a stale
   read across writers cannot happen. The field's actual pain was silent content loss on a
   re-sent field, which `if_match` does not address.
7. **My own plan-068 hint misfires.** On the half-finished state it says the lesson "BINDS only
   once the note is rebuilt", when the truth is that it was never retired.
8. **A live doc is slightly wrong**: the server README (plan 072) calls `search` an "exact
   substring"; ACMP established from the pragmas that it is case-insensitive for ASCII.
9. **The truncation claim was unverified.** I promised a marker "before the truncated body"
   without having found the truncation. It is at 180 characters; the marker belongs in the tag.

## 2. Assumptions — confirmed, rejected, unresolved

**Confirmed by direct test or inspection**
- `Approved → Superseded` with byte-identical content passes `trg_lessons_immutable` and every
  approval guard, needs no operator word today, and removes the lesson from both the note and
  the `status="Approved"` query. The half-state (pointer set, status `Approved`) is accepted
  silently; the server reads `superseded_by` nowhere.
- No doc says to set the status: `skill-promote.md:54` and `register-liveness.md:83` name only
  the pointer.
- The note truncates a lesson at 180 characters and renders the tag before the body.
- `_strip_code` runs before the prose-id match; omissions are unscanned (no `id` column);
  prompt classification is byte-equality; eval assertions pin `ready` and gates only.
- ACMP's exports hold two tokens that appear only inside code spans (`ADR-2026`, `DEC-208`):
  the separate list would be small, not noisy.
- Vacuous passes today: fresh package 17 of 21; lab fixture 2; `minimal-brief` 7;
  `execution-loop` 2. None is a blocking failure, so `ready` does not move.
- `slice-review.md` and `orient-resume.md` in ACMP are line-supersets of stock;
  `integrity-check.md` is not.

**Rejected**
- "findings_26 §3 is a rendering defect"; the line-superset merge heuristic; "the width rule is
  free"; "`if_match` answers the field's pain"; findings_26's "the prose-id rule scans omission
  rows".

**Unresolved — each has a measurement step in §5**
- Which of the 18 test assertions on a `pass` status flip under plan 077 (run, then list).
- Whether a merge marker written as an HTML comment passes `_INJECT_RE` and the stale scan.
- Whether any lesson flow in the lab scenario retires a lesson unattended (plan 075's new guard).

## 3. Risks and mitigations

| Risk | Mitigation |
|---|---|
| The engine retires a lesson the operator did not mean to retire | Automatic retirement happens only inside the write where the OPERATOR approves the successor, only for rows whose `superseded_by` names that successor, journaled as a `transition` row and named in the result |
| The new guard breaks a field flow | It refuses with the exact remedy (`operator_confirm`), as the approval guard does; called out in the CHANGELOG as a contract tightening; the lab scenario is checked for unattended retirements first |
| 077 makes every small package look amber | A recorded omission reads `pass` and names it; `indeterminate` never blocks; the flipped tests are listed by running the suite, not chosen in advance |
| The width rule hides a real slip | Narrow tokens are not dropped: they go to an informational `not_well_formed` list |
| `in_code_spans` noise (`ADR-2026` from `ADR-2026-001`) | A token immediately followed by `-<digit>` is not an id; the cost, stated: a range written `PE-1300-1310` is not scanned |
| The merge marker is an unverifiable claim | It is reported as DECLARED (`stock_merged: "declared 4.9.0"`), never as verified; containment is reported separately where it holds |
| Destructive or binding-surface code reviewed by its author only | Security + Python reviewers on 075 and 080 before commit, plus the advisor |
| Ten plans at a saturated context | Every plan record is written before its code; index rows carry status; memory updated at each milestone; patches and commit messages go through files |

## 4. Changes made and why

1. **075 redesigned: status stays the single truth, and the engine finishes the job.** Reason:
   §1.1, §1.2, §1.7. When the operator approves a lesson, every `Approved` lesson pointing at it
   becomes `Superseded` in the same transaction. Retiring a binding lesson by hand needs
   `operator_confirm`. The half-state gets a truthful hint and an advisory.
2. **078 becomes a declared marker plus reported containment.** Reason: §1.3.
3. **077 gains the omission rule and its measured blast radius.** Reason: §1.4 and your ruling.
4. **076 reports instead of dropping, and excludes the `-<digit>` suffix.** Reason: §1.5.
5. **080 shrinks to what the field needed**: `changed_columns` with before/after lengths. No
   `if_match`, no row hashes. Reason: §1.6.
6. **082 also corrects "exact substring".** Reason: §1.8.
7. **Order changed** to 075 → 077 → 076 → 079 → 080 → 081 → 078 → 082, so the new advisories are
   born with the final zero-row semantics.
8. **No web research was run, deliberately.** After `if_match` was dropped every open question
   was internal to this repository and was settled by a direct test. Nothing in this plan rests
   on outside practice.

## 5. Refined execution plan

Constraints: stdlib only, **no schema migration and no new event type**, additive top-level
result keys (never per-row), bundle never links out, CHANGELOG under `[Unreleased]`, no version
bump until 084, stock prompt edits carry a `4.10.0` history key in the same commit. Per-plan
loop: plan record → RED test → GREEN → `python check.py` → reviewers where listed → advisor →
commit from a message file → push → CI 9/9. Status updates at least every three minutes.

| # | Plan | Validation → expected output |
|---|---|---|
| 075 | **Supersession completes itself, and retiring needs the operator.** (a) Approving a lesson retires every `Approved` lesson whose `superseded_by` names it: same transaction, one `transition` journal row each (actor `system:lesson-supersession`), listed in the result. (b) Moving an `Approved`/`Promoted` lesson to `Superseded`/`Obsolete`/`Rejected` by hand requires `operator_confirm`. (c) The half-state hint becomes truthful, and the note tags such a row `[…, superseded by LL-NNN - pending]` ahead of the 180-character body. (d) Advisory `lessons-superseded-binding` names any half-state row. (e) `skill-promote.md` and `register-liveness.md` say the status must change. Security + Python reviewers | Approve the successor → old row `Superseded`, absent from the note and from the `Approved` query, journal row present; unattended retire refused naming `operator_confirm`; pending successor → both render, tag visible after truncation; pointer at a Rejected or missing row retires nothing |
| 077 | **No rule passes over nothing.** Zero population and no entities → `indeterminate`, `discriminating: false`, at every scope; a recorded omission for the family → `pass`, naming it. Replaces the plan-069 one-off flag | Run the suite, list every flipped assertion in the record; `ready` identical before and after on all three fixtures; an omitted family reads `pass` with the omission named |
| 076 | **Prose-id refinements.** Bare hits fail the rule as today. `in_code_spans` and `not_well_formed` (numeric width below the family's minimum) are informational lists. A token followed by `-<digit>` is skipped. The note says the entity list is a floor | Backticked phantom listed, rule passes; `SEC-8` against a three-digit family listed as not well-formed; `ADR-2026-001` in neither list; lab fixture still clean |
| 079 | **Open-ended blanket waivers named**: advisory `waivers-open-ended` (whole-rule, no expiry). Playbook step, test tuple, history key | The lab's `WVR-002` is named; an expiry clears it; zero waivers with no omission reads `indeterminate` |
| 080 | **A write says what it changed.** Per-item `changed_columns`, each with `old_len` / `new_len` for text. Python reviewer | A status flip reports one column; a re-sent long field that lost a paragraph shows the length drop; an unchanged write reports `[]` |
| 081 | **A stale review page is detectable.** `export_html` stamps the package digest into `review.html`; `package_verify` reports `review_current` (null when unstamped) | True after export, false after any write, null on a 4.9.0 page; two exports of one state byte-identical |
| 078 | **A completed hand-merge is visible.** A `<!-- tamheed:stock-merged X.Y.Z -->` line in a customised prompt is reported as `stock_merged: "declared X.Y.Z"` and silences the lag warning when it equals `stock_last_changed`; line-containment is reported as `contains_current_stock`. Verify the marker passes the injection and stale scans first | Marker at the current release → no warning; older marker → warning names both versions; ACMP-shaped `integrity-check.md` handled by the marker, `slice-review.md` by containment |
| 082 | **Docs and diagrams sweep** after the code: server README rows (incl. `search` is case-insensitive for ASCII), governance and quality-gates (lesson retirement, zero-row semantics, the floor), handoff.md, SECURITY (the new operator-only transition), and `docs/entities.md`'s lesson lifecycle diagram gains the automatic supersession edge. One `[Unreleased]` line corrects 4.9.0's "exact" | Per-behavior grep: every new behavior documented outside `plans/`; no stale sentence survives |
| — | **Acceptance pass**: the black-box script, one section per plan, passing on the batch tree and failing on an extracted `v4.9.0` tree with each check starting from an open package, so every failure is its own | N/N vs 0/N; suites under warnings-as-errors; self-test |
| 083 | **Lab beat 17**, agent-driven in-process, reviewed by rerunning its done criteria: approve a successor and watch the old lesson retire; an unattended retire refused; a vacuous rule `indeterminate` and an omitted one `pass`; a backticked phantom under `in_code_spans`; `WVR-002` named; a shortened re-send visible in `changed_columns`; `review_current` false then true | New `evals.json` assertions; evidence report under `plans/evidence/` |
| 084 | **Release v4.10.0** (plan-058 recipe) | Lints 4, 5, 8, 9 green; tag; CI green on the tagged commit; memory updated |

**Recorded, not built:** `if_match` and row hashes (no concurrent writer exists to be stale
against); `server_info().package` with no package open; omission rows readable or scanned; a
per-row opt-out for the prose-id rule (the code-span list makes it unnecessary).

**Relay to ACMP now, not at the next release:** they can stop the false lesson binding today
with one upsert — `LL-094`, full row, content byte-identical, `lifecycle_status: "Superseded"`,
`superseded_by: "LL-097"` — then `handoff_emit`. Also: the prose-id rule does not scan omission
rows; `package_unlock` staying unexercised and their procedure staying "annotated, not retired"
is right.

## 6. Approval checkpoint

Nothing has been executed. Approving authorizes plans 075–084 as written, with commits, pushes
and the `v4.10.0` tag on `main` under the standing git delegation. These are the points that
change tamheed's behavior or doctrine, and that you are explicitly agreeing to:

1. **The engine changes a second row's status on an approval.** Approving a lesson retires the
   lessons that point at it, in the same write, journaled. Precedent: the requirement
   auto-advance trigger.
2. **A contract tightening.** Retiring a binding lesson by hand is refused without
   `operator_confirm`. An agent that does this unattended today will be refused.
3. **Readiness wording changes on every package.** Measured: 17 of 21 rules on a fresh package
   move from `pass` to `indeterminate`; a recorded omission restores `pass`. `ready` never moves.
4. **Two new advisories on every package** (`lessons-superseded-binding`, `waivers-open-ended`);
   the lab's `WVR-002` will be named.
5. **`review.html` changes bytes once** on every package that tracks it, for the digest stamp.
6. **Stock prompts change again** (`skill-promote.md`, `register-liveness.md`, and any that
   teach the new rules), so ACMP's customised copies lag again.
7. **MINOR release v4.10.0** with lab beat 17.

Separately, and needing no release: I can write ACMP a short note now with the one-upsert
workaround for the false lesson, if you want it before 4.10.0 ships.

Approve as written, or tell me which of the seven to change.
