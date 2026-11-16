# Plan 238 -- the 6.6.0 field briefs, to the 6.5.1 standard (docs-only, after the tag)

> Status: DONE 2026-11-16 (the commit below). Both fields run 6.5.1. The briefs committed at the
> tag were short, and Jisr's assumed a 6.4.0 store. Both are rewritten in place.

- **Measured** (`scripts-238/`), on scratch copies only, with `core.autocrlf=false` and each
  field's `.gitignore`:
  - ACMP: a `git archive` of its commit `156398f8`.
  - Jisr: the operator's read-only export of its commit `7b1c85c` (branch
    `feature/sl-008-workshops`, status unchanged before and after the export).
  - On both: the sync adds only `standup-report` and moves two files, a pure append. Gates and
    readiness do not move. A first report records with `live_match` true.
  - Route A (`checkout`; `restore --source=PRE` with `clean -nd`/`-fd`, a live draft included;
    `revert`) ends equal to PRE, and 6.5.1 opens the result as before.
  - The plugin alone: 6.5.1 writes, exports and reopens a store that 6.6.0 wrote. It keeps
    `standup_reports.jsonl`, and its verify names that file dirty. Removing the file would
    restart reports at `RPT-001` over the committed page, so the briefs say: keep it.
- **Route B, after the tag**, in a separate `CLAUDE_CONFIG_DIR` (the real records unchanged),
  with Claude Code 2.1.325:
  - "updated from 6.5.1 to 6.6.0";
  - "updated from 6.6.0 to 6.5.1" with `#v6.5.1`;
  - a pinned repository answers "already at the latest version (6.5.1)".
- **The briefs:**
  - the checks, with PRE and the untracked list saved outside the repository;
  - a restart re-entry keyed on `server_info`;
  - a reading before the sync, the preview with a STOP, the confirm, and the go/no-go;
  - the guide;
  - the first report as the OPERATOR's step;
  - the way back by route A, the plugin alone and route B;
  - six classes.
- **Rehearsed** by headless agents. Turn 1 ran under the real 6.5.1 bundle and stopped at the
  restart with PRE saved. Turn 2 ran under 6.6.0 and continued, and every class held. Jisr's
  route A ended with an empty `git diff PRE`.
- **The prompts** pin the publishing commit and each brief's sha256 (the operator's choice). A
  correction needs a new prompt.
