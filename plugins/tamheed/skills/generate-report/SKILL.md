---
name: generate-report
description: >-
  Invoke to refresh and read the HTML review surface (review.html) and summarise what changed for
  the operator.
disable-model-invocation: true
argument-hint: "[package]"
---

# Generate the review report

Invoke this (`/tamheed:generate-report`) to generate and read the `<package>` HTML review surface.

---

> `<package>` below is the package this project's `CLAUDE.md` Tamheed note names; an argument to
> the slash command names another (`$ARGUMENTS`). Recording obligations: the note's table.
Generate the review surface for the `<package>` Tamheed package:

1. `package_open("<package>")`, then `export_html()`. It writes
   `<package>/review.html` (self-contained, zero-JS). Commit it: its diffs are
   row-scoped and meaningful.
   Then read the prompt rows bound to this skill: `entity_query("prompt", status="Approved", plugin_skill="generate-report")`. Each carries what is true of this project for this ceremony.
2. Open it and use the sticky nav. The page has eleven sections. `#overview` holds the gate
   chips and the package identity (values marked "(v1-manifest-derived)" came from the old
   v1 manifest, not v2 activity). `#resume` is where the last session stopped: the latest
   handoff entry and what followed it. `#flow` is requirement → decision → work → test.
   `#graph` is the relations graph. `#traceability` is the requirement×coverage matrix, with
   the raw edge dump folded below it. `#execution` is AC × latest verdict + progress log.
   `#readiness` holds the rules, their status, the waivers applied. Then `#lessons`,
   `#feedback`, `#registers` (families over 50 rows are folded: click the summary to
   expand), and `#gaps` (adoption gaps + screening notes).
3. Read the freshness line. "no v2 activity recorded yet" means nothing has been
   recorded since migration/creation. If work has happened, the operator runs
   `/tamheed:progress-sync` first, then re-export.
4. Summarize for the operator: verdict, notable register deltas since the last
   committed review.html (git diff), and anything folded that deserves attention.
5. `package_close()`.
