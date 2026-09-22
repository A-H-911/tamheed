# Tamheed v4.11.0 — findings_27, the ACMP guidance rewrite, and the operator-confirmed feedback family

Status: **APPROVED by the maintainer 2026-09-22; executing** (per-plan status lives in the index rows). Revision 2, after the devil's-advocate review and two
mid-review notes from the maintainer.** Read-only work only: `findings_27.md` read in full; its four code
claims verified against `tamheed_server.py` at `v4.10.0`; ACMP's memory/prompts/handoff files audited
(one Explore agent; nine of its cited passages re-read verbatim by me; two of its "stale" verdicts
re-tested against source, one was wrong); ACMP's scripts and `.scratch/` inventoried by me from source;
the tamheed new-family pattern mapped by me from the 4.4.0 footprint, `store.py` and `check.py`. Two
advisor passes. No web research, deliberately: every open question was internal and settled by source.
Neither repo is modified.

Interview rulings (2026-09-22): **rewrite the ten heaviest ACMP files**; a **`feedback` table, `FB-`
prefix, migration 005**; collection by **`entity_export` plus a `handoff_emit` warning**, no new tool;
**`exports/` is the sanctioned seam** for local tooling. Mid-review notes: **the operator confirms every
feedback row and every local tool's creation and use**; at migration **ACMP deletes each existing tool or
registers it as feedback if it obeys the usage policy, and updates every `.md` that references it**; the
docs/diagrams sweep runs after the checks, followed by the full test pass.

Deliverable boundary: changes land in **tamheed only**. ACMP is instructed by a brief printed in the
transcript after the tag; nothing in ACMP is edited from here.

---

## 1. Weaknesses of the original plan (revision 1), found by re-reading source

1. **Plan 086 rested on a false premise.** It said the by-hand retirement would be journaled "under the
   caller's actor". `entity_upsert` carries no actor. The precedent is the approval audit row at
   `tamheed_server.py:1389`: an ENGINE row, actor `system:lesson-guard`, naming `confirmed_by`.
2. **One audit row would have made ACMP "correct" a true sentence.** The audit called ACMP's "all seven
   gates" stale; `GATE_NAMES` has eight keys, but ACMP has recorded `gate_run() 7/7` on three releases and
   nothing in their files names which key is absent. Unsettled from here; demoted to a measurement.
3. **The feedback family had no operator gate.** As drafted, an agent could file, and by implication
   justify, any tool on its own word. That inverts the doctrine the lessons family established.
4. **"Ten heaviest files" was undefined.** The audit's hit-count top ten includes two dated project
   records that contradict nothing.
5. **The brief said nothing about the tools ACMP already has**, only about future ones.
6. **The docs/diagrams sweep and "full test" had no stated validation** beyond a grep.
7. Carried from revision 1: my 4.9.0→4.10.0 brief overstated plan 077; the unjournaled retirement was
   parked as "not in any plan"; `references/state.md:26` is looser than what SKILL.md will teach; FB rows
   quote broken ids and would trip `prose-ids-resolve` unless exempt.

## 2. Assumptions — confirmed, rejected, unresolved

**Confirmed by source or measurement**
- findings_27 §2: lookbehind and lookahead both lack `_` (`:324-325`); width is tested before code span
  (`:385-390`). §3: the "showing N of M" clause reads `len(dangling)` only (`:2015-2018`). §4: measured
  on 4.10.0, a by-hand `Superseded` write with `operator_confirm` journals nothing. §1: correct.
- The bundle ACMP ran (`0354156`) is byte-identical to the `v4.10.0` tag.
- `check.py`'s registry↔DDL lint derives tables from `store.connect()`, which applies migrations, so a
  table that exists only in `005_feedback.sql` passes; `schema.sql` stays the byte-twin of `001`.
  `export_html` iterates `ENTITY_TABLES` (`export_html.py:91,541`): the "registers" section renders a
  new table without a new SECTIONS entry. `_PROSE_ID_EXEMPT_TABLES` (`:312`) is where the journal is
  exempted. `transition` is a caller-writable event type (`schema.sql:484`). No `FB-` prefix exists. No
  code, test or doc pins the family count 37. `tests/test_store_migrations.py` is the migration test
  precedent (touched in the 4.4.0 footprint).
