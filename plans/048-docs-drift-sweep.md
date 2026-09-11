# Plan 048: Docs drift sweep — remove the claims the code no longer backs

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` (section "Advisor audit 2026-09-10") — unless a reviewer
> dispatched you and told you they maintain the index.
>
> **Drift check (run first)**: `git diff --stat 7e3a92b..HEAD -- CLAUDE.md README.md SECURITY.md docs/entities.md docs/workflow.md docs/architecture.md docs/methodology.md docs/migrate-from-keystone.md plugins/tamheed/SKILL.md plugins/tamheed/references/modes.md plugins/tamheed/references/safeguards.md plugins/tamheed/references/adopt.md plugins/tamheed/references/generated-structure.md CHANGELOG.md`
> If any in-scope file changed since this plan was written, re-read the cited
> lines before editing; a line that no longer says what "Current state" quotes
> is a STOP condition for that item only (skip it and report), not for the plan.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none. Run **after** plan 044 if both are scheduled (044 edits
  `SECURITY.md:31`; this plan edits `SECURITY.md:27-28` — sequential avoids a merge conflict).
- **Category**: docs
- **Planned at**: commit `7e3a92b`, 2026-09-10

## Why this matters

These are documentation claims an agent or operator will act on and find false: a `--dry-run`
flag that four teaching surfaces describe as a SAVEPOINT-backed preview and that no code
implements; a README migrate example in the v1 (`--mode migrate <dir>`, `status_coerced`)
shape that v4's `package_migrate(name, confirm)` refuses; a `sources=["+issues"]` adopt
parameter that does not exist; a `handoff/` directory the handoff no longer writes; two
paths in `CLAUDE.md` (`examples/`, `references/entity-guide.md`) that do not exist; a Python
floor (`3.9+`) below the CI matrix; a stock-prompt count of 15 (there are 16); a `SECURITY.md`
path that points outside the bundle and a "no git commands at all" claim that adopt mode
contradicts. The maintainer decided (2026-09-10) that `--dry-run` is **removed from the docs**,
not implemented. Every edit here is a deletion or a one-line correction; `check.py` lint 10
(dead path references) covers the bundle files, so the executor gets a mechanical check for
most of it.

## Current state

Quote → replacement, per file. Line numbers are at commit `7e3a92b`.

1. **`CLAUDE.md`**
   - `:12-14`: *"Generated output only ever lives under `examples/`, `generated-samples/`, and
     `evals/sample-results/` (curated)"* — `examples/` does not exist (`ls examples` → no such
     directory). Drop `examples/`.
   - `:25`: *"references/ # on-demand depth: artifact-catalog, governance, workflow, entity-guide"*
     — no `entity-guide.md` exists under `plugins/tamheed/references/` (files: adopt,
     artifact-catalog, artifact-rules, clarification, extension, generated-structure, governance,
     handoff, intake, modes, prompt-templates, quality-gates, research-depth, safeguards, state,
     traceability, workflow). Replace `entity-guide` with `extension, adopt`.
   - `:34`: *"examples/  generated-samples/  tests/ # teaching material, demo package, test suites"*
     → `generated-samples/  tests/               # demo package, test suites` (keep the column
     alignment of the tree).
   - `:45`: *"Python 3.9+ for the store/tests (stdlib only); the MCP server needs 3.10+ (ASM-D)."*
     → *"Python 3.10+ (ASM-D — the MCP SDK's floor and the CI matrix floor); stdlib only."*
2. **`docs/entities.md:3-4`**: *"The compact in-bundle companion is
   `plugins/tamheed/references/entity-guide.md`"* → *"The compact in-bundle companions are
   `plugins/tamheed/references/artifact-catalog.md` (the families) and
   `plugins/tamheed/references/governance.md` (identifiers, statuses)"*.
