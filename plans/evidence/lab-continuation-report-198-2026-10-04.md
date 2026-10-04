# Lab continuation report — beat 34, v6.0.0 (plan 198, 2026-10-04)

> `lab/scenario.md` beat 34: prompts return to the store, against the recorded `lab-tracker`
> fixture. Two phases. The scratch phase ran FIRST, by a real agent through the headless harness
> (`plans/evidence/scripts-fb028/labrun.py`, Opus 5.5, `--plugin-dir` on the working tree,
> `--setting-sources ""`, `--permission-mode dontAsk`, the base allow list, never
> bypassPermissions) on a copy of the fixture outside the repository. The fixture phase then ran
> in-process through the working-tree server (`plans/evidence/scripts-ste/labrun-198/beat34.py`,
> actor `agent:lab-beat-34`). The session's writes replaced the fixture's `data/`, `csv/` and
> `review.html`, removed `prompts/` and wrote `README.md` at the package root. The emitted note
> (`package/CLAUDE.md`) was removed after the phase, as beat 33 left it uncommitted. The scratch copy
> was never committed. The run's outputs are beside this report under `scripts-ste/labrun-198/`
> (the turns file, three result files, three reports, the hook trace, the setup and the two scripts).

## 1. The scratch phase: the migration by a real agent

**Setup** (`beat34_setup.py`, in-process): the fixture copied, a workspace `CLAUDE.md` with the
`@package/CLAUDE.md` pointer, nothing emitted. The 6.0 server cannot emit on this package before the
migration (no Approved kickoff row), so the session started with no note. Observed before the run:
`schema_version` 8 (migration 008 applied at connect), `entry_point` `prompts/project-kickoff.md`,
the resume block naming beat 33's handoff `PE-065`, G-SET `pass` with no `prompt` row in the fixture's
registry yet (the registry syncs at `package_migrate`), zero prompt rows.

**The hook.** Three sessions, three trace lines, all `status=silent lines=0`: with no note there is
no package pointer, and the hook printed nothing at startup or at either resume. The agent worked
from the operator's words, which named the package.

**T1, the operator's words (the preview and the STOP).** Session
`00ca494c-0c3a-46ed-a2fa-b3aa6f6c243d`, 6 turns, $0.22, no permission denial. My words ordered
`package_open` and then `package_migrate`. The plugin refused the preview: "package 'package' is
open — package_close it first". The agent STOPPED, wrote nothing, did not close the package on its
own ("I can't tell from here whether closing writes to the package"), quoted the refusal, and asked
for the word. **The error was the words, not the plugin.** A client brief must say that
`package_migrate` runs on a closed package.

**T1b, the corrected words** (`--resume`, a new client process). 4 turns, $0.30. The lock named pid
56080, observed not-running; the unlock on the word (`PE-066`, the journal). The preview, quoted from
the tool's result: `prompts/README.md` "remove (byte-equal to shipped stock)";
`prompts/project-kickoff.md` "convert to PRT-001 (kickoff), then move to prompts-v5-backup/", title
"tick — SL-002 kickoff"; `entry_point` from `prompts/project-kickoff.md` to `PRT-001`;
`prompts_folder: remove`; `entity_types_added: ["prompt"]`; no G-SET sentence (a row converts); the
report's own "nothing written — back the package up … then re-run with confirm=true". The agent
STOPPED with nothing written and said what the operator must say.

