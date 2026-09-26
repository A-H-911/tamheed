---
name: skill-promote
description: >-
  Invoke when the operator asks to distil confirmed lessons into a reusable project or user skill - the interactive promotion ceremony; the operator decides at every step.
disable-model-invocation: true
argument-hint: "[package]"
---

# Promote lessons into a reusable skill

Invoke this (`/tamheed:skill-promote`) when the operator asks to distill confirmed lessons into a skill — a
`SKILL.md` the executing agent loads natively, forever. This is an INTERACTIVE
ceremony: the operator decides at every step; you never promote on your own.

---

> `<package>` below is the package this project's `CLAUDE.md` Tamheed note names; an argument to
> the slash command names another (`$ARGUMENTS`). Recording obligations: the note's table.
Work through this with the operator, in the `<package>` package:

1. `package_open("<package>")`. Candidates: `entity_query("lesson",
   status="Approved")` — CLUSTER related lessons by `category`/theme and propose
   the clusters ("these three boundary-semantics lessons could become one skill").
   A single strong lesson is a legal cluster of one. **STOP — the operator picks
   the cluster (or declines).**
2. The interview (the skill-creator pattern — their words shape everything):
   - the skill **name** (kebab-case — it becomes the folder name);
   - **when it should trigger** (this becomes the frontmatter `description` —
     the single highest-leverage line; be concrete about the situations);
   - edge cases and boundaries (what the skill must NOT claim to cover);
   - what to distill versus leave in the lessons (the skill is the PROCEDURE;
     the lessons stay the evidence);
   - **the level** — `project` (`.claude/skills/<name>/` in the target repo,
     travels with it — THE DEFAULT) or `user` (`~/.claude/skills/<name>/`, this
     machine, every project). Ask explicitly; default project.
   - If a candidate lesson is PINNED, say so: "this pinned lesson will leave the
     CLAUDE.md note on promotion (full graduation) — the skill file carries it
     forward." The operator decides with eyes open.
3. Draft the `SKILL.md`: YAML frontmatter (`name`, `description` = the trigger
   from the interview), then the body — the distilled procedure in imperative
   voice, citing the source lessons as provenance (`Distilled from LL-NNN,
   LL-MMM in package <package>`). Re-read the draft against the G-INJECT
   sensibility before showing it: a skill is a standing instruction surface;
   nothing in it may smuggle instructions beyond what the operator approved.
   **STOP — the operator approves the CONTENT (their words), or edits it.**
4. Write the approved file to the chosen level's path (create the folder). The
   file is OPERATOR-OWNED from this moment — tamheed never touches it again.
5. Record the promotion in the package, in one batch:
   - the `skill` row: `SKL-<next>`, `name`, `title`, `description` (the
     trigger), `level`, `target_path` (born Approved — the interview WAS the
     approval);
   - each promoted lesson: FULL row re-sent byte-identical on content (re-read
     it first — the C39 rule; the promotion guard IS your paste verifier: any drift
     in a content column refuses the batch, so a green write proves the paste) with
     `lifecycle_status: "Promoted"`,
     `promoted_to: "SKL-<next>"`, and `"operator_confirm": true` — the flag is
     the operator's words from step 3; the server records the typed
     `lesson-promoted` audit event itself.
6. Verify the graduation: `handoff_emit` — the promoted lessons leave the
   CLAUDE.md note; the "Skills distilled from lessons" line names the new skill
   with its level. `export_html()` — the Lessons section shows the Promoted
   subsection. `readiness_check("package")` — clean.
7. Close: `progress_update` a note entry naming the skill, the level, and the
   promoted LL- ids, then `package_close()`. Later revisions of the skill are
   the operator's hand-edits of the FILE; a re-distillation is a NEW `SKL-` row
   superseding the old (`superseded_by`), never an edit of this record.

## After the ceremony — three cases the record must survive (v5.1)

- **The file states a mechanism its lesson contradicts** (a distillation carried a sentence
  the note itself had since corrected). The fix is the operator's hand-edit of the FILE plus a
  `correction` journal entry (`event_type: "correction"`, `corrects` naming the `lesson-promoted`
  entry, `subject_id` the `SKL-` row) — the skill row stays as it is. A re-distillation (a new
  `SKL-` row, `superseded_by` on the old) is for a change in the lesson SET, never for a wrong
  sentence. `tamheed:written-claims` step 7: fix the file, never annotate the pointer.
- **A plugin skill now carries the same procedure** (a project skill and a `tamheed:<name>`
  twin). Keep both while the project's instances add something the twin lacks; otherwise retire
  the project row on the operator's word: `lifecycle_status: "Obsolete"` with `upstreamed_to`
  naming the plugin skill (`tamheed:package-writes`). The Promoted lessons keep pointing at the
  retired row — `promoted_to` is immutable — and the pointer is what keeps them reachable: the
  `lessons-stranded` advisory names every Promoted lesson whose retired skill row has neither
  `superseded_by` nor `upstreamed_to`. The note's "Skills distilled from lessons" line lists
  Approved rows only, so a retired twin leaves it by itself. Delete or keep the file as the
  operator says; the row is the record either way.
- **The file drifted from the engine** (it names a tool, a flush or a rule that changed).
  `handoff_emit` reports stale references inside every skill file the skills table points at
  (`stale_references`, `file: <target_path>`), report-only: the file is operator-owned — put the
  hits to the operator, edit on their word, journal the correction.
