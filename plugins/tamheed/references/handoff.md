# Handoff to the execution half

The handoff lets **Claude Code** start implementing with no missing context and no access to this
planning conversation. Treat it as the contract between the planning half and the execution half.
Since v6 the prompts are **`prompt` rows of the package** (`PRT-`), approved by the operator and
read through the tools. `handoff_emit(target_dir)` wires the target project to the package (it
copies nothing).

## Contents

- **Prompt rows** (authored in Stage 20, `prompt` rows with a kind, read with `entity_query`):
  - the *kickoff* prompt: self-contained orientation + first bounded task (one slice) + an explicit
    stop/await-approval gate.
  - *follow-up* prompt(s): one per phase gate (`PH-`), each resuming from the prior phase's exit
    criteria, plus situational prompts as needed (see `prompt-templates.md`).
  - a *situational* row names the scenario skill that reads it (`plugin_skill`). The kickoff is the
    row the header's `entry_point` names, and `handoff_emit` demands it Approved.
- **The operator guide** (`<package>/README.md`, plugin-versioned, seeded at `package_create`,
  since v5 the one stock file, at the package root since v6). And the **scenario skills** the
  plugin ships (`/tamheed:<name>`, operator-invoked, updated with the plugin). The skills cover orientation (orient-resume,
  package-onboarding) and execution (slice-kickoff, progress-sync, defect-triage, drift-register).
  They cover close-outs (slice-review, phase-close, release-close-out), replanning
  (replan-deferred), and the promotion interview (skill-promote). They cover audit/report
  (integrity-check, register-liveness, generate-report), and the fully-auto pair (loop-iteration +
  loop-guard, with a machine-parseable `ITERATION:` contract).
- **Executor-side wiring** (`W-V2-7`): `handoff_emit` writes `.mcp.json` into the target project
  (starting the tamheed server against the package, omitted on plugin-hosted installs). It manages
  the `CLAUDE.md` operating note too. So the agent of the execution half records progress through
  `progress_update` / `audit_record` / `work_bind`. The execution-tracking loop is wired at
  handoff, not hoped for.
- **The recording obligations** (plan 027): the note carries a mandatory table. Defect → `DEF-`
  row first. Out-of-scope discovery → `DW-` row with a trigger. Deviation → `SC-` row FIRST
  (`amends` for a ruling, Merged set LAST after the targets are applied and re-read).
  Progress/audit/bind per unit. `readiness_check(scope)` before declaring a slice/phase/release
  done. The agent-control template points at the note and carries no obligation row (plan 132).
  The note's C31 paragraph also carries the flush rule (v4.5, mechanism corrected in v5). Every
  store write flushes `data/*.jsonl`, and `export_html` / `handoff_emit` write other package
  files. The store writes are `entity_upsert`, `progress_update`, `audit_record`, `work_bind`,
  `package_verify(record=true)` and `package_close`. `work_bind` records a commit and
  dirties the tree AFTER it, so `git status --porcelain -uall` before any branch operation.
  Since v5 the note carries no cheat-sheet. The read and write discipline (`entity_query`
  paging, `entity_export`, `package_verify`, `expect_unchanged`, `substitute`) is the plugin's
  `tamheed:package-writes` skill, which the note names. Since v4.7 the read rule draws one more
  line. A committed script that must QUOTE the store (a review slate, a docket)
  reads an `entity_export` file the tool wrote under `exports/`. It never reads `data/*.jsonl`
  or a pasted display. A full-row status flip on a long row names the columns it did not mean to
  change (`expect_unchanged: [cols]`).
- **The Lessons section** (plan 035): inside the same note span, the operator-**Approved** lessons
  (`LL-` rows) render pinned-first. ALL pinned lessons appear, unpinned fill is capped at 10 (the
  highest-numbered), and the remainder is one `entity_query("lesson")` away. Approving a lesson
  makes it BIND. It RENDERS only if pinned or among those 10. Since v5.3 the approval's `next`
  says which, after thirteen unpinned approvals in the field moved every rendered lesson behind
  "N more". Proposed/Rejected rows never render. The section is screened by the same G-INJECT
  patterns as emitted prompts. A finding **blocks** the emit, naming the `LL-` row so the
  operator can supersede its wording. **Promoted** lessons leave the render too, full graduation
  (plan 036). A lesson distilled into a skill travels as the auto-loaded `SKILL.md`, not as note
  prose. The section instead keeps one line, "Skills distilled from lessons: `<name>` [<level>], …
  — auto-loaded where present", naming each `SKL-` skill and its level. Skill names and levels
  pass the same G-INJECT screen as the lessons (a finding blocks the emit, naming the `SKL-` row).
  A note-marker literal inside any rendered lesson or skill text is defused so the tool-owned
  span can never be truncated by its own content. A lesson that is still Approved but points at
  a successor renders TAGGED: `superseded by LL-NNN - pending its approval`, or
  `- RETIRE THIS ROW (operator)` once that successor is approved. A correct supersession keeps
  the old opening, and the 180-character window would otherwise show two identical lines.