3. **`--dry-run` removal** (maintainer decision: docs, not code). Sites:
   - `README.md:108`: delete the line
     `  --dry-run           transactional preview: report entity/gate deltas, then roll back`.
   - `README.md:215-220`: delete the paragraph *"**`--dry-run` — preview any mutating run.** …"*
     and its code block (the `--mode update … --dry-run` example) — 6 lines plus the blank
     separators.
   - `plugins/tamheed/SKILL.md:111-112`: in the Parameters sentence delete
     `; \`--dry-run\` (transactional preview: run the stage's mutations in a SAVEPOINT, report entity counts and gate deltas, roll back)`
     and end the sentence after the `--package-dir` clause with a period.
   - `plugins/tamheed/references/modes.md:19-20`: same deletion of the `--dry-run (…)` clause.
   - `plugins/tamheed/references/modes.md:51-52`: *"2. Preview to the operator: the impact set +
     what would be regenerated. With `--dry-run`, apply inside the SAVEPOINT and report gate
     deltas instead."* → *"2. Preview to the operator: the impact set + what would be regenerated."*
   - `plugins/tamheed/references/safeguards.md:23` (safeguard 16): delete the clause
     `; \`--dry-run\` previews mutations in a rolled-back SAVEPOINT` (keep the rest of the cell).
   - `docs/architecture.md:171`: *"an optional `--profile` hint, `--package-dir`, and `--dry-run`."*
     → *"an optional `--profile` hint, and `--package-dir`."*
   - `docs/methodology.md:127-128`: delete *", and `--dry-run` runs a stage's mutations inside a
     rolled-back transaction and reports the entity/gate deltas"* (rejoin the sentence).
   - `docs/methodology.md:273`: delete *", and `--dry-run` previews mutations in a rolled-back
     transaction"* (keep *"(safeguard 16)"*).
4. **`README.md:196-203`** — the v1-shaped migrate example:

   ```
   /tamheed:tamheed ./old-project/planning-package --mode migrate --package-dir ./planning

   The preview reports every judgment call before anything is written — including `status_coerced`
   (v1 status words … ), zero-family tripwires, and per-file coverage ledgers. Full runbook:
   [`docs/migrate-from-keystone.md`](docs/migrate-from-keystone.md).
   ```

   Replace the code block and paragraph with the v4 story:

   ```text
   /tamheed:tamheed ./planning/my-package --mode migrate --package-dir ./planning
   ```

   *"`package_open` refuses a pre-v4 store by version and names the tool; `package_migrate(name)`
   previews every transform (value coercions, edge retypes, dropped columns) and writes nothing;
   `package_migrate(name, confirm=true)` converts in place with the old files kept in
   `data-v3-backup/`. v1 Keystone Markdown packages take the two-step route — migrate under
   tamheed 3.2.1 first, then v3→v4 here: [`docs/migrate-from-keystone.md`](docs/migrate-from-keystone.md)."*
5. **`docs/workflow.md:199`** (stage 20 row, "Output" cell): *"`handoff/` in the target project +
   `.mcp.json` + `CLAUDE.md` note"* → *"`.mcp.json` + the `CLAUDE.md` note in the target project
   (no prompt copies — prompts stay in `<package>/prompts/`)"*.
6. **`plugins/tamheed/references/generated-structure.md:23`**: `<15 stock scenarios>.md` →
   `<16 stock scenarios>.md` (`ls plugins/tamheed/prompts/*.md | grep -vc README` → `16`). Also
   add, after the `data/` subtree (before `prompts/`), one line:
   `├── data-v3-backup/                # only after a v3→v4 package_migrate: the pre-migration data/ files`.
7. **`SECURITY.md`**
   - `:27-28`: *"the MCP server and the store execute no `git`/`gh` commands at all;
     `scripts/scratch_diff.py` is a read-only diff tool"* → *"the store and the package tools
     execute no VCS commands; the sole exception is adopt mode's read-only `git log` (list-argument
     subprocess, no shell — `plugins/tamheed/server/adopt.py`); `plugins/tamheed/scripts/scratch_diff.py`
     is a read-only diff tool"*. Verify the adopt claim first:
     `grep -n 'subprocess' plugins/tamheed/server/adopt.py` → a `subprocess.run([... "git", "log" ...])`
     call with a list argument and no `shell=True`.
   - Leave `:30-32` (the traversal bullet) to plan 044.
