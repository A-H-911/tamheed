# Plan 167: the teaching and the docs follow the engine, and the corrections of 5.7.0

> Maintainer-executed, 2026-09-30. Batch map: [165-169-batch-fb026-fb027.md](165-169-batch-fb026-fb027.md).
> Source: rulings R56–R58; the field's `FB-026`; the security review of plan 166's docs paragraph.

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## What changed

| File | Change |
|---|---|
| `skills/session-handoff/SKILL.md` | the carried rule rewritten: a carried line is re-measured at its source AND against the rulings given since; one that cannot be carries the mark with its source and the date last measured; the mark lasts one handoff; `handoff-repeated` names the lines by number; do not reword to clear it. Field evidence: the two FB-027 lines, anonymised |
| `skills/orient-resume/SKILL.md` | a marked line is a claim about the past, re-measured before it is acted on |
| `skills/tamheed/SKILL.md` (the front door) | one clause naming the rule |
| `server/tamheed_server.py`, the two journal descriptions | name their argument: "`entries` is a list; each entry …", "`verdicts` is a list; each verdict …" (333 and 325 characters; one field call had sent `items`) |
| `docs/install.md` | the 5.7.0 note's dated correction (O18) with the measurement (2,122 transcripts; 936 / 5; 100 / 12 / 0); step 7, what a session meets at 5.8.0: the rule, the page's one-time re-flow with the git numbers, the scanner paragraph in the field's voice (the security review's four points taken: the ADR's claim attributed, history not rewritten, the store's free text named as where a secret enters, the field's setup called its own decision, neither recommended nor validated), the descriptions |
| `plans/briefs/acmp-5.7.0.md` | class 9's corrected row beside the original; classes 1 and 10 are true and stay |
| `docs/design-decisions.md` | §20's D-DESCRIPTION-IS-REGISTERED gains the dated correction; §21: D-HANDOFF-REPEATED, D-ONE-ROW-PER-LINE, D-RESUME-KEEPS-THE-RECORD, the number, the errors owned |
| `CHANGELOG.md` | the 5.8.0 entry (under `[Unreleased]` until plan 168 stamps the five surfaces, lint 8) and 5.7.0's dated correction |
| `README.md`, `server/README.md`, `references/quality-gates.md`, `state.md`, `handoff.md`, `workflow.md`, `docs/architecture.md`, `docs/entities.md` | the rule named beside `handoff-current`; the two diagrams gain one line each; the advisory count re-measured: twenty-four on the lab fixture, twenty on an empty package (four conditional: waivers, feedback, skill rows, three handoffs) |
| `lab/scenario.md` | item 31 |

## Validation

- `grep -rn "after the reload" docs plans/briefs CHANGELOG.md`: 17 hits read one by one. The
  two false sentences carry their correction (`docs/install.md:255`, the brief's class 9);
  the rest name the server or the hook after a reload, which is true, or are history.
- `grep -rn "carried, not re-measured" plugins`: the skill's rule, `orient-resume`'s sentence
  and the engine's comment; no other site teaches the mark.
- `python check.py lint` after each skill; `python check.py` green.
