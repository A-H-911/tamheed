# Governance: identifiers, statuses, versioning, cross-references

This is the single source of truth for how every Tamheed entity is named, identified,
versioned, and linked. Apply it uniformly — consistent identifiers are what make traceability
and the handoff trustworthy.

## Identifier scheme

Each identifier is a stable prefix + zero-padded number, unique within a package and never
reused (retire, don't recycle). Every entity lives in its `data/<table>.jsonl` family
(see `artifact-catalog.md`).

| Entity | ID format | Family (table) |
|---|---|---|
| Functional requirement | `FR-NNN` | requirements |
| Non-functional requirement | `NFR-NNN` | requirements |
| Constraint | `CON-NNN` | constraints |
| Invariant (non-negotiable) | `INV-NNN` | invariants |
| Assumption | `ASM-NNN` | assumptions |
| Dependency | `DEP-NNN` | dependencies |
| Open question | `OQ-NNN` | open_questions |
| Decision (any project decision) | `DEC-NNN` | decisions |
| Architecture Decision Record | `ADR-NNNN` (exactly 4 digits) | adrs |
| Risk | `RISK-NNN` | risks |
| Hypothesis | `HYP-NNN` | hypotheses |
| Experiment / POC | `EXP-NNN` / `POC-NNN` | experiments / pocs |
| Success metric / KPI | `KPI-NNN` | kpis |
| Stakeholder | `STK-NNN` | stakeholders |
| Phase | `PH-N` | phases |
| Milestone (roadmap label) | `MS-NNN` | milestones |
| Slice (vertical increment) | `SL-NNN` | slices |
| Work item (WBS) | `WBS-N[.N[.N]]` (group `WBS-N`, leaf `WBS-N.N`) | wbs_items |
| Acceptance criterion | `AC-NNN` | acceptance_criteria |
| Test / validation item | `TEST-NNN` | tests |
| Audit verdict | `AV-NNN` | audit_verdicts (append-only) |
| Progress entry | `PE-NNN` | progress_entries (append-only, typed) |
| Defect | `DEF-NNN` | defects |
| Deferred work | `DW-NNN` | deferred_work |
| Execution gate | `GATE-NNN` | execution_gates |
| Execution plan | `EP-NNN` | execution_plans (per slice) |
| Convention | `CONV-NNN` | conventions |
| Scope change | `SC-NNN` | scope_changes |
| Waiver (v4) | `WVR-NNN` | waivers |
| Narrative document / section | `DOC-NNN` / `SEC-NNN` | narrative_documents / document_sections |
| Diagram | `DIA-NNN` | diagrams |
| Glossary term | `GT-NNN` | glossary_terms |
| Lesson | `LL-NNN` | lessons |
| Skill | `SKL-NNN` | skills |
| Feedback (upstream feedback / local tool) | `FB-NNN` | feedback |

Retired prefixes: `PRM-` (v3 — prompts became files under `<package>/prompts/`; ids of that
shape in a converted package are conversion-audit provenance, not entities).

**`DEC` vs `ADR` — the promotion rule (v4, plan 031).** Use `DEC-` for ANY decision. Promote
to an `ADR-NNNN` when the **one-way-door test** says yes: hard to reverse (a week of
refactoring, not a config flip), broad blast radius (structure, a critical -ility,
dependencies, interfaces, or construction techniques — Nygard's five), or the same question
keeps being re-debated. Record the promotion (`decisions.promoted_to = ADR-0003`) so the link
is never lost. ADRs are immutable after approval and carry `confirmation` — how compliance
will be verified. The `decisions-look-architectural` readiness advisory flags DECs that work
items implement, or that touch invariants/constraints, but were never promoted.

## Lifecycle statuses

Every status-bearing row carries `lifecycle_status` (the column name is uniform in v4 —
the three-axis doctrine below is why it is not just `status`).

```
Draft → Proposed → Approved → Implemented
                 ↘ Rejected
                 ↘ Deferred  (→ back to Proposed later)
        Approved/Implemented → Superseded (by a newer item) → Obsolete
```

- **Draft** — being written; not yet offered for approval.
- **Proposed** — offered to the human. The default for anything Tamheed authored on its own
  initiative.
- **Approved** — the human (or an authorized gate) accepted it. **Only Approved items
  constrain execution.**
- **Rejected** — considered and declined; kept with the reason (rejected alternatives are
  evidence).
- **Deferred** — postponed with a trigger/condition for revisiting.
- **Review** *(v4; wbs-items and slices only)* — **done-CLAIMED**: the agent asserts the work
  is complete but verification has not confirmed it. Counts as OPEN in every readiness
  closed-set; only the guarded transition to Implemented closes work.
- **Implemented** — done-VERIFIED: realized in the execution repo and past the readiness
  rules (phase/slice transitions to Implemented are guarded; `force` requires the operator's
  explicit words and leaves a forced-override audit event).
  A phase or slice cannot be created already Implemented — the rules have nothing to
  measure for a new id; `force` (operator words, self-audited) is the only route.
- **Superseded** — replaced; row points to its successor (`superseded_by`).
- **Obsolete** — retained for history, excluded from active views.

**Decision statuses** are exactly: Proposed, Approved, Rejected, Superseded, Deferred,
Implemented — `Draft` is unrepresentable on a decision row (CHECK-enforced). Never render a
Proposed decision as if Approved — this is a core safeguard.

**Lesson statuses** (v4.3, extended v4.4) are exactly: Proposed, Approved, **Promoted**,
Rejected, Superseded, Obsolete — no Draft (a lesson is born Proposed, awaiting the
operator's interview) and no Deferred (an undecided lesson keeps nagging via the
`lessons-confirmed` advisory; Rejected is the decided-no, kept as evidence). **Only
operator-Approved lessons bind future sessions** (rendered into the CLAUDE.md note, pinned
lessons always), and **landing a lesson in Approved or Promoted — from any state,
including birth — requires the operator's words**, mechanically: `entity_upsert` refuses
without `"operator_confirm": true` (the flag is operator-words-only, the `force`
doctrine), refuses any content drift on the transition (approval/promotion is not an
edit), and requires `confirmed_by` WITH the approval (attribution can never be added
later); the server appends the typed `lesson-confirmed`/`lesson-promoted` journal event
itself. Approved/Promoted lesson CONTENT is immutable — supersede, never edit; `pinned`,
lifecycle transitions, and `superseded_by` stay mutable ON THE OPERATOR'S WORD: STATUS is the
single truth for what binds (the note and the `status="Approved"` query both read it), so a
lesson is retired by its status becoming `Superseded` — `superseded_by` is only a pointer.
The engine does that itself when the operator approves the successor; by hand, any move off a
binding status and any change to the pointer needs `"operator_confirm": true` (v4.10), and the
engine journals that by-hand exit (`transition`, `system:lesson-guard`) as it journals an
approval (v4.11) — the journal covers the lesson lifecycle in both directions.
**Promoted** (v4.4) =
distilled into a skill: Approved → Promoted only, `promoted_to` names the `SKL-` row
(frozen once Promoted), and the lesson leaves the CLAUDE.md note render (full graduation
— the skill file carries the content forward). A Promoted lesson whose skill row is later
retired (Superseded or Obsolete) stays reachable only through a pointer on that row —
`superseded_by` (a successor `SKL-`) or `upstreamed_to` (v5.1: the plugin skill that absorbed
it, e.g. `tamheed:package-writes`); the `lessons-stranded` advisory names the Promoted lessons
behind a retired row that carries neither. Since v5.2 the engine witnesses the move: a skill
row's `lifecycle_status` change, and the arrival of either pointer, is journalled as a
`transition` signed `system:skill-guard` — never on the row's insert (the promotion ceremony
journals `lesson-promoted`), never on an idle re-send. A wrong sentence in a distilled skill FILE is the
operator's hand-edit plus a `correction` journal entry naming the row, never a re-distillation
(that is for a change in the lesson SET) and never a note on the pointer.

**Skill statuses** (v4.4) are exactly: Approved, Superseded, Obsolete — born Approved out
of the operator's promotion interview (the interview IS the approval; a domain lifecycle).
A skill row is METADATA + provenance (name, trigger description, level project|user,
target path); the BODY lives solely in the written `SKILL.md` file, operator-owned after
creation — the server never writes or reads skill files. A re-distilled skill supersedes
its predecessor (`superseded_by`).

**Domain lifecycles** (same column name, domain vocabularies — CHECK-enforced):

| Family | `lifecycle_status` values |
|---|---|
| defect | Open, In-progress, Fixed, Won't-fix, Duplicate |
| deferred-work | Open, Activated, Scheduled, Done, Won't-do |
| scope-change | Proposed, Approved, **Merged** (deltas applied to the plan rows; an `amends` target merges by full-row upsert of a `DEC-` or by SUPERSESSION of an `ADR-`; Merged is set LAST, after every target row is applied and re-read — nothing mechanical checks the assertion it makes) |

**Three-axis status (ADR-0001, revised plan 031).** Lifecycle, verdict, and disposition are
independent columns:

- `lifecycle_status` — the sets above.
- `verdict` — **Met/Partial/Not-met/Pending** for audit verdicts;
  **Validated/Invalidated/Inconclusive/Pending** for experiments/POCs (a hypothesis verdict);
  **Pass/Fail/Pending** for tests. Domain sets are deliberate — a test result and a
  hypothesis outcome are different judgments.
- `disposition` ∈ {superseded, accepted-with-deviation, void} — always with a
  `disposition_reason_ref` to the deciding decision/ADR. A cancelled criterion is *void*,
  not *Not-met*.
- Risks additionally carry `risk_state` ∈ {open, mitigated, materialized, retired, accepted}
  with `discharged_by` naming the AC/test that retires the risk.
- **The risk scale (v4, plan 033):** `probability` = the judged likelihood the risk
  materializes; `impact` = the severity if it does — both on the `high/medium/low`
  enum. The enum IS the scale; there is no numeric tier behind it.

**Audit verdicts carry their evidence chain (v4):** `evidence` (what proves it),
`verified_by` (human/agent/ci), `verification_method` (auto-test/manual/inspection),
`against_commit` (what state it was judged against). A Met without evidence is *narrated*,
not *evidenced* — gate_run counts the split.

## Feedback and local tools — on the operator's word (v4.11)

A function tamheed lacks, a defect in it, a doc error, a question (`kind`: `missing-capability` | `defect` | `doc-error` | `question` | `local-tool`) — or a
script the project keeps over the package — is a `feedback` row (`FB-`), never a side utility.
The agent drafts the first four (`local-tool` cannot be drafted; see below). It drafts it
(`Proposed`: binds nothing, leaves the package nowhere). The OPERATOR confirms it
(`operator_confirm` + `confirmed_by`; the engine journals `system:feedback-guard`), and only a
confirmed row leaves — `entity_export("feedback.json", args={"type": "feedback"})`, its
envelope and rows quoted in the project's findings (exports are point-in-time and may be
untracked), then `Reported`, then `Resolved` with `resolved_in` (`resolved_in` and
`upstream_ref` are bookkeeping: no word needed). A `local-tool` row names its `tool_path`,
needs the word to exist at all — it has NO draft stage; the word is a precondition of the insert
or of a later `kind` change — and is born `Confirmed`. Its rule has two clauses, and the second
applies only to store readers: it writes nothing tool-owned; if it reads the STORE, it reads `exports/` only (a generator of
project-owned files inside the package directory satisfies both). While a row is
Confirmed/Reported/Resolved its content changes only with the word, and leaving that set is
journaled — what the operator vetted is never rewritten underneath their name. The move
WITHIN that set (`Confirmed → Reported`, `Reported → Resolved`) is bookkeeping, needs no word,
and is journaled too (v4.13, the field's FB-014) — the row says which it was. `handoff_emit`
names every row that still awaits the operator or the export, and every reported row until it
is answered; the `feedback-unanswered` advisory lists the same rows (registers excluded — a
local-tool row never resolves).

## The package header — on the operator's word (v4.12)

The header (`server_info().package`) is written with `entity_upsert(type="package")`. `title`,
`mode`, `iteration`, `mvp_definition` and `entry_point` are the agent's bookkeeping; `go_no_go` is
the package's governance verdict: NAME it only when changing it, and only with `operator_confirm`
(v4.13: presence-checked — a header copied back from `server_info().package` is refused
unattended); a real move is journaled by the engine (`system:package-guard`, returned as
`package_audit`), an attested re-send of the same verdict writes no audit row. `name`, `profile`, `package_version` and `created_at` are the
package's identity and are frozen. The header is not an entity family: it has no register, no
CSV and no registry row. **The operator's word, everywhere, is the JSON boolean `true`** — a
truthy string never attests.

## The ambiguity marker (v4)

Never assume. Where prose is ambiguous, write `[NEEDS-CLARIFICATION: OQ-NNN]` in place and
create the OQ (with owner + due_by). G-COMPLETE validates markers: one citing an existing,
unresolved OQ is legal; a marker with no id, a dangling id, or a resolved cite is an
unfinished-marker failure. The `clarifications-open` advisory counts live markers.

## Versioning

- **Package / skill version:** semver `MAJOR.MINOR.PATCH`. MINOR = additive. MAJOR =
  breaking change to the store shape, identifiers, or the handoff contract; ships with an
  explicit migration (`package_migrate` — `package_open` refuses older stores).
- **Document rows:** narrative documents carry `lifecycle_status`; material change bumps it
  back through Proposed.
- **Immutable-after-approval** (ADRs incl. `confirmation`, approved acceptance criteria):
  never edit in place — supersede. Typos yes, meaning no (trigger-enforced).
- **Derived artifacts** (views, review.html, CSVs, the CLAUDE.md note span) are regenerated,
  never hand-edited.

## Cross-reference rules

- Reference any entity by its ID in running text: "mitigated by `RISK-012`", "per `DEC-004`".
- A row that exists because of another records the link as a **typed trace edge**
  (`derives_from`, `implements`, `verifies`, `tests`, `mitigates`, `discharges`,
  `blocked_by`, `satisfies`, `supersedes`, `scope_adds`/`scope_modifies`/`scope_removes`,
  `learned_from` — a lesson names what taught it: defect, decision, risk, slice,
  wbs-item, or progress-entry — `amends` (v4.5): a scope change that carves an
  exception out of a RULING or re-scopes one — scope-change → decision | adr only; a
  ruling is not a plan row, so the scope_* deltas never point at one — and `carries`
  (v5): the wbs-item that carries an ACTIVATED deferred-work row, written in the
  activating batch; the `deferred-work-carried` advisory lists Activated rows no open
  item carries),
  not only in prose. `relates_to` is the documented untyped escape hatch. Endpoint types are
  enforced at write time and by the **blocking G-REL gate**. Edges are keyed (from, to,
  relation), so a new relation never replaces an old one — a wrong edge is RETIRED
  (`retire: true` on the trace-edge item: the triple is deleted, the relation rule is not
  consulted, and the server journals a `correction` row naming it — v4.6) and the correct
  edge written in the same batch. Retire a wrong edge only, never to make a gate pass.
- A full-row update that only means to flip a status names the columns it did NOT mean to
  change — `expect_unchanged: ["title", ...]` on the item — and the store refuses the write
  if any of them differs from the stored row (v4.7; the field's LL-063: a paragraph lost
  mid-paste with `ok: true`). Opt-in; the immutability trigger's self-verifying property
  for the long-text registers that have no trigger.
- Every MVP `FR-/NFR-` must be reachable to ≥1 decision, ≥1 work item, and ≥1 test (G-TRACE);
  a requirement with zero edges trips the `requirements-wired` advisory.
- Waivers and gates point at entities via their own `applies_to` column, not edges.

## Supersession & deprecation

- Superseding creates a new ID and sets `superseded_by`/a `supersedes` edge; the old item
  stays (status Superseded) so history and rationale survive.
- Deprecating marks an item Obsolete with a one-line reason; downstream references are
  updated or explicitly noted as historical.