8. **`plugins/tamheed/references/adopt.md:46-47`**: *"**Opt-IN** (`sources=["+issues"]`; requires
   `gh` + network): GitHub issues/PRs → `OQ-`/backlog candidates. Never scanned by default."* —
   `package_adopt(source_dir, name=None, confirm=False)` has no `sources` parameter
   (`grep -n 'def package_adopt' plugins/tamheed/server/tamheed_server.py`). Replace with:
   *"**Not scanned:** GitHub issues/PRs. Adopt reads the working tree only; an opt-in issues source
   is a recorded future option, not a parameter."* (No path to `plans/` — the bundle never
   links out; that is a CLAUDE.md invariant lint 10 cannot see.)
9. **`docs/migrate-from-keystone.md`** — sections 3–7 describe `package_migrate(source_dir, …)`,
   `status_map`, `patch=<file>`, `allow_zero`: these are tamheed **3.2.1**'s signatures (the doc's
   own §3 says the mapping contract "shipped inside tamheed 3.2.1"), but §2 installs the *current*
   plugin, whose `package_migrate(name, confirm)` refuses v1 input. Add, at the top of §3 (after
   the heading at :51), a boxed note:

   > **Run §§3–7 with tamheed 3.2.1, not the current plugin.** The tool signatures below
   > (`package_migrate(source_dir, …)`, `status_map`, `patch`, `allow_zero`) are 3.2.1's; the v4
   > server's `package_migrate(name, confirm)` refuses v1 input. Check out the tag and launch that
   > server against your package root: `git -C <tamheed-checkout> checkout v3.2.1`, then
   > `uv run <tamheed-checkout>/plugins/tamheed/server/tamheed_server.py --package-dir <root>`
   > (or point `.mcp.json` at it). When §7 is done, return to the current plugin and run the
   > v3→v4 `package_migrate(name)` preview + `confirm=true`.

   The tag exists (`git tag | grep v3.2.1` → `v3.2.1`). Do not rewrite the signatures.
10. **`CHANGELOG.md`** under `## [Unreleased]` → `### Changed` (docs only): one bullet.

### Release discipline (this repo's `check.py` will fail you otherwise)

- Do NOT bump `plugins/tamheed/.claude-plugin/plugin.json` (lint 4).
- `README.md` and `plugins/tamheed/SKILL.md` are version-stamped (lint 8): edit only the lines
  named above; do not touch the version string.
- Lint 10 checks every backticked path token and markdown link in
  `plugins/tamheed/references/*.md` (except `generated-structure.md`), `SKILL.md`,
  `server/README.md`, `db/CANONICAL.md` resolves — every path you write into those files must
  exist (`plugins/tamheed/server/adopt.py` does; verify any other with `ls`).
- Lint 9b (teaching-surface vocabulary) rejects prose in the bundle that names a gate/tool the
  engine lacks — deletions cannot trip it; the new adopt.md sentence names no tool.
- Do NOT touch `plugins/tamheed/prompts/*.md`; do NOT touch `plugins/tamheed/templates/**`
  (their paths describe the generated package — not this repo).
- `docs/**` is not linted; read your edits back.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Lints only | `python check.py lint` | every `lint:` line prints; no `FAIL` |
| Full gate | `python check.py` | `ALL CHECKS PASSED` |
| Leftover dry-run claims | `grep -rn -i 'dry-run' README.md docs plugins/tamheed --include='*.md' \| grep -v 'docs/history'` | no matches |
| Leftover dead paths | `grep -rn 'entity-guide\|examples/' CLAUDE.md docs/entities.md` | no matches |
| Prompt count | `ls plugins/tamheed/prompts/*.md \| grep -vc README` | `16` |

## Scope

**In scope** (the only files you should modify): exactly the files listed in "Current state"
plus `plans/README.md` (your status row).

