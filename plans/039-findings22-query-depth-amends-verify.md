# Plan 039 (B35): findings_22 + the ACMP lessons — the query surface with depth, `amends`, `package_verify`, the note budget — v4.5.0

## Status

**DONE (2026-09-06)** — `python check.py` fully green, `--selftest` green (17 tools).
Version stamped **v4.5.0** (MINOR — migration 004, a new tool, additive query
parameters). *Release only on the maintainer's explicit words.*

## What this was

findings_22 (evidence **C43**): an operator-commissioned integrity audit found that a
query surface with no paging had pushed agents onto the files (`LL-011` demands the
full text of every cited record; 91 defect rows overflow any client cap; a FALSE
sentence about the cause then recruited every later session onto the JSONL), that a
scope change amending a ruling could only be `relates_to`, that the one C7 signal
withheld its ids, that a `.converted` leftover lived in the canonical directory, and
that the byte-stability guarantee — which held over 488 commits of history — was a
property nobody could cite. The maintainer asked, in the same breath, for the ACMP
lessons register to be read for anything that would improve tamheed: 62 rows, six of
which named engine or doctrine gaps, and whose size (57 lines rendered into the
always-loaded note) was itself a finding.

Maintainer-locked over three interview rounds: `after_id` + `ids` + `search`; a new
`amends` relation; `package_verify` with a typed `integrity-verified` event; relocate
the leftover on sync; four doctrine lines from LL-061/042/040/004; a
`lessons-note-budget` advisory at 20 rendered lines; refuse all four server-only
journal kinds from callers; one MINOR; the lab's beat 12 by a real agent.

## What shipped

1. **`entity_query(…, after_id?, ids?, search?)`** — keyset paging on the SAME byte
   collation as `ORDER BY id` (`next_after` exact via a one-row look-ahead; `total`
   constant across a walk), a known set in one call, a keyword sweep over TEXT
   columns; the docstring states there is no field truncation.
2. **`amends`** (scope-change → decision | adr) via **migration 004**, with merge
   semantics taught in the advisory note, the obligations row, register-liveness,
   and every reference (DEC-: upsert; ADR-: supersede; Merged LAST, after re-read).
3. **`package_verify(name?, record?)`** — per-file byte-equality, foreign files,
   loadable-as-finding (store.load now locates bad JSON), memory-vs-disk when open,
   a sha256 digest; `record=true` appends the server-only `integrity-verified` row
   whose text states the digest-moves-on-record rule.
4. **`narrated_ids`** in `audit_evidence`.
5. **Server-only journal kinds refused** from `progress_update` (the field data held
   five agent-written `lesson-confirmed` rows).
6. **The `.converted` leftover**: the v3 converter deletes its source (the backup
   copy is the trail); `package_migrate` relocates an old one per file (move /
   remove-if-identical / refuse-if-different — the DA round caught that ACMP's
   backup already held a byte-identical copy, and that the registry-current refusal
   would have made the remedy a no-op); the advisor's done-check added the v3→v4
   confirm path (a stale `.converted` removed in the SAME run — its backup copy is
   taken first — never a second migrate).
7. **`lessons-note-budget`** — entities = the rows rendering past position 20 in the
   note's own order (one row helper shared with the note).
8. **Doctrine**: the note's C31 sentence carries LL-061 (recording flushes after the
   commit — porcelain check before any branch op); orient-resume classifies
   unreferenced commits by path (LL-004); defect-triage sends rulings to `DEC-`
   rows (LL-040); register-liveness step 8 sets Merged last (LL-042) and gains the
   note-budget step; integrity-check opens with `package_verify` and reads through
   the tool; onboarding/kickoff teach paging; the prompts README's standing rules.
9. Docs swept end to end on the maintainer's words (references, templates incl. the
   lint-11 `amends` needle, both READMEs, SKILL.md, CANONICAL.md's verify section,
   SECURITY.md, docs/architecture + entities + methodology + workflow, CONTRIBUTING,
   the lab README + scenario beat 12, the evals README + three fixture assertions);
   the advisor's done-check closed the last `amends`-less SC-flow teachings
   (drift-register, progress-sync, replan-deferred — three more roster appends —
   the follow-up template, the catalog's drift bullet, the entities.md sequence
   diagram) and confirmed the HTML viewer carries no relation vocabulary of its own.

## Verification

check.py green end-to-end (120 contract tests incl. the paging walk over mixed-width
ids, ids/search/refusals, narrated_ids, amends typing, the package_verify battery,
the note-budget rule with 25 pinned rows, the relocation cases on both migrate
paths, the server-only
refusals; 7 migration tests incl. 004; the viewer suite; all lints incl. the new
needle, the roster appends, the stamps; the canonical round-trip; the evals with the
beat-12 fixture). `--selftest` lists 17 tools. The ACMP shape re-proven in-test: a
mixed-width family paged at limit=1 without gaps or duplicates; an SC amending a DEC
typed and a DEC→SC / SC→SL refused; a registry-current store relocating an identical
`.converted` by removal.

## The lab's beat 12 (real agent, `plans/evidence/lab-continuation-report-2026-09-06.md`)

Every ✔ observed, none missed; `gate_run` ready; all 19 fixture assertions green
(the three new ones included); the fixture byte-canonical by its own `verify`. The
agent's findings, triaged: (1) the `lessons-note-budget` note read as false on a
PASS ("renders 0 lesson line(s) — past the ceiling") — FIXED in-release (the
past-the-ceiling clause is composed only when rows exceed it); (2) the `amends`
refusal is two-layered (batch line + per-item cause) — the existing batch contract,
kept; (3) the scenario quoted a substring of the refusal — the scenario now quotes
the real text; (4) nine of the fixture's stock prompts were STALE-STOCK — refreshed
by a scripted `handoff_emit(refresh_stock=true)` after the beat (the classifier
worked as designed); (5) `.mcp.json` is a dotfile — noted; (6) `OQ-001` trips
`open-questions-overdue` by calendar — named in the scenario's pass bar; (7)
everything else exactly as documented (DEC- full-row upsert accepted, paging order ==
cut order, `ids` in id order, the lock released after every script).

## Left open

Tamper-evidence proper (a hash chain, signatures, an external anchor) — recorded in
plans/README future options. ACMP-side: upgrade → `DW-100` unblocks (slate
generators on `ids`/`after_id`); retype the three SC→ruling `relates_to` edges to
`amends`; `package_migrate` relocates the leftover; `package_verify(record=true)` on
the operator's words; the note-budget advisory fires on 48 pinned lessons — the
promotion ceremony or unpinning answers it; the customized `orient-resume` /
`integrity-check` copies need a hand-merge of this release's edits.
