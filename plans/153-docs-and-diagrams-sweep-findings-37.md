# Plan 153: docs and diagrams sweep for v5.6.0

> Maintainer-executed, 2026-09-28. Batch map: [151-155-batch-findings-37.md](151-155-batch-findings-37.md).
> Rulings R36, R37, R41, R43, R44.

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## What changed

| File | Change |
|---|---|
| `docs/install.md`, the trace paragraph | the line's new shape; what `version=` answers; a line with no `version=` is an older hook's; why the field sits after the timestamp; read the line by key |
| `docs/install.md`, who writes a line | enablement is read from the folder a session starts in, quoted from Claude Code's settings page; a session started in a subfolder loads no plugin; the field saw it once and confirmed the rule by its own method |
| `docs/install.md`, the upgrade section | a version folder says a release is installed, never that a session runs it: the previous folder stays 14 days, quoted from the plugin loading reference; three readings say what runs; the first export, and what the two keys mean |
| `SECURITY.md` | the version in the line and in the page's head, each under the token rule |
| `plugins/tamheed/server/README.md` | the line's shape; `review_exported_by` in the `package_verify` row |
| `README.md` | the key in the tool table; the hook's release in the trace sentence |
| `docs/architecture.md` | the resume diagram's trace note; a v5.6 paragraph. The diagram gains no arrow: it shows no export, so "written LAST" names the last journal entry |
| `docs/design-decisions.md` | §18: D-TRACE-VERSION with its departure from the append convention, D-EXPORTED-BY, D-EXPORT-BEFORE-COMMIT, D-WORD-RULING, D-CARRIED-LINE, D-LINT-NEGATED, what was not absorbed and not built, and what the maintainer owns |
| `CHANGELOG.md` | the `[Unreleased]` body, naming first what a reader of a log line or a tool result sees change |
| `plans/README.md` | the findings_37 section |
| `plans/151-155-batch-findings-37.md` | the batch record: measurements, rulings, errors owned |
| `plans/evidence/scripts-findings-37/` | `m37.py` and its output |

## Read and left

`docs/entities.md`, `docs/methodology.md` and `docs/workflow.md` name neither the export's order,
nor `review_current`, nor the trace line (grep, no hit). `docs/migrate-from-keystone.md:166` exports
and then commits, which is the rule.

## What is stated as measured, and what as documented

| Sentence | Basis |
|---|---|
| Enablement is read from the session's primary working directory | documented, quoted |
| The previous version folder stays 14 days | documented, quoted |
| A session started in a subfolder listed no plugin and wrote no line | the field, one observation |
| A custom meta name is allowed | the HTML Standard, quoted |
| A new key is usually appended at the end of a `key=value` line | one author's page; the release departs from it and says why |

Nothing is said about `.in_use` markers: they are on no page, and the field refuted its own
reading of them.

## Validation

| Check | Result |
|---|---|
| `python check.py lint` after the sweep | lint 13 refused one sentence of the new §18, which quoted the field's negated line; reworded |
| Grep for the old line shape (`<utc> source=`) over the repo, `.claude/` and `plans/` left out | one hit: `lab/scenario.md:697`, the pass bar of beat 25, which describes the 5.3 line. It gains a pointer to item 28 in plan 154, as it gained one to item 26 in 5.4 |
| Grep for `review_current` over the docs | every hit read; each says "the page's data" or names the digest |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED |
