# Plan 014 (B8): Docs, Mermaid diagrams, and the 2.0.0 changelog

> **Executor instructions**: Docs plan. Every claim written must be true of the repo AT THE TIME
> OF WRITING — verify by running the commands you document. STOP conditions are binding.
>
> **Drift check (run first)**: plans 005–013 landed. This plan runs near-last so docs describe
> reality; if a predecessor is unfinished, STOP and report which.

## Status

- **Priority**: P2
- **Effort**: M
- **Risk**: LOW
- **Depends on**: plans/005–013 (all prior v2 plans)
- **Category**: docs
- **Planned at**: commit `0e055f6`, 2026-07-11

## Why this matters

After the re-architecture, every prose surface still describes v1: Markdown packages, a bootstrap
script, seven file-scanning gates, "runs in any agent with file read/write", Python 3.9+. Leaving
them is the same "actively wrong docs" failure Track A just fixed for v1 — at larger scale. The
maintainer also explicitly requested Mermaid diagrams (flow + three-actor interaction) and the
governance-mandated MAJOR-version migration notes.

## Deliverables

1. **README.md rewritten for Tamheed v2** using plan 005 Step 6's residual-hits list as the
   worklist: what Tamheed is (DB-backed, MCP-driven planning packages), install (plugin +
   per-server MCP approval + `uv`/pip note), usage (modes incl. `update`'s three capabilities,
   `adopt`, `migrate`), the honest **requirements** block (MCP-capable host; Python per ASM-D;
   the chat-only/claude.ai path ended with v1 — say it plainly, adversarial finding W-V2-3).
   Two mandatory blocks (D-REPO revision): the **old-repo reference** — a visible "Lineage"
   section linking https://github.com/A-H-911/keystone as the frozen v1 predecessor (user
   requirement) — and the **migration runbook link** (`docs/migrate-from-keystone.md`, plan
   010's deliverable 5) for projects arriving from Keystone.
2. **Mermaid flow diagram IN the README** (replaces `docs/assets/keystone-flow.svg` + `.json` —
   delete both): the three movements (Understand → Explore → Plan & hand off) with the two human
   gates, now showing the MCP boundary (skill ⇄ tools ⇄ DB).
3. **Mermaid sequence diagram** (README or `docs/architecture.md`): three actors — **planning
   agent · human operator · executing agent** — plus the MCP server lane: brief → intake/clarify
   (operator gate) → generate (entity upserts) → gate_run → handoff (config emitted into target
   project) → executing agent records progress/audit via MCP → operator follows via HTML view →
   agile scope change loops back. This diagram is the maintainer's explicit ask; GitHub renders
   Mermaid natively.
4. **docs/ refresh**: `architecture.md` (three-tier gate mapping, server-as-capability doctrine
   from the plan-007 ADR), `methodology.md`/`workflow.md` (tool-driven stages),
   `design-decisions.md` (append: D-STORE/D-REVIEW/D-MCP superseding §2's dual-surface — mark §2
   superseded, don't delete it; supersede-don't-edit is the house rule), `install.md` (rewritten
   capability tiers).
5. **CHANGELOG.md `[2.0.0]`**: MAJOR entry — the **repo split** (Tamheed lives at
   `A-H-911/tamheed`; old install commands remain valid only for Keystone 1.0.x at the old repo;
   new install `marketplace add A-H-911/tamheed`), storage contract, MCP interaction, parameter
   changes (+removed `--no-repo`, removed bootstrap), ASM-D Python floor, migration path
   (`package_migrate`, `docs/migrate-from-keystone.md`,
   `plugins/tamheed/references/migration-v1.md`), v1 line frozen at 1.0.x. Add the **lineage
   preamble** at the top of the file (W-R4): "Entries ≤ 1.0.x record this project under its
   former name, **Keystone**, in its original repository." Follow the Keep-a-Changelog format
   already in the file. Note after this plan: plan 016 executes the keystone-side close-out.

## Commands

Every command quoted in any doc must be run once as written before committing; `python check.py`
green; the two negative/positive golden sets per plan 013.

## Scope

**In scope**: README.md, docs/** (except docs/history/**), CHANGELOG.md `[Unreleased]`→`[2.0.0]`,
deletion of the two old flow-diagram assets, logo/wordmark relabel if plan 005 deferred it.
**Out of scope**: docs/history/** and released CHANGELOG entries (immutable), SKILL.md/references
(plan 009 owns runtime docs), CONTRIBUTING.md (plan 015).

## Steps

1. Sweep: `git grep -ln "keystone" -- ':!docs/history' ':!CHANGELOG.md' ':!plans'` +
   plan 005's recorded residual list → the worklist.
2. README rewrite + Mermaid flow diagram (validate rendering with a Mermaid previewer or GitHub
   draft).
3. Sequence diagram + docs/ refresh.
4. CHANGELOG 2.0.0.
5. Final truth-pass: run every documented command; fix or remove any that fail.

**Verify**: step 5 IS the verification; plus `git grep -c "3.9" README.md docs/` → 0 (floor
updated everywhere) and `test -f docs/assets/keystone-flow.svg` → absent.

## Done criteria

- [ ] Zero stale v1 claims in README/docs (spot-check list: bootstrap, md packages, 3.9,
      chat-only tier, old install commands, old gate table)
- [ ] Both Mermaid diagrams render on GitHub
- [ ] CHANGELOG 2.0.0 complete with migration notes; `[Unreleased]` reset
- [ ] `python check.py` exit 0; `plans/README.md` updated

## STOP conditions

- A predecessor plan's feature doesn't behave as its plan claims (docs can't truthfully describe
  it) — report the discrepancy; never document the intended-but-absent behavior.

## Maintenance notes

- Mermaid sources live in the Markdown — no asset build step returns; keep it that way.
- Reviewer scrutiny: the requirements block's honesty (host support, Python floor) and that
  design-decisions §2 is superseded-not-rewritten.