- Migrations apply at `connect()` before the JSONL load; the load skips a missing file (`store.py:327`);
  `package_open` refuses only pre-v4; `entity_upsert` resolves types from `ENTITY_TABLES` in code. A
  4.10.0 package opens on 4.11.0 and accepts `FB-` rows at once; `package_migrate` reports
  `registry-sync` (pure append, no backup — `:3144,3315`) for the stored `entity_types.jsonl`. All three
  additive-table migrations (4.3.0, 4.4.0, 4.5.0) shipped MINOR.
- The package header `go_no_go` is readable (`_PACKAGE_ROW`, `:3598`) and writable by no tool — ACMP's
  memory is right, and it is a feedback item.
- ACMP's four generators and every `.scratch` probe read `exports/*.json` only; `count-prompt-ids.py`
  is the sole `data/*.jsonl` reader (`:49`), already flagged non-compliant by ACMP.
- Audit spot-check: nine passages exact at their lines.

**Rejected**
- "The by-hand retirement can carry the caller's actor." "ACMP's seven-gate sentence is stale."
  "ACMP's utilities bypass the tools" (one does). "A backup-taking staged migrate is needed."

**Unresolved — settled in execution, never by guessing**
- Which gate key ACMP's `gate_run` lacks (the brief asks for the list).
- Whether an FB row's free text needs escaping beyond what `export_html` already does for every other
  free-text family (checked when the table renders; FB text is never emitted into prompts or the note).

## 3. Risks and mitigations

| Risk | Mitigation |
|---|---|
| An agent files feedback or registers a tool on its own word | A row is born `Proposed`; `Confirmed` needs `"operator_confirm": true` (the lessons guard, same refusal text shape); `kind: local-tool` rows are refused at INSERT without `operator_confirm` — a tool exists only on the operator's word |
| "Usage" of a tool cannot be seen by tamheed | Stated limit. Enforced by doctrine: SKILL.md, the note's standing line, the two prompts, and the ACMP rewrite; `handoff_emit` names unconfirmed rows every emission |
| The brief makes ACMP delete a correct sentence | Every row carries the 4.11.0 doc path it is corrected against; a "must survive" list (DEC-135 d1, operator-only rules, trap 27, `package_unlock` first); the gate-count row is a measurement, not a correction |
| Deleting a tool breaks an ACMP workflow (LL-011 slates) | The brief's rule is delete OR register; the four generators are compliant and register; only `count-prompt-ids.py` is deleted, replaced by `prose-ids-resolve` |
| The engine journal row for a by-hand retirement is mistaken for the automatic path | Distinct entry text ("on the operator's word — by hand") and actor `system:lesson-guard` vs `system:lesson-supersession` |
| `_` fix hides a real slip | A slip like `DEF-82` has no `_`; measured on the lab fixture and ACMP's exports before commit |
| A new Always family fails G-SET everywhere | `feedback` is `Continuous` |
| FB rows trip `prose-ids-resolve` (they quote `SEC-8`, `DEC-208`) | `feedback` added to `_PROSE_ID_EXEMPT_TABLES` |
| The lab fixture's guide orphans again at release | Plan 084's F-1 step is in the recipe |
| Sub-agent output trusted unverified | Four Explore runs died on 529; two explorations done by hand from source; the surviving audit verified by re-reading nine passages and re-testing two verdicts (one failed) |

## 4. Changes made and why

1. **086 rewritten**: the row is an engine row (`transition`, actor `system:lesson-guard`, naming
   `confirmed_by` when sent). Reason: §1.1.
2. **087 gains the operator gate**: `Proposed → Confirmed` on `operator_confirm`; `kind: local-tool`
   refused at insert without it. Reason: your note; the lessons precedent.
3. **The brief gains a tool-migration step**: inventory → delete or register (operator-confirmed) →
   update every referencing `.md`. Reason: your note.
4. **The ten files are named** (§5, brief step 2). The gate-count row is a measurement.
5. **088 and the acceptance step carry explicit validation** (per-behavior grep; the four-part full test).
6. Carried: findings_27 fixes first so the family's text is born correct; `state.md` tightens; no web
   research.

## 5. Refined execution plan

