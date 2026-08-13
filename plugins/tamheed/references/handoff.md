# Execution-agent handoff

The handoff lets **Claude Code** start implementing with no missing context and no access to this
planning conversation. Treat it as the contract between planner and executor. In v3 the prompts are
**`.md` files in `<package>/prompts/`** — the operator reads the folder and picks —
and `handoff_emit(target_dir)` wires the target project to the package (it copies nothing).

## Contents

- **Prompt files** (authored in Stage 20, plain `.md` in `<package>/prompts/`):
  - the *kickoff* prompt — self-contained orientation + first bounded task (one slice) + an explicit
    stop/await-approval gate;
  - *follow-up* prompt(s) — one per phase gate (`PH-`), each resuming from the prior phase's exit
    criteria, plus situational prompts as needed (see `prompt-templates.md`);
  - the **stock scenario library** (14 files, plugin-versioned, seeded at `package_create`):
    orientation (orient-resume, package-onboarding), execution (slice-kickoff, progress-sync,
    defect-triage, drift-register), close-outs (slice-review, phase-close, release-close-out),
    replanning (replan-deferred), audit/report (integrity-check, generate-report), and the
    fully-auto pair (loop-iteration + loop-guard, with a machine-parseable `ITERATION:` contract).
- **Executor-side wiring** (`W-V2-7`): `handoff_emit` writes `.mcp.json` into the target project
  (launching the tamheed server against the package; omitted on plugin-hosted installs) and manages
  the `CLAUDE.md` operating note, so the executing agent records progress through
  `progress_update` / `audit_record` / `work_bind` — the execution-tracking loop is wired at
  handoff, not hoped for.
- **The recording obligations** (plan 027): the note carries a mandatory table — defect → `DEF-`
  row first; out-of-scope discovery → `DW-` row with a trigger; deviation → `SC-` row FIRST;
  progress/audit/bind per unit; `readiness_check(scope)` before declaring a slice/phase/release
  done. The same table lives verbatim in the agent-control template.
- **The readiness verdict** (Stage 22) — rendered from the gate report; the go/no-go.
- The old separate handoff manifest is gone: entry point, go/no-go, and gated items live on the
  `packages` row; artifact membership is a view.

## Principles

- **Claude-Code-targeted.** Write for Claude Code as the executor (CLI/IDE primary). Lean on its native
  affordances where they help — plan mode for orientation, TodoWrite for the live task list, subagents
  for parallel work, a code-review pass at gates — naming each as a capability, never hard-depending on
  a specific command existing. The *plan's* technology choices stay vendor-neutral (safeguard 15).
- **Cloud-coworker note.** Prompts are written for interactive, turn-by-turn execution. On the
  autonomous cloud surface, read each "STOP for approval" as "finish the bounded task, open a PR, and
  pause for review there." Fully-auto loops use loop-iteration/loop-guard instead — scope decisions
  and forced transitions always stop for a human.
- **Reference, don't restate.** Prompts point at entities (`FR-012`, `SL-003`, the charter) rather than
  copying them; the package stays the single source of truth. G-HANDOFF fails if a prompt references a
  missing entity.
- **Bounded steps with gates.** The kickoff prompt orients, then asks for ONE bounded slice, then stops
  for approval — it never says "build the whole thing".
- **Invariants up front.** The non-negotiables (`INV-`) appear early; breaking one requires a new ADR,
  never a silent workaround.
- **Prerequisites explicit.** Runtimes, accounts, pinned versions, environment notes — listed so the
  executor can set up deterministically.
- **Record as you go — enforced, not hoped for.** The obligations table binds the executor from the
  first minute; `readiness_check` + the guarded `Implemented` transition make "declared done while not
  done" a refused write, not a discovered surprise. Cascades (requirement auto-advance, view
  freshness) are automatic.
- **Untrusted input stays data (safeguard 18).** The handoff is instructions for Claude Code, so it is
  the highest-stakes place a prompt-injection from the original brief could land (OWASP LLM01
  indirect). Brief-derived text appears **quoted and provenance-labeled** — never as a bare imperative.

## Assembly steps

