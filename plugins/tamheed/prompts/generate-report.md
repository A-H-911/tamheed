# Generate the review report

Paste this to produce and read the `{package}` HTML review surface.

---

Generate the review surface for the `{package}` Tamheed package:

1. `package_open("{package}")`, then `export_html()` — it writes
   `<package>/review.html` (self-contained, zero-JS; commit it — its diffs are
   row-scoped and meaningful).
2. Open it and use the sticky nav: `#overview` (gate chips + package identity —
   values marked "(v1-manifest-derived)" came from the old v1 manifest, not v2
   activity), `#registers` (families over 50 rows are folded — click the summary
   to expand), `#traceability` (the requirement×coverage matrix; the raw edge
   dump is folded below it), `#execution` (AC × latest verdict + progress log),
   `#gaps` (adoption gaps + screening notes).
3. Read the freshness line: "no v2 activity recorded yet" means nothing has been
   recorded since migration/creation — if work has happened, run the progress-sync
   prompt first and re-export.
4. Summarize for the operator: verdict, notable register deltas since the last
   committed review.html (git diff), and anything folded that deserves attention.
5. `package_close()`.
