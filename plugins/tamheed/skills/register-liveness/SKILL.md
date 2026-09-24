---
name: register-liveness
description: >-
  Invoke periodically during execution, not only at close: the playbook that works every advisory readiness finding (the amber list) - resolve each or carry it deliberately, on a cadence.
disable-model-invocation: true
argument-hint: "[package]"
---

# Register liveness — work the amber list

Invoke this (`/tamheed:register-liveness`) periodically during execution of `<package>` (not only at close): the
readiness engine NAGS about decaying registers — this is the playbook that answers it.
Registers stay alive because someone works the ambers, in one sitting, on a cadence.

---

> `<package>` below is the package this project's `CLAUDE.md` Tamheed note names; an argument to
> the slash command names another (`$ARGUMENTS`). Recording obligations: the note's table.
Sweep the advisory findings of the `<package>` Tamheed package. Advisories never block,
which is exactly why they rot — resolve each finding or carry it DELIBERATELY; silence
is the only wrong answer.

1. `package_open("<package>")` if not already open, then `readiness_check("package")`.
   Work every advisory rule whose status is `fail` (an `indeterminate` rule means the
   keyed column is empty everywhere — populating it IS the fix). Do not touch blocking
   failures here — they belong to the close-out prompts.
2. **Ambiguity markers** (`clarifications-open`): each entry names a field carrying
   `[NEEDS-CLARIFICATION: OQ-NNN]`. Resolve the OQ if you now can, then remove the
   marker from the field (full-row upsert); still genuinely open → leave both.
3. **Open questions** (`open-questions-overdue`, then `open-questions-resolved`):
   overdue ones first — answer it (set `resolution` + `resolved_by`), re-date it
   (new `due_by`, full row), or escalate what the silence is costing into a `risk`
   row. A question with no `owner`/`due_by` gets both.
4. **Assumptions** (`assumptions-current`): past `validation_date` — re-validate
   (confirm it still holds; set a fresh `validation_date`) or, if it no longer holds,
   record the fallout: a `risk` row (or a `scope-change` if the plan must move) and
   the assumption to `Rejected`.
5. **Risks** (`risk-liveness`): every open high-probability/high-impact risk gets an
   `owner` and a `response_strategy` (avoid|mitigate|transfer|accept) — no owner means
   nobody monitors. Prerequisite: the rule reads the scale — with `probability`/`impact`
   unpopulated on every open risk it reports `indeterminate`, not pass (it cannot
   measure); populate the scale per `${CLAUDE_PLUGIN_ROOT}/references/governance.md` first.
6. **Hypotheses** (`hypotheses-measurable`): past Draft without `metric` + `threshold`
   — set both NOW (the number is decided BEFORE the experiment runs) or send the
   hypothesis back to Draft honestly.
7. **Decisions that look architectural** (`decisions-look-architectural`): apply the
   one-way-door test (hard to reverse? broad blast radius? re-debated?). If it passes,
   draft the `adr` row (context/decision/consequences/`confirmation`) and set
   `promoted_to` — **STOP for operator approval before the ADR leaves Proposed**.
   If it genuinely is a two-way door, note why in the decision's `rationale`
   (full-row upsert) so the nag has an answer on record. Every full-row upsert in
   this sweep that only means to change ONE column re-fetches the row through
   `entity_query` and names the rest in `"expect_unchanged": [...]` — the store
   refuses transport drift on the columns you did not mean to touch. Name only columns
   the item CARRIES: an omitted column is preserved by the store, so naming it asserts
   nothing and is refused; a one-token change is a `substitute` item, which needs no
   re-fetch at all.
8. **Unmerged scope changes** (`scope-changes-merged`): an Approved `SC-` whose deltas
   never landed — apply the row changes its `scope_adds`/`scope_modifies`/
   `scope_removes` edges name (via `entity_upsert`); an `amends` edge merges its
   RULING (a `DEC-` by full-row upsert; an `ADR-` by supersession — the successor ADR
   is the merge). **`Merged` is the LAST step, not the first**: after applying, RE-READ
   every row the edges name (`trace_query("<SC-x>")` — the edges are the checklist),
   rewrite any sentence in those rows that the change discharges ("needs an SC- first",
   "do not edit X"), and only then set the `SC-` to `Merged` — nothing mechanical
   checks the assertion `Merged` makes.
9. **Unbound ACs** (`acs-slice-bound`): bind each to its slice (full-row upsert —
   NOTE: an Approved AC's content is immutable; if the binding itself is the change,
   supersede instead), or record the deliberate choice to verify at package scope
   only.
10. **Minor defects** (`defects-minor`): before framing ANY question for the operator,
    `entity_query(search="<DEF-id>")` across families — a ruling often lives in a
    decision, an AC or a scope change, never on the defect row (the field re-asked three
    questions whose answers were already recorded). Fix the quick ones now (the defect-triage
    flow, `${CLAUDE_PLUGIN_ROOT}/skills/defect-triage/SKILL.md`: fix, evidence-chained `audit_record`, status flip, `work_bind`). For ones
    worth carrying, propose a waiver to the operator — **waivers are operator-only:
    you NEVER author a `WVR-` row without their words** — or convert to
    `deferred-work` with a trigger. If `waivers-open-ended` fires, it names whole-rule
    waivers with no expiry: each keeps waiving rows written long after it was approved.
    Show the operator what it absorbs today and ask for an `expires` date or a narrower
    `applies_to` — their decision, never yours.