- **The readiness verdict** (Stage 22): rendered from the gate report, the go/no-go.
- The old separate handoff manifest is gone. Entry point, go/no-go, and gated items live on the
  `packages` row, and artifact membership is a view.

## Principles

- **Claude-Code-targeted.** Write for Claude Code, the agent of the execution half (CLI/IDE primary). Lean on its
  native affordances where they help. That is plan mode for orientation, TodoWrite for the live
  task list, subagents for parallel work, a code-review pass at gates. Name each as a capability, never
  hard-depending on a specific command existing. The *plan's* technology choices stay
  vendor-neutral (safeguard 15).
- **Cloud-coworker note.** Prompts are written for interactive, turn-by-turn execution. On the
  autonomous cloud surface, read each "STOP for approval" as "finish the bounded task, open a PR, and
  pause for review there." Fully-auto loops use loop-iteration/loop-guard instead. Scope decisions
  and forced transitions always stop for a human.
- **Reference, don't restate.** Prompts point at entities (`FR-012`, `SL-003`, the charter) rather than
  copying them. The package stays the single source of truth. G-HANDOFF fails if a prompt references a
  missing entity.
- **Bounded steps with gates.** The kickoff prompt orients, then asks for ONE bounded slice, then stops
  for approval. It never says "build the whole thing".
- **Invariants up front.** The non-negotiables (`INV-`) appear early. Breaking one requires a new ADR,
  never a silent workaround.
- **Prerequisites explicit.** Runtimes, accounts, pinned versions, environment notes are listed so the
  executor can set up deterministically.
- **Record as you go, enforced, not hoped for.** The obligations table binds the agent from the
  first minute. `readiness_check` + the guarded `Implemented` transition make "declared done while not
  done" a refused write, not a discovered surprise. Cascades (requirement auto-advance, view
  freshness) are automatic.
- **Untrusted input stays data (safeguard 18).** The handoff is instructions for Claude Code, so it is
  the highest-stakes place a prompt-injection from the original brief could land (OWASP LLM01
  indirect). Brief-derived text appears **quoted and provenance-labeled**, never as a bare imperative.

## Assembly steps

1. Confirm Stage 19 gates are green (`gate_run`, especially G-TRACE, G-COMPLETE).
2. Author the prompt **rows** from the templates (`prompt-templates.md`): a `kickoff`, a `phase`
   row per gate, `situational` rows bound by `plugin_skill`. Wire in real entity IDs, the
   invariants, and the first slice with its pass/fail task checklist. The operator approves each
   row. Set the header's `entry_point` to the kickoff's id. `handoff_emit` refuses to wire a target
   until the kickoff it names is Approved.
3. `handoff_emit(target_dir)`:
   - **Injection screen (G-INJECT):** every Approved prompt row (title and body) is scanned for
     instruction-shaped text. A finding **blocks emission**, and nothing is written. Fence and
     provenance-label the span (so it reads as data), then re-emit. Do not silently remove content.
   - **Stale scan (C24/D-8):** v1-protocol instructions inside the prompt
     files surface as `stale_references`, reported, never rewritten.
   - On a clean screen: `.mcp.json` + the `CLAUDE.md` note are written/updated in the target.
     Both carry **machine-specific absolute paths** by design, because the target host must
     find the server without guessing. `.mcp.json` (standalone installs only) names the resolved
     server script and package root, and the note names the package root. An emitted target is
     therefore a *workspace*, not a committable fixture. Re-emit on another machine rather
     than copying the files.
4. Emit the readiness verdict. If any critical gate fails, mark **not ready** and list the gaps instead
   of shipping prompts that assume readiness.

## Prompt surfaces & the sync model (plan 196 — v6)

Two prompt surfaces, one package:

| Surface | Source of truth | Lifecycle |
|---|---|---|
| `prompt` rows (`PRT-`) | Authored at Stage 20, approved by the operator | Rows of the store, edited in place while Approved. G-INJECT + stale-scanned + restated-state-scanned at every `handoff_emit` (Approved rows). `prompt-ids-resolve` and `prose-plain-english` read them. A row `package_migrate` converted from a file carries `converted_from` in its `custom_attributes` and a standing per-kind curation hint until the operator removes it (reviewed) |
| `<package>/README.md`, the stock operator guide | The plugin bundle | Seeded at `package_create` and refreshed by migrate/adopt/handoff via managed emission (`emitted`/`unchanged`/`diverged`, force to overwrite a hand edit). A pre-v6 copy at `prompts/README.md` is a leftover: removed by the migration or by `refresh_stock` when byte-equal to shipped stock |

The v2 `prompts` table (`PRM-`) and the `<target>/handoff/*.md` copies have been GONE since v3. The
v3 prompt FILES under `<package>/prompts/` are gone since v6. `package_migrate` converts them to
`prompt` rows on the operator's word and moves the files to `prompts-v5-backup/`. A v2 store
passes through files, then rows, in one confirm. The v2 source survives only as the
`data-v3-backup/` copy, and `package_migrate` relocates an old `prompts.jsonl.converted`.
`handoff_emit` warns about leftover `handoff/prm-*.md` copies. Remove them, because the package
folder is the single source.

