# Run 34 — the scratch phase of lab beat 34 (plan 198): the 6.0.0 migration by a real agent

One headless conversation on a scratch copy of the fixture (`beat34_setup.py`), two turns, each
turn a NEW client process (`labrun_turns.py`, run label `r34`). Both turns are the operator's words,
opening with the standing preamble from `run-words.md`: the migration is operator-initiated and no
slash skill runs it. The package is `package` under the workspace; the actor for every write is
`agent:lab-beat-34`. Nothing of this run is written to the fixture.

## T1 — words

{PREAMBLE}

Your task this session, on the operator's words. The plugin is tamheed 6.0.0 and this package was
last written under 5.9.0. (1) `package_open("package")`, then `server_info`: quote the plugin
version and the schema version. (2) `package_migrate("package")` with no confirm: the PREVIEW. Quote,
from the tool's own result, every file under `prompts/` and what the plan does with it (converted
to which row id and kind, moved, or removed), the `entry_point` line, the folder line, and the
G-SET sentence if the report carries one. (3) STOP. Write nothing. Do not confirm. The scratch copy
you are working on IS the operator's backup. (4) Final message: the quoted plan, one line on what the
operator must say for the migration to run, one line on anything the plugin refused.

## T1b — words

{PREAMBLE}

My order in the last turn was wrong, and you were right to stop: `package_migrate` runs on a CLOSED
package. This turn, after the unlock on my word, do NOT open the package. (1) `package_migrate("package")`
with no confirm: the PREVIEW. Quote, from the tool's own result, every file under `prompts/` and what
the plan does with it (converted to which row id and kind, moved, or removed), the `entry_point` line,
the folder line, and the G-SET sentence if the report carries one. (2) STOP. Write nothing. Do not
confirm. The scratch copy you are working on IS the operator's backup. (3) Final message: the quoted
plan, one line on what the operator must say for the migration to run, one line on anything the
plugin refused.

## T2 — words

{PREAMBLE}

Your task this session, on the operator's words, continuing the migration you previewed. After the
unlock on my word, do NOT open the package before step (1): `package_migrate` needs it closed. The
operator's word: "Confirmed: run package_migrate("package", confirm=true), 2026-10-04, lab beat 34."
(1) Run it and quote the report's `prompt_rows`, `entry_point`, `prompts_folder` and
`prompt_files_applied` lines from the tool's own result. (2) `package_open("package")`. Read the
kickoff row whole: `entity_query("prompt", ids=["PRT-001"])`. (3) The operator's second word: "The
operator approves PRT-001 as the kickoff, 2026-10-04, lab beat 34." Set its `lifecycle_status` to
Approved in place with a full-row `entity_upsert` carrying `expect_unchanged` on every column you
do not touch (an Approved prompt row is edited in place, never superseded). (4) `handoff_emit` on
the workspace root (the folder holding `CLAUDE.md` and `package/`) with `refresh_stock=true`. Quote
the `prompt_library.refreshed` list and, from the note it wrote, the marker line and the line that
names PRT-001. (5) `export_html()`, then confirm from the file that `review.html` carries a section
with id `prompts`. (6) `readiness_check("package")`: quote the `prompt-ids-resolve` status and its
population. (7) Write the handoff LAST, as `tamheed:session-handoff` says; the actor is
`agent:lab-beat-34`. (8) `package_close`. Final message: the ids you wrote, in order; the quoted
report lines; the note's two lines; one line on anything the plugin refused.
