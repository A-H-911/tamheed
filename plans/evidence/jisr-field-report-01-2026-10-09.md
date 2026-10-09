# Field report jisr-01 (2026-10-09): FB-001 and LL-001 from the `jisr` package, tamheed 6.2.0

Two `entity_export` envelopes handed upstream by the operator on 2026-10-09, copied here byte for
byte from `C:\Users\ahammo\Repos\jisr\tamheed-package\exports\` (data, never edited; nothing was
written into that repository). FB-001 is the defect plan 214 fixes. LL-001 is the lesson the field
wrote for itself. The hook print and the gate replay that close the report follow the two files.

## `exports/feedback.json`

```json
{
 "tamheed_export": {
  "version": "6.2.0",
  "package": "tamheed-package",
  "tool": "entity_query",
  "args": {
   "type": "feedback"
  },
  "digest": "e4f206d668278b176244cce42aa4ff415bfe31e151e9f43e0296d0104417ef63",
  "memory_matches_disk": true,
  "count": 1,
  "total": 1,
  "partial": false
 },
 "result": {
  "ok": true,
  "rows": [
   {
    "id": "FB-001",
    "kind": "defect",
    "title": "G-COMPLETE's marker scan reads the append-only journal, so a journal entry that quotes a removed marker fails the gate forever",
    "detail": "gate_run on 2026-10-09 (tamheed 6.2.0) reports G-COMPLETE fail: {id: PE-011, column: entry, marker: \"OQ-019 is resolved — remove the marker\"}. PE-011 is a work-done journal entry that quotes, in prose, the clarification marker it had just replaced in FR-016. The placeholder scan in gate_run exempts progress_entries.entry (server/tamheed_server.py line 2651, _EXEMPT, with the comment that an append-only journal means one authoring slip would fail the gate forever). The marker scan _scan_markers (lines 622 to 659) applies no such exemption: it reads every TEXT column except custom_attributes in every table, the journal included. The journal cannot be edited (expect_unchanged and upsert both refuse progress-entry rows as append-only), so the failure cannot be repaired from the package.",
    "workaround": "A correction entry (corrects PE-011) states that the text is a quotation, not a live marker. The handoff names the standing G-COMPLETE failure and this row. No side tool was written. Expected fix upstream: give _scan_markers the same _EXEMPT set as the placeholder scan, or scan the journal for markers only on entries newer than the OQ's resolution.",
    "tool_path": null,
    "tool_or_rule": "gate_run / G-COMPLETE / _scan_markers",
    "plugin_version": "6.2.0",
    "lifecycle_status": "Confirmed",
    "confirmed_by": "Eng. Anas Hammo (operator)",
    "confirmed_at": "2026-10-09",
    "resolved_in": null,
    "upstream_ref": null,
    "recorded_at": "2026-10-09",
    "custom_attributes": null,
    "last_referenced": null
   }
  ],
  "count": 1,
  "total": 1,
  "next_after": null
 }
}
```

## `exports/lessons.json`

```json
{
 "tamheed_export": {
  "version": "6.2.0",
  "package": "tamheed-package",
  "tool": "entity_query",
  "args": {
   "type": "lesson"
  },
  "digest": "e4f206d668278b176244cce42aa4ff415bfe31e151e9f43e0296d0104417ef63",
  "memory_matches_disk": true,
  "count": 1,
  "total": 1,
  "partial": false
 },
 "result": {
  "ok": true,
  "rows": [
   {
    "id": "LL-001",
    "title": "A journal entry describes a clarification marker, never quotes it",
    "statement": "A journal entry never contains the literal text of a clarification marker. It names the open question and says the marker was added or removed. The marker scan reads the append-only journal, and a quoted marker that cites a resolved question fails G-COMPLETE with no repair.",
    "context": "2026-10-09: PE-011 recorded that FR-016's marker for OQ-019 was replaced, and quoted the marker's literal text. OQ-019 was Deferred with a resolution in the same batch. gate_run then failed G-COMPLETE on PE-011 (FB-001).",
    "recommendation": "Write \"the OQ-019 clarification marker\" or \"the marker citing OQ-019\". Before any progress_update, search the entry text for the opening of a marker and reword it.",
    "rationale": "The journal is append-only by design. A correction entry can retract a sentence but cannot remove text from the scanned column, so a literal marker in the journal stays a gate failure until the plugin changes.",
    "kind": "improve",
    "category": "journal, gates, markers, G-COMPLETE",
    "impact_if_followed": "G-COMPLETE stays clean while open questions resolve.",
    "impact_if_ignored": "A permanent G-COMPLETE failure the operator must explain at every readiness review.",
    "lifecycle_status": "Approved",
    "recorded_at": "2026-10-09",
    "confirmed_by": "Eng. Anas Hammo (operator)",
    "confirmed_at": "2026-10-09",
    "pinned": 0,
    "promoted_to": null,
    "superseded_by": null,
    "custom_attributes": null,
    "last_referenced": null
   }
  ],
  "count": 1,
  "total": 1,
  "next_after": null
 }
}
```

## The 6.2.0 acceptance in `jisr`, measured 2026-10-09 (the operator's second ask)

The root `CLAUDE.md` (written 2026-10-08 15:47 by the first `package_open` under 6.2.0) is the stub
byte for byte: the package title, the operator's comment,
`## Tamheed progress tracking`, `@tamheed-package/CLAUDE.md`. `tamheed-package/CLAUDE.md` holds the
planning note in the emit's shape. `AGENTS.md` is absent, and the stub imports one only when the
operator writes it. The jisr session log (`.remember/today-2026-10-08.md`, 15:36-15:51) records the
same event from the other side: "package_open run (6.2.0 tamheed pkg opened, root CLAUDE.md created,
resume block matched expectations)". No lock was held. The SessionStart hook, run read-only from the
tamheed repository with `CLAUDE_PROJECT_DIR` on jisr and `TAMHEED_HOOK_LOG` unset, printed:

