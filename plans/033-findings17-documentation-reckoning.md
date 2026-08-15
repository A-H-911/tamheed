# Plan 033 (B29): findings_17 + the documentation reckoning — v4.2.0

## Status

**DONE (2026-08-15)** — all seven phases executed, `python check.py` fully green with the
four new/extended lints, `--selftest` green. Version stamped **v4.2.0** (MINOR — behavior
fixes + lints + documentation re-baseline; no schema change). *Release (push + GitHub
release) happens only on the maintainer's explicit words — this line records execution,
not publication.*

## What this was

Three streams converged at plan review (maintainer, 2026-08-15):

1. **findings_17** (evidence **C38**, `plans/evidence/acmp-field-report-17-2026-08-15.md`)
   — the ACMP v3→v4.1.0 migration acceptance. The migration was clean first-try and the
   plan-032 refresh design was silently field-proven (13/16 stock byte-current, 3
   customized correctly untouched). Two tamheed findings: the `open-questions-resolved`
   rule couldn't discriminate answered-but-unattributed rows (72 ambers, ~1 real), and
   the migrator silently dropped six milestone statuses that every other lossy change
   stashed. One mapping gap: bare `H`/`M`/`L` letters unknown to the risk-scale
   normalizer. One doctrine line adopted: repair from `data/*.jsonl`, never from
   `entity_query` output (C1).
2. **The maintainer-ordered full documentation audit** — the ExitPlanMode rejection
   ordered a review of every markdown file at every level of the repo. Three parallel
   audit agents over 100+ files found the root cause: the unlinted zone (references/,
   templates/, docs/, root files) — where the half-executed `schemas/` deletion (claimed
   Removed in 4.0.0, still on disk), a wholly-v1 package README template, a retired
   migration runbook, a dead migrate UX in SKILL.md, and ~30 stale claims survived.
   Headline duplicate: `entity-guide.md` overlapped the artifact catalog wholesale.
3. **The Mermaid delivery gap** — the seven v4 diagrams existed in `docs/entities.md`
   but with ZERO inbound links, three sequence diagrams carrying `;` in message/Note
   text (lexer-breaking), and no diagrams at all in workflow/methodology.

Two interview rounds locked the forks (merge entity-guide into the catalog; delete
examples/, schemas/, the runbook; trim assets/README; write ADR-0002; 4.2.0 MINOR; full
plans/README index rewrite — executed doctrine-bounded with the interpretation flagged),
then the devil's-advocate template refined the lints (closed-triangle gate roster;
templates/prompts excluded from the dead-path lint as generated-package content).

## What shipped

1. **findings_17 fixes**: the OQ rule discriminates (amber = no resolution AND no
   resolved_by AND non-terminal status; ACMP measure 72 → 1, pinned by an ACMP-shaped
   fixture); milestone stash parity (`v3_lifecycle_status` etc. into `custom_attributes`,
   `stashed_as` in the preview report); the letter map `h/m/l → high/medium/low`; scale
   semantics in governance.md; the repair doctrine in the catalog + prompts/README.
2. **Deletions completing the record**: `plugins/tamheed/schemas/` (the 4.0.0 execution
   miss, stated plainly in the 4.2.0 CHANGELOG entry — the 4.0.0 entry is append-only and
   was not edited), `references/migration-runbook.md` (§8 folded into server/README),
   `examples/` (41 files), `references/entity-guide.md` (merged into the catalog),
   assets/README trimmed to a caption.
3. **The merge + full sweep**: artifact-catalog.md absorbed the entity-guide (operating
   rules, ER + lifecycle diagrams, version stamp — joins lint 8); SKILL.md teaches the
   real v4 migrate UX; quality-gates.md gained G-REL + the Warn-tier label; every audited
   stale claim across references/, templates/, docs/, and root files fixed;
   package-readme.template rewritten for v4; the demo package's three project prompts
   rewritten v4-correct (canonical gate re-verified).
4. **The Mermaid delivery**: the three sequence diagrams cleared of `;`/`#` in message
   text (structural fix — the render confirmation on GitHub is an explicit maintainer
   acceptance line in the close-out); inbound links added (README, CLAUDE.md, docs
   siblings); the 22-stage flowchart + human-gate sequence added to docs/workflow.md;
   the HYP→EXP/POC→DEC→ADR chain added to docs/methodology.md; the migration-path
   diagram added to docs/migrate-from-keystone.md.
5. **The four lints (the root-cause fix)**: lint 9 extended to ALL teaching surfaces
   with a closed-triangle gate roster (every allowed name in quality-gates.md, every
   G-token in the doc in exactly one tier); lint 10 dead-path over references/SKILL/
   server-README/CANONICAL, resolving relative-to-file OR repo-root OR bundle-root
   (templates, prompts, and generated-structure.md excluded by design — they describe
   the generated package tree; the bundle-root base and the generated-structure
   exemption were added at first-run triage, when the lint's 8 initial hits split
   5 false-positive classes / 2 genuine dead paths / 1 illustrative example);
   lint 8 extended to
   five version-stamped surfaces; lint 11 template-sync (governance + naming-conventions
   template tables vs governance.md). First-run reds proved each lint bites.
6. **Records**: ADR-0002 (the v4 re-baseline, partially superseding ADR-0001 — which got
   only a status pointer); plans/README rewritten as the era-grouped program index
   (history condensed, never falsified; evidence untouched); this record; C38.

## Verification

`python check.py` green end-to-end (suites incl. the new OQ-discrimination and
stash/letter-map tests, all lints, canonical, evals); `uv run … --selftest` green;
mermaid blocks re-validated against the conservative subset (no `;`, no `#` in sequence
message/Note text); the dead-path lint green over the post-deletion tree.

## Left open (operator-side, returned in the close-out prompt)

The findings_17 §E list is ACMP's: DW-027 close, DW-026 build-or-carry, OQ-074, owners
for RISK-013…024, the A4 title recovery, the 20 unbound ACs — plus the risk-scale
recovery now that 4.2.0 ships the letter mapping, and the maintainer's GitHub
confirmation that the seven entities.md diagrams render.