**Out of scope** (do NOT touch, even though they look related):
- `docs/history/**`, `plans/evidence/**`, released CHANGELOG entries — frozen.
- `plugins/tamheed/templates/**`, `plugins/tamheed/prompts/**`.
- `SECURITY.md:30-32` — plan 044.
- Any code. If a doc claim turns out to be *true* on re-read, skip that item and say so.
- Implementing `--dry-run` — decided against; recorded as a future option in the index.

## Git workflow

- `main` or a local branch `advisor/048-docs-sweep`; one commit:
  `docs: remove --dry-run and other claims the code no longer backs (plan 048)`.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Bundle files first (they are linted)

Apply items 3 (SKILL.md, modes.md, safeguards.md), 6 (generated-structure.md), 8 (adopt.md).

**Verify**: `python check.py lint` → ends without `FAIL`; the line
`lint: no dead path references across N bundle prose files` prints.

### Step 2: Root and docs files

Apply items 1, 2, 3 (README.md, architecture.md, methodology.md), 4, 5, 7, 9.

**Verify**: the three `grep` commands in the table return no matches / the expected count;
`git diff --stat` lists only in-scope files.

### Step 3: CHANGELOG

Under `## [Unreleased]` → `### Changed`:

```markdown
- Docs: removed the `--dry-run` flag from every surface that described it (never implemented;
  decided 2026-09-10 to drop rather than build); README's migrate example now shows the v4
  `package_migrate(name)` preview/confirm flow; `CLAUDE.md` no longer names `examples/` or
  `references/entity-guide.md`; stage 20 no longer claims a `handoff/` directory; the stock
  prompt count is 16; `SECURITY.md` names adopt's read-only `git log` and the bundled
  `scripts/scratch_diff.py` path; `adopt.md` no longer documents a `sources` parameter; the
  Keystone runbook says which steps run under tamheed 3.2.1 (advisor plan 048).
```

**Verify**: `python check.py` → `ALL CHECKS PASSED`.

## Test plan

No code tests. Mechanical checks: lint 10 for the bundle, the `grep` table for the rest, and a
read-through of every edited paragraph for grammar after the deletions (rejoined sentences in
`methodology.md:127` and `safeguards.md:23` are the two most likely to be left dangling).

## Done criteria

- [ ] `grep -rn -i 'dry-run' README.md docs plugins/tamheed --include='*.md' | grep -v docs/history` → no output
- [ ] `grep -rn 'entity-guide' CLAUDE.md docs/entities.md` → no output; `grep -n 'examples/' CLAUDE.md` → no output
- [ ] `grep -n '15 stock' plugins/tamheed/references/generated-structure.md` → no output; `grep -c 'data-v3-backup' plugins/tamheed/references/generated-structure.md` → `1`
- [ ] `grep -n 'sources=' plugins/tamheed/references/adopt.md` → no output
- [ ] `grep -n 'status_coerced' README.md` → no output
- [ ] `grep -n 'handoff/' docs/workflow.md` → no output
- [ ] `grep -n 'tamheed 3.2.1, not the current plugin' docs/migrate-from-keystone.md` → one hit
- [ ] `python check.py` → `ALL CHECKS PASSED`
- [ ] `git status` shows only in-scope files
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:

- Lint 10 reports a dead reference you did not introduce — report it (it means the file drifted).
- `grep -n 'subprocess' plugins/tamheed/server/adopt.py` shows `shell=True` or a string command —
  then the SECURITY.md sentence in item 7 would be false; report instead of writing it.
- `grep -rn 'dry_run\|dry-run' plugins/tamheed/server/*.py` returns a hit — then `--dry-run` *is*
  implemented somewhere and the maintainer's premise is wrong; stop before deleting any docs.
- Any quoted line in "Current state" does not appear at or near the cited line — skip that item
  and list it in your report.

## Maintenance notes

- The five version-stamped files + lint 10 catch *paths*; nothing catches *behavioural* claims
  in `README.md`/`docs/**`. Reviewers of future releases should grep the docs for each
  parameter and directory the release note mentions.
- If `--dry-run` is ever built, restore the wording from this commit's diff (it was accurate
  as a spec) and add the SAVEPOINT test alongside plan 043's rollback test.