**T2, the operator's words** (`--resume`). 20 turns, $0.80, no denial. No lock this turn. The agent
re-ran the preview and compared it with T1b's before confirming. The confirm (`stage: migrated`):
`prompt_rows: ["PRT-001"]`, the `entry_point` line, `prompts_folder: remove`,
`prompt_files_applied: {moved_to_backup: [prompts/project-kickoff.md], removed_stock:
[prompts/README.md], folder: removed}`; the audit journal row `PE-067`. Then `package_open`, the
kickoff row read whole, and on the second word a full-row `entity_upsert` with `expect_unchanged`
on every other column: `changed_columns` = `lifecycle_status` only. `handoff_emit(refresh_stock=true)`
on the workspace root: `prompt_library.refreshed` `[]` (the root guide was already seeded by the
migrate, so the emit found it unchanged), the note rebuilt in `package/CLAUDE.md` (the pointer
pattern), a standalone `.mcp.json` written at the workspace root (the headless server is not
plugin-hosted). The marker line `<!-- tamheed:note v7 -->`; the roster line
`- **PRT-001** [kickoff, the entry point] tick — SL-002 kickoff`. `export_html`: `id="prompts"` at
line 832. `readiness_check`: `prompt-ids-resolve` pass over the `prompts` population of 1 row,
`DEF-090` and `SL-007` inert in code spans; `ready: false` on `acs-met` (AC-003 and AC-005, the
scenario's deliberately-open items). The handoff `PE-068` LAST, then `package_close`. Nothing refused.

Two things the agent said that the maintainer took: the migrate result does not carry the id of the
journal row it appends (`PE-067` was read from the resume block), and the export in step 5 preceded
the handoff, so the scratch page does not hold `PE-068` (the fixture phase exports after the handoff).

## 2. The fixture phase (`beat34.py`, in-process, the committed package)

```
A.before          review_current true, review_exported_by 5.9.0
A.schema          schema_version 8, migrations_head 008_prompts.sql, entry_point prompts/project-kickoff.md
A.gset.before     pass (no `prompt` row in the registry before the migrate)
A.preview         README.md remove (byte-equal to shipped stock); project-kickoff.md -> PRT-001 (kickoff);
                  entry_point prompts/project-kickoff.md -> PRT-001; folder remove; registry + prompt
A.confirm         moved_to_backup [project-kickoff.md], removed_stock [README.md], folder removed
A.backup_removed  true (prompts-v5-backup/ removed from the fixture; git holds the file)
A.row             PRT-001 kickoff "tick — SL-002 kickoff" Proposed, converted_from prompts/project-kickoff.md
A.gset.after      pass
A.stop            "the kickoff prompt PRT-001 is Proposed, not Approved — the handoff carries only what
                  the operator approved. Approve the row in their words (lifecycle_status Approved), then re-run"
A.approved        changed_columns [lifecycle_status]
A.library         unchanged [README.md] (seeded by the migrate), refreshed []
A.guide           tamheed v6.0.0, nine **discipline skills**
A.note            tamheed:note v7; "- **PRT-001** [kickoff, the entry point] tick — SL-002 kickoff"
A.emit.stale      []
A.rule            prompt-ids-resolve pass, population prompts 1 row, entities []
A.handoff         PE-068 (handoff-current pass, handoff-repeated pass)
A.page            Evaluated as of 2026-10-03 -> 2026-10-04, 1101 -> 1125 lines, the Prompts section
A.gate_run.ready  true
A.verify          verified true, dirty [], foreign [], review_current true, review_exported_by 6.0.0
A.lock_gone       true
```

## 3. What the beat measured, beyond the scenario

- **A 5.9-era package under the 6.0 server opens, and G-SET passes vacuously** until the registry
  syncs at `package_migrate`: the fixture's `entity_types` had no `prompt` row before the confirm.
  The two planning-only fixtures (`minimal-brief`, `execution-loop`) took the same sync and then an
  omission row, through `fixtures_198.py`.
- **The migrate seeds the root guide**, so a following `handoff_emit(refresh_stock=true)` reports it
  `unchanged`, never `refreshed`. A brief that promises `refreshed: ["README.md"]` after a migration
  would be wrong.
- **The hook is silent on a package with no note**, at startup and at resume alike. The words carried
  the package name.
- **The words can be wrong before the plugin is**: T1's order (`package_open`, then the preview) is
  refused by design. The agent's STOP without closing on its own is the behaviour the discipline
  skills ask for.