```
tamheed resume — package `tamheed-package` (schema 8) — unlocked
Handoff PE-018 (2026-10-09T10:43:06Z, agent:session_...); 0 work-done/transition entries since.
  [the handoff's seven lines: the field project's own words, left in the field]
Feedback awaiting upstream or the operator: FB-001
Latest journal: PE-018 (handoff), PE-017 (transition), PE-016 (lesson-confirmed)
Next: Read handoff PE-018 and its corrections, then continue the planning half with /tamheed:tamheed at the stage it names. Invoke tamheed:package-writes before your first write, and write a fresh handoff (tamheed:session-handoff) before the next compaction
Skill: tamheed:package-writes — invoke it by name before your first write.
```

## The gate replay over a scratch copy of the field's package

`plans/evidence/scripts-214/replay_jisr_214.py` copies `jisr/tamheed-package` to a temp folder, opens
the copy in-process (`_WIRE_ROOT` off), runs `gate_run` and `readiness_check("package")`, closes and
deletes the copy. The `head` run loads HEAD's server (`git show`) from a temp copy of the bundle. jisr
before and after both runs: 55 untracked entries, no lock, nothing written.

```
[head] opened the copy: package tamheed-package, wiring None, half planning
[head] ready=False
[head] G-IDS=pass
[head] G-DEC-STATUS=pass
[head] G-REQ-SRC=pass
[head] G-TRACE=pass
[head] G-SET=fail failures=['acceptance-criterion', 'phase', 'prompt']
[head] G-PROGRESS=pass
[head] G-COMPLETE=fail failures=['PE-011']
[head]   {"id": "PE-011", "column": "entry", "marker": "OQ-019 is resolved — remove the marker"}
[head] G-REL=pass
[head] clarifications-open=fail entities=[18 live markers: FR-001, FR-002, FR-013, FR-014, FR-015, NFR-001, NFR-002, NFR-003, NFR-006, KPI-001..004, SEC-064, SEC-065]

[fixed] opened the copy: package tamheed-package, wiring None, half planning
[fixed] ready=False
[fixed] G-IDS=pass
[fixed] G-DEC-STATUS=pass
[fixed] G-REQ-SRC=pass
[fixed] G-TRACE=pass
[fixed] G-SET=fail failures=['acceptance-criterion', 'phase', 'prompt']
[fixed] G-PROGRESS=pass
[fixed] G-COMPLETE=pass
[fixed] G-REL=pass
[fixed] clarifications-open=fail entities=[the same 18]
```

The field's package passes G-COMPLETE on the fixed engine with every other gate and advisory
unchanged. FB-001 is resolved by plan 214, released as 6.2.1 (plan 215).