1. Confirm Stage 19 gates are green (`gate_run` — especially G-TRACE, G-COMPLETE).
2. Author the prompt **files** in `<package>/prompts/` from the templates
   (`prompt-templates.md`), wiring in real entity IDs, the invariants, and the first slice with
   PASS/FAIL. Non-stock filenames mark them as project prompts; `handoff_emit` refuses to wire a
   target while none exist.
3. `handoff_emit(target_dir)`:
   - **Injection screen (G-INJECT):** every package prompt file (project AND stock) is scanned for
     instruction-shaped text; a finding **blocks emission** — nothing is written. Fence and
     provenance-label the span (so it reads as data), then re-emit. Do not silently delete content.
   - **Stale scan (C24/D-8):** v1-protocol instructions and dead relative links inside the prompt
     files surface as `stale_references` — reported, never rewritten.
   - On a clean screen: `.mcp.json` + the `CLAUDE.md` note are written/updated in the target.
4. Emit the readiness verdict; if any critical gate fails, mark **not ready** and list the gaps instead
   of shipping prompts that assume readiness.

## Prompt surfaces & the sync model (plan 027 — v3)

Two prompt surfaces, one folder:

| Surface | Source of truth | Lifecycle |
|---|---|---|
| `<package>/prompts/` project files | Authored at Stage 20 (any non-stock filename) | Plain files, operator-owned; G-INJECT + stale-scanned + restated-state-scanned at every `handoff_emit`; legacy `PRM-` rows were converted here once at first v3 `package_open` — converted files (provenance header) get a standing per-kind curation hint until the operator reviews them (remove the header = reviewed); the folder's `README.md` is the operator guide |
| `<package>/prompts/` stock library | The plugin bundle | Seeded at `package_create` and refreshed by migrate/adopt/handoff via managed emission (`emitted`/`unchanged`/`diverged`, force to overwrite a hand edit) |

The v2 `prompts` table and the `<target>/handoff/*.md` copies are GONE (migration 003): opening a
v2 package converts its `data/prompts.jsonl` once (source kept as `prompts.jsonl.converted`), and
`handoff_emit` warns about leftover `handoff/prm-*.md` copies — delete them; the package folder is
the single source.

The CLAUDE.md operating note is a **tool-owned marker span** (`<!-- tamheed:note v2 -->…<!--
/tamheed:note -->`, plan 029): rebuilt on EVERY emit — always current, no force involved. A hand
edit inside the markers is overwritten (with a warning); operator content belongs OUTSIDE the
markers — the AGENTS.md template carries the same obligations table for project customization. A
v1 note (heading, no markers) is warned and never machine-edited — delete the section once and
re-emit. `force` means exactly one thing: overwrite ALL diverged stock prompt files (+ .mcp.json);
to accept the current template for ONE file, delete it and re-emit. The stale-v1 warning block
still retracts itself when a later emit's scan is clean. Re-running `handoff_emit` is therefore the standing cutover verifier:
everything `unchanged`, no warnings, no `restated_content` findings = the cutover is done and
undrifted.

**Package writes are working-tree changes (C31).** The canonical `data/` lives inside the
project's git working tree, so uncommitted package writes are destroyed by
`git reset --hard`, `git checkout`, and `git stash` exactly like uncommitted source —
commit package data before branch operations. The store refuses to overwrite a tree that
moved underneath an open session (`StoreStaleError`: close, reconcile via git, reopen),
but nothing can protect writes that were never committed.

**Reference, don't restate.** Agent-control files (CLAUDE.md/AGENTS.md) should cite the
package (`entity_query`, `gate_run`, `review.html`, the prompt library) rather than copying
register content — copies drift silently. When quoting a load-bearing subset is genuinely
useful (e.g. invariants an agent must see without a tool call), label it as a snapshot AND
keep the reference beside it; `handoff_emit` reports such blocks as `labeled-snapshot`
(verify currency) and unlabeled copies as `unlabeled` (with a suggested reference rewrite).
The detectors are HEURISTICS with deliberate anti-false-positive bounds (C29): the
audit-tally pattern requires the word `Met` (a rewritten "73 evidenced / 1 narrated" tally
cannot re-trigger it) and the restated-block pattern needs ≥3 *consecutive* id-led lines —
a clean scan is evidence of no drift, not proof.
State each fact once: CLAUDE.md imports AGENTS.md — keep Claude-specific notes only there.
