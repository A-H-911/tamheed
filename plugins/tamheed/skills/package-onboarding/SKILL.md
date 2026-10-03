---
name: package-onboarding
description: >-
  Invoke for an agent or a teammate's session that has NEVER seen this project's Tamheed package.
  It goes deeper than orient-resume, which assumes prior familiarity. Read-only until the operator
  confirms.
disable-model-invocation: true
argument-hint: "[package]"
---

# Package onboarding: a new agent meets the package cold

Invoke this (`/tamheed:package-onboarding`) for an agent (or teammate's session) that has NEVER seen
`<package>`. It goes deeper than orient-resume, which assumes prior familiarity.

---

> `<package>` below is the package this project's `CLAUDE.md` Tamheed note names; an argument to
> the slash command names another (`$ARGUMENTS`). Recording obligations: the note's table.
Onboard yourself onto the `<package>` Tamheed package from zero:

1. `server_info`: server version, package root. Then `package_open("<package>")`.
2. The why: read the charter and executive summary
   (`entity_query("narrative-document")` → `entity_query("document-section",
   columns=["id", "document_id", "heading", "body"])` for the charter's sections).
3. The rules: `entity_query("invariant")`, `entity_query("constraint")`, and the approved
   `DEC-`/`ADR-` rows (`entity_query("decision")`, `entity_query("adr")`). Never violate
   an invariant, because a violation needs a new ADR. These are FINAL. Do not
   re-litigate.
4. The shape of the work: `entity_query("phase")` and `entity_query("slice")` in
   order, then `entity_query("wbs-item")` for the open backlog. Run `trace_query` from
   the MVP requirements to see how needs → decisions → work → tests connect. Registers are
   read THROUGH the tool, whatever their size. `limit` cuts rows (never fields),
   `total` is exact, and the result's `next_after` pages the rest (`after_id`).
   Quote a known set verbatim with `ids=[...]`, sweep by keyword with `search=`.
   A committed script that must quote the store (a review slate, a docket) reads
   an `entity_export` file the tool wrote under `exports/`. It never reads `data/*.jsonl`
   or rows you pasted by hand.
5. The lessons: `entity_query("lesson", status="Approved")`. Operator-confirmed
   lessons BIND you, every one. This project's CLAUDE.md note renders only the pinned
   ones and the highest-numbered unpinned few. The rest reach you by this query.
   Read them before writing code.
   Where it stands: `gate_run()`, `readiness_check("package")`, the last 10
   `progress-entry` / `audit-verdict` rows, and open `defect`/`deferred-work` rows.
6. The surfaces: `export_html()` and skim `review.html` (overview chips, the
   traceability flow, phase readiness). The situation playbook is the plugin's `/tamheed:`
   scenario skills. `<package>/prompts/README.md` maps situations to them, and
   project-authored prompts live in that folder. Know what is in it.
7. The obligations: read the "Recording obligations" table in this project's CLAUDE.md
   note. Every one of them binds you from the first minute. On genuine ambiguity,
   never assume: create an `OQ-` row (owner + due_by) and put
   `[NEEDS-CLARIFICATION: OQ-NNN]` at the exact ambiguous spot. G-COMPLETE fails
   markers with no live `OQ-` behind them.
8. Report back in five lines: what this project is, the load-bearing invariants, the
   active phase/slice, the gate + readiness verdicts. The fifth line is what you would
   work on first. STOP for confirmation before writing anything.
