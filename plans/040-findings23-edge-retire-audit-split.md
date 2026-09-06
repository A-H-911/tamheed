# Plan 040 (B36): findings_23 — the edge retire, the honest audit split, the relocate wording — v4.6.0

## Status

**DONE (2026-09-06)** — `python check.py` fully green, `--selftest` green (17 tools).
Version stamped **v4.6.0** (MINOR — a new write operation on `entity_upsert`; no schema
migration). *Release only on the maintainer's explicit words.*

## What this was

findings_23 (evidence **C44**) came out of USING 4.5.0 for the close-out: every
findings_22 section verified closed by observation ("four for four"), and three things
found by doing the work — the `amends` relation had arrived with no way to remove the
`relates_to` it was meant to replace (the composite PK puts the new edge BESIDE the old
one; zero `DELETE FROM trace_edges` anywhere) while the G-REL note, the adopt note, and
the maintainer's own 4.5.0 upgrade note all told callers to "delete + re-add"; the C7
counter ran over every verdict row ever written, so its twelve "narrated" ids were
untouched Pending placeholders the package had long since graded; and the relocate
approval string named the backup copy without saying its durability was unverified.

Verified at source and on ACMP data before planning. One premise corrected: tamheed
generates no `.gitignore` — ACMP's ignore rule and its comment are ACMP's own, and the
server never calls git. One promise corrected by the DA round: the plan's first draft
said ACMP would read `ungraded: 12`; measured under the engine's exact new predicate
(active ACs, latest by numeric id) ACMP reads `evidenced 142 / narrated 0 / ungraded 0`.

Maintainer-locked over the interview and two DA forks: `retire: true` on the trace-edge
item as a HARD delete (the `retired_in` tombstone offered and declined — a migration plus
a filter in every edge consumer, PK collision on re-add), NO operator gate (the journal
row, the per-item report, and the gates' re-evaluation are the controls; doctrine: a
WRONG edge only, never to make a gate pass); the three-bucket split over each active
AC's latest verdict; honest wording without a git call; **v4.6.0**.

## What shipped

1. **Edge retire** — `{"type": "trace-edge", "from_id", "to_id", "relation", "retire":
   true}`, exactly those keys: the triple deleted, the relation rule bypassed (a
   mistyped edge is what gets retired), a server-appended `correction` row (actor
   `system:edge-retire`, entry `EDGE RETIRED: <from> -<relation>-> <to> …`) in the same
   transaction, an absent triple an error, the batch all-or-nothing, `applied` counting
   it. The `correction` kind is a stated stretch (it corrects the trace record, not a
   journal entry, `corrects: null`) — verified safe: review.html folds only rows with a
   non-null `corrects`, nothing in the server keys on the kind.
2. **G-REL and adopt notes** name the real operation: retype in ONE batch.
3. **`audit_evidence`** = `{evidenced, narrated, ungraded, narrated_ids, ungraded_ids,
   note}` over each ACTIVE AC's LATEST verdict (the `acs-met` population; the
   `v_latest_verdicts` subselect inlined because the view carries no id). review.html
   prints all three and labels a Pending latest verdict `ungraded`; `pkg_check gates`
   prints the split.
