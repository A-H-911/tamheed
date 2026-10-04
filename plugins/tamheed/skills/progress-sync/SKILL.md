---
name: progress-sync
description: >-
  Invoke after implementation work to bring the package up to date: typed progress entries, Review
  claims, bindings, evidenced verdicts, scope changes first, lessons, trace edges.
disable-model-invocation: true
argument-hint: "[package]"
---

# Progress sync: record what actually happened

Invoke this (`/tamheed:progress-sync`) after implementation work on `<package>` to bring the package
up to date.

---

> `<package>` below is the package this project's `CLAUDE.md` Tamheed note names; an argument to
> the slash command names another (`$ARGUMENTS`). Recording obligations: the note's table.
Sync the `<package>` Tamheed package with the work just completed:

1. `package_open("<package>")` if not already open.
   Then read the prompt rows bound to this skill: `entity_query("prompt", status="Approved", plugin_skill="progress-sync")`. Each carries what is true of this project for this ceremony.
2. For each meaningful unit of work: `progress_update([{"entry": "<what happened>",
   "phase_id": "<PH-x>", "slice_id": "<SL-x>", "event_type": "work-done",
   "subject_id": "<WBS-x/AC-x>", "actor": "agent:<session>"}])`. Write concrete entries,
   not summaries. A `wbs-item` you believe finished: full-row upsert to
   `lifecycle_status: "Review"` (done-claimed, because `Implemented` means verified, and
   readiness counts Review as open). Read the row again through `entity_query`
   first and send it with `"expect_unchanged": ["title"]` (and every other long
   column you did not mean to change). The store refuses the write if the transport
   changed any of them.
3. For each commit/PR that satisfies package entities:
   `work_bind(ref="<commit-or-PR>", entity_ids=["FR-x", "AC-y", "SL-z"], note="...")`.
4. For each acceptance criterion now verifiable:
   `audit_record([{"ac_id": "AC-x", "verdict": "Met|Partial|Not-met",
   "evidence": "tests/test_x.py::test_y; commit <sha>", "verified_by":
   "human|agent|ci", "verification_method": "auto-test|manual|inspection",
   "against_commit": "<sha>"}])`. An evidenced verdict
   beats a narrated one. Never record Met without pointing at the proof.
5. If scope changed (something deferred, cancelled, expanded): write the typed
   `scope-change` row FIRST, Proposed. Give it `scope_adds`/`scope_modifies`/
   `scope_removes` delta edges to the affected plan rows. Use `amends` when it carves
   an exception out of a `DEC-`/`ADR-` ruling: DEC- full-row upsert, ADR-
   supersede. Only after operator approval apply the mutation it authorizes,
   RE-READ the rows the edges name, and set the `SC-` Merged LAST.
6. Did this work teach something durable, a mistake whose fix future sessions must
   know, or a practice worth repeating? Record it NOW: a `lesson` row (`LL-`, born
   Proposed, kind improve|sustain) + a `learned_from` edge to its source. The statement
   opens with its rule, plus impact_if_ignored. The operator confirms
   later. Only Approved lessons bind future sessions.
7. Any requirement created during this work receives its trace edges (`derives_from` /
   `implements` / `tests`) in the SAME sync. `work_bind` stamps commits, it does
   NOT wire traceability. Edge endpoints must respect the endpoint rules. G-REL
   now FAILS `gate_run` on violating edges, and `relates_to` is the escape hatch. Edges
   are keyed (from, to, relation). A wrong one is RETIRED (`retire: true` on the
   trace-edge item, journaled) and the correct one written in the same batch.
   Never leave the old edge beside its replacement.
8. `gate_run()`: report the verdict delta (including `requirements_unwired`),
   then `package_close()`. A project that commits its review page exports it after
   the last write of the sync and before the commit (`tamheed:package-writes`).
