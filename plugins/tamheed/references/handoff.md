# Execution-agent handoff

The handoff lets **Claude Code** start implementing with no missing context and no access to this
planning conversation. Treat it as the contract between planner and executor. In v2 the handoff is
emitted by the `handoff_emit(target_dir)` tool from `prompt` rows — never hand-assembled.

## Contents

- **`prompt` rows** (written in Stage 20, emitted as `handoff/*.md` in the target project):
  - *initial* — self-contained orientation + first bounded task (one slice) + an explicit
    stop/await-approval gate.
  - *follow-up* — one per phase gate (`PH-`), each resuming from the prior phase's exit criteria,
    plus situational prompts (fresh-session refresher, invariant audit, bug-triage, release prep,
    deviation-ADR, status report).
  - *review* — audit work against invariants, re-run readiness, review a PR.
- **Executor-side MCP config** (`W-V2-7`): `handoff_emit` writes `.mcp.json` into the target project
  (launching the tamheed server against the package) and appends a `CLAUDE.md` note, so the executing
  agent records progress through `progress_update` / `audit_record` / `work_bind` — the
  execution-tracking loop is wired at handoff, not hoped for.
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
  pause for review there."
- **Reference, don't restate.** Prompts point at entities (`FR-012`, `SL-003`, the charter) rather than
  copying them; the package stays the single source of truth. G-HANDOFF fails if a prompt references a
  missing entity.
- **Bounded steps with gates.** The initial prompt orients, then asks for ONE bounded slice, then stops
  for approval — it never says "build the whole thing".
- **Invariants up front.** The non-negotiables (`INV-`) appear early; breaking one requires a new ADR,
  never a silent workaround.
- **Prerequisites explicit.** Runtimes, accounts, pinned versions, environment notes — listed so the
  executor can set up deterministically.
- **Track as you go.** The executing agent works acceptance-criteria-first and records at each phase
  gate: `audit_record` with evidence refs (test path, CI run id — an evidenced verdict beats a narrated
  one), `work_bind` for every commit/PR that satisfies an FR/AC/slice, `progress_update` for the
  journal. Cascades (requirement auto-advance, view freshness) are automatic.
- **Untrusted input stays data (safeguard 18).** The handoff is instructions for Claude Code, so it is
  the highest-stakes place a prompt-injection from the original brief could land (OWASP LLM01
  indirect). Brief-derived text appears **quoted and provenance-labeled** — never as a bare imperative.

## Assembly steps

1. Confirm Stage 19 gates are green (`gate_run` — especially G-TRACE, G-COMPLETE).
2. Write the `prompt` rows from the templates (`prompt-templates.md`), wiring in real entity IDs, the
   invariants, and the first slice with PASS/FAIL.
3. `handoff_emit(target_dir)`:
   - **Injection screen (G-INJECT):** every prompt is scanned for instruction-shaped text originating
     in the brief; a finding **blocks emission** — nothing is written. Fence and provenance-label the
     span (so it reads as data), then re-emit. Do not silently delete content.
   - On a clean screen: prompt files + `.mcp.json` + the `CLAUDE.md` note are written to the target.
4. Emit the readiness verdict; if any critical gate fails, mark **not ready** and list the gaps instead
   of shipping prompts that assume readiness.

## Prompt surfaces & the sync model (plan 019, C20)

Three prompt surfaces exist, with distinct lifecycles — the relationship is managed, not
implicit:

| Surface | Source of truth | Lifecycle |
|---|---|---|
| `prompts` rows (`PRM-`) | THE governed source | Written at Stage 20 from the templates; G-INJECT-screened; superseded, never edited, like any approved entity |
| `<target>/handoff/*.md` | Emission of the PRM rows | Managed: re-emit reports `unchanged` when identical, **refuses hand-edited files** (`diverged`) unless `force=true` |
| `<package>/prompts/*.md` | The plugin bundle (static scenario library) | Emitted by migrate/adopt/handoff; plugin-versioned, deliberately NOT DB-backed; same managed-emission rules |

The CLAUDE.md operating note is append-once; its stale-v1 warning lives in a marker-managed
block that retracts itself when a later emit's scan is clean. Re-running `handoff_emit` is
therefore the standing cutover verifier: everything `unchanged`, no warnings, no
`restated_content` findings = the cutover is done and undrifted.

**Reference, don't restate.** Agent-control files (CLAUDE.md/AGENTS.md) should cite the
package (`entity_query`, `gate_run`, `review.html`, the prompt library) rather than copying
register content — copies drift silently. When quoting a load-bearing subset is genuinely
useful (e.g. invariants an agent must see without a tool call), label it as a snapshot AND
keep the reference beside it; `handoff_emit` reports such blocks as `labeled-snapshot`
(verify currency) and unlabeled copies as `unlabeled` (with a suggested reference rewrite).
State each fact once: CLAUDE.md imports AGENTS.md — keep Claude-specific notes only there.