4. **Relocate action text** (both migrate paths): what was verified (the byte-identical
   copy) and what was not (that directory's durability; check `git log -- data/<file>`).
5. **Docstring first** (findings_22's lesson): `entity_upsert` teaches `retire` with the
   retype-in-one-batch idiom.
6. **Teaching sweep**: governance / traceability / quality-gates / artifact-catalog /
   workflow / prompt-templates references; the governance template (lint-11 needle
   `retire`); the note span's cheat-sheet line; SECURITY.md (nothing leaves the store
   silently); both READMEs; SKILL.md; docs/entities + methodology ("no entity row is
   ever deleted" now states the one exception); CHANGELOG; four stock prompts
   (integrity-check: the three buckets by id, the retype remedy as a recommendation,
   LL-053's control-from-outside line; progress-sync; register-liveness; the prompts
   README's retire rule + remedy-must-exist rule) with roster appends.
7. **Doctrine** (plans/README): a remedy named by a gate note, an advisory, a refusal
   text, or a release note must be an operation the server exposes; the lab beat
   performs every named remedy end to end.
8. **Tests**: the retire battery (exact triple, journal row, absent-triple refusal with
   rollback, extra-key and wrong-type refusals, a raw-inserted mistyped edge retired
   despite the rule and the gate going red→green in one batch, falsy `retire` ignored);
   the three-bucket split (superseded narrated history not counted, a Pending latest =
   ungraded, a retired AC excluded, then the C7 case proper); the relocate strings; the
   findings_19 §3 culprit text pinned for a trace-edge item (`to_id='FR-999'
   (references entity_index.id)`) — the field had carried that verification
   unverified for four releases; the note needle.
9. **Evals**: three lab-tracker assertions (the `EDGE RETIRED` row present; no
   `relates_to` residue beside the `amends` edge — a `grep-absent` whose needle format
   was verified against the canonical `trace_edges.jsonl` line shape, since an absent
   needle passes vacuously (LL-013); the beat's before/after `trace_query` is the real
   proof; `narrated:0/ungraded:1`).

## The lessons register, read again

Unchanged since plan 039 (62 rows; `LL-062` Proposed→Approved). `LL-025` measured on
ACMP: 16 live→Superseded edges, every one a Merged scope change's delta to a superseded
AC — history, zero live hits, and the lesson itself says nothing mechanical sees it →
no advisory (the hollow-pass class). `LL-053` → one line in integrity-check. `LL-062`
(a calibration proves the one check it calibrates) is already how `package_verify`'s
battery is built — one injected fault per reported field.

## Verification

check.py green end-to-end (see the lab section for the beat-13 fixture); `--selftest`
lists 17 tools; the ACMP shape re-proven in-test (an `amends` + `relates_to` pair
reduced to one edge in one batch; a Pending placeholder counted `ungraded`, zero
`narrated`; a superseded narrated Met invisible).

## The lab's beat 13 (real agent) — see `plans/evidence/lab-continuation-report-040-2026-09-06.md`

Every ✔ observed, none missed: the migrate refusal verbatim; the residue accepted beside
`amends`; the retire exact (`retired: true`, `PE-016` = the server's `correction` row,
`trace_edges.jsonl` byte-identical to the pre-residue fixture); both refusals verbatim,
the `amends` edge surviving both; the G-REL note naming the operation; the placeholder
counted `ungraded` with nothing narrated; readiness failing only on the deliberately-open
items; six stale-stock prompts refreshed and the cheat-sheet teaching `retire`;
review.html labelling `ungraded`; `gate_run` ready; the digest moving by construction;
22/22 lab assertions and `check.py` green under the agent's own run.

The agent's findings, triaged: (1) the scenario said `evidenced: 2` — WRONG, AC-003's
Not-met carries evidence, 3 is right — the scenario now says 3 (the eval pinned only
`narrated:0/ungraded:1`, so nothing false was mechanically asserted); (2) the beat brief
bound the new export AC to `FR-004` (task history) instead of `FR-007` (CSV export) — the
MAINTAINER's error in the brief, not the agent's; Approved ACs are immutable, so the fix
went through the store's own mechanism: `AC-005` supersedes `AC-004` bound to `FR-007`
and carries the placeholder (`AV-005`), `AC-004` retired, the journal row `PE-018` names
why (actor `maintainer:plan-040-fixture-fix`); the scenario records the fixture note;
(3) an AC born Approved on an already-Implemented slice met no guard — reported, not
changed: a closed slice legitimately gains ACs through a scope change, and a guard here
would need the SC- linkage first (recorded under plans/README future options as a
question, not a defect); (4) the refusals are two-layered (batch line + per-item text) —
the existing batch contract, kept.

## Left open

Tamper-evidence proper (unchanged, future options). ACMP-side: upgrade → `SC-050`'s two
owed deletions become two retire items — `(SC-046, DEC-128, relates_to)` and `(SC-049,
DEC-135, relates_to)` — and `SC-050` → Merged only after `trace_query` on both SCs shows
one edge each; `audit_evidence` reads 142 / 0 / 0 (the twelve placeholders are history —
`entity_query("audit-verdict", search="Pending")` lists them); the findings_19 §3
verification can be done safely (a trace-edge to a nonexistent id is refused naming
the column and value, nothing written); `integrity-check.md` changed again (their one
real hand-merge); `AGENTS.md`/`PE-367`/`PE-370` staleness is theirs, as they said.