11. **Deferred work** (`deferred-work-reviewed`): the rule lists Open and Scheduled
    rows — the ones a human still judges. Read each activation trigger against current
    reality. Fired → say so and point the operator at `/tamheed:replan-deferred`
    (activation is a scope decision, not yours); once Activated the row is work — its
    WBS rows carry it — and leaves this list. Not fired → it is deliberately carried;
    nothing to write, and the row stays listed until it fires or is closed.
12. **Execution plans** (`execution-plans-approved`): plans still Draft/Proposed for
    active slices — finish them and **STOP for operator approval**.
13. **Unwired requirements** (`requirements-wired`): every listed requirement gets its
    real edges — `derives_from` the deciding DEC-/ADR-, `implements` from its slice/
    work item, `tests` from its test. `relates_to` only when nothing typed fits — and
    when a typed edge replaces an old `relates_to` (or any wrong edge), RETIRE the old
    one in the same batch (`retire: true` on the trace-edge item; journaled): edges
    are keyed (from, to, relation), so the new one never replaces the old by itself.
14. **Lessons awaiting confirmation** (`lessons-confirmed`): walk each Proposed `LL-`
    row WITH the operator — this is their interview, not yours; the store ENFORCES it
    (an approving upsert without `"operator_confirm": true` is refused, in every
    mode). Per lesson they say: **Approve** — then RE-READ the row and resend it
    byte-identical on content with `lifecycle_status: "Approved"`, `confirmed_by`
    (their attribution — it lands WITH the approval, never later), the pin decision,
    and `"operator_confirm": true` (their words are the flag; the server records the
    typed audit event itself); **Reject** (kept as evidence); or **refine** (upsert a
    successor `LL-` and point the old row at it with `superseded_by` — the transition
    write may change NOTHING else, the guard refuses content drift). **The pointer
    alone retires nothing: an Approved lesson keeps binding until its STATUS is
    `Superseded`.** The engine sets that itself the moment the operator approves the
    successor; retiring a binding lesson by hand is their word too
    (`"operator_confirm": true`). `lessons-superseded-binding` names any Approved
    lesson still binding beside an approved successor. When several Approved lessons share a
    theme, offer PROMOTION: point the operator at `/tamheed:skill-promote` — the
    distillation ceremony is its own interview. **STOP for the operator's words on
    every lesson — you never self-approve, mechanically.**
15. **Note budget** (`lessons-note-budget`): the always-loaded CLAUDE.md note renders
    EVERY pinned lesson plus an unpinned fill of the 10 highest-numbered Approved ones;
    past the curation ceiling (20 rendered lines) the rule names the rows that render
    beyond it — the promotion candidates. The arithmetic (the field measured it, v5):
    while ten or more unpinned Approved lessons exist the fill is always exactly ten, so
    unpinning or promoting a PINNED lesson removes exactly one line whatever its number
    (a high-numbered one displaces the tenth of the fill; a low-numbered one never
    enters) — and retiring or rejecting an UNPINNED lesson removes NOTHING, the fill
    simply refills. With N pinned lessons reaching 20 therefore needs at least N - 10
    pinned removals (promotions or unpins), and no unpinned retirement counts toward it.
    Put them to the operator: distil the shared themes into a skill
    (`/tamheed:skill-promote` — promoted lessons graduate out of the note) or unpin what
    no longer needs to bind every session. Pinning stays their choice; the rule only
    makes its cost visible.
16. **Dangling references** (`prose-ids-resolve`): identifiers written in PROSE that
    resolve to no entity — `G-IDS` checks foreign keys and the index, never a sentence,
    so a row can cite a `DEF-` that was never recorded and every gate stays green. For
    each `<row>.<column> -> <id>`: correct the id if it is a slip, or record the missing
    row if the reference is real. An immutable row (approved AC, ADR, lesson) is
    repaired by supersession, never by an edit. Code spans, the append-only journal and
    Superseded/Obsolete rows are not scanned — history may name what was refused.
17. **Dangling references in prompt files** (`prompt-ids-resolve`): the same rule over
    the PROJECT's own `prompts/*.md` (never a stock body) — the prose a session reads
    before any tool. Fix the id or record the row; quote history in backticks (a code
    span is inert and lands in `in_code_spans`). A green here means every id RESOLVES,
    not that the sentence about it is true.
18. **Feedback reported and not yet answered** (`feedback-unanswered`): each `FB-` row
    that went upstream and has no `resolved_in`. If the maintainer shipped or answered
    it, set it `Resolved` with `resolved_in` and `upstream_ref` as a PARTIAL row (id,
    kind, title and those three — omitted columns are preserved, but a partial row still
    carries every NOT NULL column); if upstream declined,
    `Rejected` on the operator's word; otherwise carry it and say so. Local-tool rows are
    registers and never appear here.
19. Close the sweep: `progress_update([{"entry": "liveness sweep: <per-family tally —
    resolved / carried / escalated / awaiting operator>", "event_type": "note",
    "actor": "agent:<session>"}])`, then `readiness_check("package")` again and report
    the advisory delta plus everything now awaiting operator words (promotions,
    waivers, plan approvals, activations).
