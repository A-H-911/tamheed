# Critical Review & Readiness Record

Status: Complete · 2026-06-17 · Verdict: **Execution-ready (v0.1)**

This records the critical review the brief required before finalizing the design ("review it for excessive
complexity, missing controls, weak handoff mechanisms, unnecessary documentation, logic duplicated in the
slash command, and unnecessary coupling…"). Review was done two ways: an **adversarial read** of the whole
package by an independent reviewer, and **mechanical checks** (the bundled validator + its test suite, schema
parsing, a scan for host-domain references, and command-size/coupling checks).

## Checklist verdicts

| # | Concern | Verdict | Notes |
|---|---|---|---|
| 1 | Excessive complexity | OK | SKILL.md is lean with progressive-disclosure references; nothing over-built. Generated package collapses to a minimal set for small projects (see example 01). |
| 2 | Missing controls | OK | 9 operating principles + 15 quality gates + a runnable validator. Two real gaps were found and closed (below). |
| 3 | Weak handoff | OK | Handoff prompts are agent-neutral, bounded, gated, and reference real artifacts; G-HANDOFF enforces it. Traced one requirement end-to-end in the sample (FR-004 → ADR-0002 → WBS-3.2 → TEST-002 → AC-002 → INV-002) — coherent. |
| 4 | Unnecessary / duplicated documentation | OK (after fix) | Repo-root specs reference the skill rather than copy it. One verbatim duplication (entry-point contract in ARCHITECTURE.md) was replaced with a pointer. |
| 5 | Logic duplicated in the slash command | OK | `commands/keystone.md` is 56 lines: input normalization, flag-syntax validation, mode pass-through, skill invocation, output routing, help. No methodology. (G-CMD-THIN.) |
| 6 | Coupling (agent / tool / tech / GitHub) | OK | Methodology is stack-agnostic; handoff is agent-neutral; repo bootstrap is provider-neutral (local `git` always works; remote/`gh` is opt-in behind `--create-remote`). Minor cosmetic "GitHub" wording in help text noted, not blocking. |

## Findings and resolutions

**MAJOR-1 — the showcase generated sample failed its own validator while its readiness report claimed it
passed** (a self-inflicted violation of safeguard 7, "verify before you claim"). Causes: the validator only
recognized identifiers defined in tables/front-matter, so the sample's heading- and bold-list-defined
`WBS-`/`PH-` items read as dangling; the WBS pattern forbade group ids like `WBS-1`; and a section whose only
content was a file-tree code block read as "empty".
**Resolved:** the validator now recognizes IDs defined in headings and bold list leaders (as reference-
resolving "weak" definitions that don't create false duplicates), accepts the `WBS-N[.N[.N]]` group form
(governance.md updated to match), and treats a fenced code block as section content. The sample now passes
all five critical gates **genuinely**; its readiness report and manifest are accurate. The fix made the tool
match the documented authoring style rather than weakening any check — the invalid fixture still fails.

**MAJOR-2 — `ARTIFACT-CATALOG.md` cited templates/schemas that don't exist or were misnamed** (e.g.
`charter.template.md` vs the real `project-charter.template.md`; `requirements.schema.json` /
`registers.schema.json` vs the per-entity schema files). The same bad names had leaked into
`skill/references/workflow.md` and `schemas/README.md`.
**Resolved:** every cited `*.template.md` / `*.schema.json` token now names a file that exists; artifacts
with no dedicated template/schema honestly show `—` (anti-bloat: rows kept, fictitious file refs removed).

**MINOR — addressed:** sample `review-prompts.md` no longer links into Keystone internals (now
self-contained); ARCHITECTURE.md entry-point contract de-duplicated to a pointer.
**MINOR — accepted (not blocking):** the operating principles appear in SKILL.md (front door) and
safeguards.md (canonical) and are re-narrated in METHODOLOGY.md for a different audience — both point back,
acceptable; "GitHub" wording in two help strings is cosmetic.

## Final mechanical status

- `python tests/validate_package.py generated-samples/support-triage-agent` → **OK — no critical gate
  failures** (G-IDS, G-DEC-STATUS, G-REQ-SRC, G-COMPLETE, G-TRACE all pass).
- `python tests/test_validate_package.py` → **18/18 OK**. Fixtures: valid passes (exit 0), invalid fails
  (exit 1) with all seeded defects detected.
- All 20 JSON Schemas parse and meta-validate (draft 2020-12); cross-`$ref`s resolve.
- Repo bootstrap: dry-run + real run verified (creates tree, baseline files, initial commit; refuses dirty
  target without `--force`; remote strictly opt-in).
- No project-specific domain references found; Keystone is fully neutral.

## Residual / known limitations

- The name **Keystone** collides with OpenStack Keystone (identity service); documented and mitigated in
  `ADR-0001` (consistent "Keystone (project inception)" framing; fallback repo slug if `keystone` is taken).
- Logos ship as **SVG only**; PNG/ICO exports are documented in `docs/assets/README.md` but not generated
  (no rasterizer needed for SVG; export commands provided).
- Two dev-scratch artifacts (`tests/_vp_probe.py`, `tests/__pycache__/`) could not be deleted from the
  build environment (read-only-delete mount); both are git-ignored and safe to remove from the host.
- This is **v0.1**: the skill methodology, schemas, templates, validator, bootstrap, and one full worked
  sample are complete; broadening the mechanical gates (G-EXEC/G-COUPLING heuristics) and adding more
  worked samples are roadmap items (`ROADMAP.md`).

**Overall:** the capability meets its MVP acceptance criteria and is ready to be lifted into its own `keystone`
repository and used. The two material defects this review found were exactly the class of problem the review
exists to catch, and both are fixed and re-verified.