Constraints: stdlib only; one additive migration (`005_feedback.sql`); no new tool (`len(TOOLS)` stays
19); bundle never links out; CHANGELOG under `[Unreleased]` until 090; stock prompt edits carry a
`4.11.0` history key in the same commit; FB text is never rendered into the note or emitted prompts.
Per plan: record → RED test → GREEN → `python check.py` → reviewers where listed → commit from a
message file → push → CI. Status updates at least every three minutes.

| # | Plan | Validation → expected |
|---|---|---|
| 085 | **findings_27 §1–§3.** `_` added to the id pattern's lookbehind AND lookahead; the rule note states the classification order (width first, then code span); the "showing N of M" clause covers all three lists; the `indeterminate` note names `scoped` as the discriminator | `KPI-17_score` inside a code span lands in no list; `SEC-8` still `not_well_formed`; `DEF-82` still reported; a 51-entry informational list says "50 of 51"; lab fixture assertions unchanged |
| 086 | **findings_27 §4.** In the lesson block, when an Approved/Promoted row moves off a binding status WITH `operator_confirm`, the engine inserts one `transition` row, actor `system:lesson-guard`, entry `LESSON <id> -> <status> on the operator's word — by hand (operator_confirm attested; confirmed_by <x>)`, inside the item's savepoint. Security reviewer | Exactly one row per retirement; a refused write journals nothing; the automatic path's row unchanged; the two rows are distinguishable by actor and text |
| 087 | **The `feedback` family** (`FB-`, `005_feedback.sql`, `Continuous`). Columns: `id`, `kind` CHECK (`missing-capability`, `defect`, `doc-error`, `question`, `local-tool`), `title`, `detail`, `workaround` (what was built instead — nullable), `tool_path` (required when `kind=local-tool`, CHECK), `tool_or_rule`, `plugin_version`, `lifecycle_status` CHECK (`Proposed`, `Confirmed`, `Reported`, `Resolved`, `Rejected`), `confirmed_by`, `confirmed_at`, `resolved_in`, `upstream_ref`, `recorded_at`, `custom_attributes`, `last_referenced`; `entity_index` triggers as `003_skills.sql`. **Guards** in `entity_upsert`: `Proposed → Confirmed` refused without `operator_confirm` (sets `confirmed_by/at`, journals a `transition` row by `system:feedback-guard`); a `local-tool` row refused at INSERT without `operator_confirm`; a move off `Confirmed`/`Reported` to `Rejected` needs it too. Registered in `ENTITY_TABLES`, `BASELINE_ENTITY_TYPES`, `_PROSE_ID_EXEMPT_TABLES`, the catalog, governance id table, `docs/entities.md`, `tests/test_store_migrations.py`. `handoff_emit` warns: `N feedback row(s) await the operator (Proposed: FB-…); M confirmed and unexported — entity_export("feedback")`. The note gains one standing line: *a function tamheed lacks is an FB- row FIRST, on the operator's word; a local tool exists only as a Confirmed local-tool row; local tooling reads exports/ only, writes nowhere tool-owned*. SKILL.md, `references/state.md:26` (tightened), `prompts/README.md` and `orient-resume.md` teach the same. Python + security reviewers | Migration applies on a copied 4.10.0 store; `package_migrate` reports registry-sync for one row; upsert/query/export round-trip; unconfirmed `Confirmed` and unconfirmed `local-tool` both refused naming `operator_confirm`; the warning names the ids and nothing else; an FB row quoting `DEC-208` trips no rule; G-SET unchanged on all fixtures; `check.py` sync lints green; `len(TOOLS)` 19 |
| 088 | **Docs + diagrams sweep, after the checks**: server README rows (`entity_upsert` guards, `handoff_emit` warning, `readiness_check` wording), quality-gates, governance (FB lifecycle, the operator's word), extension.md (worked example gains 005), `docs/architecture.md` (data-flow diagram: package → `exports/feedback.json` → findings → upstream plan), `docs/entities.md` (FB state diagram with the operator edges), SECURITY.md (what leaves the package, only by export, only Confirmed) | Per-behavior grep: every new name outside `plans/` in ≥2 docs; no stale count or "hand-edit at rest is legal" survives; every mermaid block parses (existing lint) |
| — | **Full test**: (1) `python check.py`; (2) all suites under `PYTHONWARNINGS=error::DeprecationWarning`; (3) black-box acceptance, one section per plan, N/N on the batch tree and 0/N on an extracted `v4.10.0` tree, each check from an open package; (4) `--selftest` 19/19 | N/N vs 0/N; all green |
| 089 | **Lab beat 18** (agent, opus, worktree; plan file first; every new assertion must fail on the pre-beat fixture): file an FB row → see it named as awaiting the operator → confirm it on the plan's word → export `feedback.json`; a `local-tool` row refused unattended, accepted confirmed; retire a lesson by hand and quote the engine row; a `KPI-17_score`-shaped token vanishing from the lists | New `evals.json` assertions; evidence report |
| 090 | **Release v4.11.0** (plan-058 recipe + the F-1 fixture step; `005` named in the lead-in) | Lints green; tag; CI on the tag |
| — | **The ACMP brief**, transcript-only, after the tag: (1) upgrade 4.10.0→4.11.0; `package_migrate` preview → confirm (registry-sync, no backup); (2) **rewrite the ten files**: `.claude/memory/tamheed-package-mechanics.md`, `tamheed-v4-and-liveness.md`, `tamheed-stale-lock-pid-reuse.md`, `commit-package-writes-before-git-ops.md`, `tamheed-data-repair.md`, `batches-13-21-durable-rules.md`, `verify-mechanically-not-carefully.md`, `read-the-artefact-not-the-entry-about-it.md`, `an-id-is-a-pointer-not-a-reference.md`, `MEMORY.md` (index lines) — each audit row with its correcting 4.11.0 doc path; plus sentence-level fixes in `prm-next.md` (§1394-1411, §2041, §1361, trap 27b), `integrity-check.md` step 8, `project-invariant-audit.md:26,36`, `handoff/RESUME*.md`, `HANDOFF-RUNBOOK.md`; the lock rule worded "`package_unlock` first; hand removal only for what the host cannot see, on the operator's word"; a "must survive" list; the gate-count MEASUREMENT (quote `gate_run()` keys, then fix the sentence if eight); (3) **tool migration, operator-interviewed**: inventory every tool (`scripts/gen-*.mjs`, `scripts/lib/package-export.mjs`, `count-prompt-ids.py`, every `.scratch` probe) → for each, DELETE it, or REGISTER it as a Confirmed `local-tool` FB row if it reads only `exports/` and writes nowhere tool-owned → `count-prompt-ids.py` deleted (JSONL reader) and `prose-ids-resolve` cited instead → update every `.md` that references a deleted or registered tool (`AGENTS.md`, `MEMORY.md:45`, `prm-next.md:64,1396`, `verify-mechanically-not-carefully.md`, `sl034-slate-generator-and-asvs-pack.md`, `project-invariant-audit.md`); (4) backfill four `missing-capability` FB rows, operator-confirmed (unwritable `go_no_go`; id-resolution over prompt FILES; per-field token census with context; a patch/substitute write mode); (5) `findings_28.md` with `exports/feedback.json` attached | ACMP's next findings carries a feedback export and a tool register |

**Recorded, not built:** absorbing slate generation upstream; a `feedback-unreported` readiness
advisory; `FEEDBACK.md` in the target repo; mechanical detection of a tool's use.

## 6. Approval checkpoint

Nothing has been executed. Approving authorizes plans 085–090, commits, pushes and the `v4.11.0` tag on
`main` under the standing git delegation, and the ACMP brief. These change tamheed's doctrine or behavior:

1. **A new entity family and migration `005`** in a MINOR release (precedent 4.3–4.5); field packages
   run one `package_migrate` registry-sync.
2. **Feedback is on the operator's word**: `Proposed` freely, `Confirmed` only with `operator_confirm`;
   a `local-tool` row cannot even be inserted without it. The word "usage" is enforced by doctrine, not
   mechanically — tamheed cannot see a `node` process.
3. **The engine journals a by-hand lesson retirement** as `system:lesson-guard`.
4. **The id pattern treats `_` as a word character.**
5. **Doctrine tightens**: `state.md` stops calling a hand-edit at rest legal; SKILL.md, the note and two
   stock prompts say "FB- row first, on the operator's word; local tooling reads `exports/` only".
6. **Two stock prompt bodies change** (`README.md`, `orient-resume.md`).
7. **ACMP is told to rewrite ten files, delete-or-register every tool it has, and update every file
   that references them.**
8. **MINOR release v4.11.0** with lab beat 18.

Approve as written, or name which of the eight to change.
