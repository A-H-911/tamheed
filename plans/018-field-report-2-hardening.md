# Plan 018 (B14): Second field report — preview honesty, viewer scale, prompt library, cutover tooling

## Status

**DONE (2026-07-22)** — five phases executed with `check.py` green at every boundary; released
as **v2.2.0**. Evidence: the second ACMP field report (successful production migration under
v2.1.0, verdict "production-quality"; archived at
`evidence/acmp-field-report-2-2026-07-22.md`), clusters **C17** (preview honesty), **C18**
(viewer scale/navigation), **C19** (cutover portability & agent-control tooling).
**Outstanding: the maintainer's ACMP re-migration on v2.2.0** (the acceptance test — the
maintainer chose tooling + re-migration over hand-fixing ACMP's agent-control files).

Maintainer decisions locked at the 2026-07-22 checkpoint: semantic status defaults **with
operator multi-select confirmation** (`status_map` param) · prompt library lives **in the
package directory** · ACMP fixed via tooling, not hand edits · emitted agent-control note
carries a full MCP tool cheat-sheet. An adversarial review pass re-verified all sub-agent
claims against source before approval (recorded in the session plan file).

## What shipped (per phase, one commit each)

1. **Migration preview honesty (C17)** — `STATUS_COERCE` semantic defaults
   (Resolved→Implemented, Open/Monitoring/Active→Approved, Closed→Obsolete) with the
   `status_coerced` ledger and the `status_map` override; title aliases never resolve to the
   id column (+ `name` alias, `title_fallbacks` ledger); ADR/EXP/POC/diagram parse failures
   fall through to the narrative catch-all; narrative front-matter preserved; per-file
   `partial_files` row counts; pre-flight reports the frozen validator's sha256+size. Golden
   regenerated in the same commit (expected deltas only: hypotheses, open_questions,
   narrative_documents). `migration-v1.md` quirks 12–15.
2. **Viewer (C18)** — sticky zero-JS TOC (the only anchors; hostile test pins "every href is
   a #fragment"); >50-row families and the all-edges dump folded behind closed `<details>`;
   `table{width:max-content;min-width:100%}` so wide tables actually scroll; freshness
   distinguishes "no v2 activity recorded yet" from real activity; migrated metadata labeled
   `(v1-manifest-derived)`.
3. **Cutover tooling (C19)** — bundle `prompts/` library (orient-resume with git-history
   cross-check, progress-sync, integrity-check, generate-report, slice-review) emitted into
   `<package>/prompts/` by migrate, adopt, AND handoff_emit (three sites — adopted packages
   have no PRM rows and must not be stranded); `handoff_emit(subdir=…)` validated; plugin-
   hosted servers omit the project `.mcp.json` entry (the old emit hard-coded the versioned
   plugin-cache path); the CLAUDE.md note is a full operating context with a tool
   cheat-sheet; `stale_references` report (file:line + suggestion; the bare word "Keystone"
   never matches — ACMP's ADR-0007 lesson); `entity_query` returns `total`; operator-facing
   strings de-jargoned.
4. **Skill/docs** — SKILL.md/modes.md migrate walkthrough (status-map confirmation);
   prompt-templates.md scenario-library section; fresh-session refresher rebuilt tool-first
   with the git cross-check (deliberate, recorded exception to the template freeze: content
   only, the mechanical v1 contract never parses template content); migrate-from-keystone.md
   §2–§5; README Usage (prompt library, MCP tools table, viewer navigation, status step).
5. **Release** — plugin.json + CHANGELOG `[2.2.0]` (version-sync lint), tag v2.2.0.

## Verification

`python check.py` green at every boundary (~135 tests incl. 16 new; 5 v1 goldens; version-sync
lint; canonical round-trip; evals). Golden diff reviewed against the expected-delta list before
regen. **Acceptance (maintainer, post-release):** re-run the ACMP migration on v2.2.0 — status
mappings presented for confirmation and landing right-side-up; phases titled from the name
column; `adrs/README.md` prose preserved; no machine-specific `.mcp.json` on the plugin host;
`tamheed-package/prompts/` emitted; `stale_references` sufficient to fix AGENTS.md/CLAUDE.md
without archaeology ("Keystone optional" untouched); the 2 MB review.html navigable.

## Rejected (do not re-audit)

Hand-editing ACMP agent-control files (maintainer decision) · `${CLAUDE_PLUGIN_ROOT}` in
emitted project configs (not guaranteed defined there; omit+note is field-proven) · viewer
pagination/virtualization (details-folding suffices; zero-JS contract) · growing the dialect
fixture with broken ADRs (forfeits its v1 exit-0 golden status) · a repo-docs prompts page
(maintainer chose package-dir emission).