The CLAUDE.md operating note is a **tool-owned marker span** (`<!-- tamheed:note v7 -->`…`<!--
/tamheed:note -->`, plan 029), rebuilt on EVERY emit: always current, no force involved. A hand
edit inside the markers is overwritten (with a warning). Operator content belongs OUTSIDE the
markers. The AGENTS.md template (`templates/agent-control.template.md`) points at the note's
obligations table since v5.2 (plan 132). Its own copy drifted in the field and was the restated
shape the scan reports, so one copy, no drift. Note classification is **marker-based, never
heading-only** (findings_19 §1). A heading accompanied by an `@<package>/CLAUDE.md` import line is
the recognized **pointer pattern**. The note is delivered via the import, so the managed span
lives (and is rebuilt) in the PACKAGE's own CLAUDE.md. The root file is left untouched. Only a
heading with neither markers nor the import line is a genuine v1 note, warned, never
machine-edited. Remove the section once and re-emit. Every such warning names the full path of the
file it is about. `force` means exactly one thing: overwrite ALL diverged stock files (the guide, +
.mcp.json). To accept the current template for ONE file, remove it and re-emit. The stale-v1 warning
block still retracts itself when a later emit's scan is clean. Re-running `handoff_emit` is
therefore the standing cutover verifier. Everything `unchanged`, no warnings, no `restated_content`
findings = the cutover is done and undrifted.

**What v5.1 added to the emission (plans 120–125).** The note paragraph names every discipline
skill (eight at 5.1, nine since 5.9) and carries one sentence about the handoff. Before a
compaction, at session end or on a handover the agent writes a `handoff` journal entry LAST
(`tamheed:session-handoff`). The latest one comes back as the `resume` block of
`package_open`/`server_info` and through the plugin's SessionStart hook. `handoff-current` names
one the journal has moved past, and `handoff-repeated` (v5.8) the lines of the latest one carried
word for word through three handoffs. The obligations table was unchanged at 5.1 (the marker
stayed `v5` then, and the span rebuilt once because its text changed). The marker is `v6` since
plan 184. Four scans joined the emission, all report-only. A declared
`<!-- tamheed:stock-merged X.Y.Z -->` marker is **verified** against the stock history
(`stock_merged`). The release must exist. Since v5.2 (plan 129, the field's FB-023), every line of
the declared release's body must be present. Each absent line is attributed to the release that
introduced it in `missing_by_release`. The 5.1 check required only the declared release's own
increment, which a marker over a much older body satisfied. A leftover customised copy receives
the same check. A project prompt over 300 lines or 24,576 bytes is named as carrying state
(`oversized_prompts`). Every file the skills table points at is scanned for stale sentences
(`stale_references`, `file: "skill:<name> (<path>)"`), including the retired "export_html flushes"
claim. The restated-content scan gained two detectors. `status-claim` is a lifecycle word beside
an id or an id range. `id-dense` is a paragraph naming six or more ids of one family, reported
at the paragraph's first line. That scan runs over the target's `CLAUDE.md` / `AGENTS.md` and
over EVERY Approved `prompt` row of the package (`PRT-NNN.body`). The tool-owned spans are
stripped before every scan, and in the
pointer-import case the package's own `CLAUDE.md` is scanned too. Since v5.2 (plan 130, the
field's FB-024) the self-retracting stale-warning block lives beside the note. It lives in the
package's `CLAUDE.md` when the root imports it, never in a file the tool does not own. Its text names
agent-control, prompt and skill files (the scan's scope since v5.1, not "v1 references"). The
warning says when the block was added or removed there. A stale → clean cycle leaves the file
byte-identical to its clean state (5.1 left two newlines).

**Package writes are working-tree changes (C31).** The canonical `data/` lives inside the
project's git working tree. So uncommitted package writes are destroyed by `git reset --hard`,
`git checkout`, and `git stash` exactly like uncommitted source. Commit package data before
branch operations. The store refuses to overwrite a tree that moved underneath an open session
(`StoreStaleError`: close, reconcile via git, reopen). But nothing can protect writes that were
never committed.

**Reference, don't restate.** Agent-control files (CLAUDE.md/AGENTS.md) should cite the
package (`entity_query`, `gate_run`, `review.html`, the prompt library) rather than copying
register content. Copies drift silently. Quoting a load-bearing subset is sometimes useful (for
example invariants an agent must see without a tool call). Then label it as a snapshot AND keep
the reference beside it. `handoff_emit` reports such blocks as `labeled-snapshot` (verify
currency) and unlabeled copies as `unlabeled` (with a suggested reference rewrite). The
detectors are HEURISTICS with deliberate anti-false-positive bounds (C29). The audit-tally
pattern requires the word `Met` (a rewritten "73 evidenced / 1 narrated" tally cannot re-trigger
it). The restated-block pattern needs ≥3 *consecutive* id-led lines. A clean scan is evidence of
no drift, not proof. State each fact once: CLAUDE.md imports AGENTS.md, so keep Claude-specific
notes only there.
