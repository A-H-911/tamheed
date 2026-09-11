# Plan 052: Bounded `pip install` everywhere, a real `uv` step in CI, a 3.13 matrix leg

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` (section "Advisor audit 2026-09-10") — unless a reviewer
> dispatched you and told you they maintain the index.
>
> **Drift check (run first)**: `git diff --stat 7e3a92b..HEAD -- .github/workflows/ci.yml CONTRIBUTING.md docs/install.md docs/migrate-from-keystone.md plugins/tamheed/server/README.md plugins/tamheed/server/tamheed_server.py plugins/tamheed/SKILL.md README.md tests/test_mcp_contract.py CHANGELOG.md`
> Plans 042, 047 and 048 touch some of these files first — expect diffs from them; compare
> the "Current state" excerpts against the live text and proceed if the quoted lines still
> exist. A quoted line that is gone is a STOP for that item only.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: **042** (CI must have produced one green run — otherwise a red matrix leg
  cannot be attributed); **047** (the smoke job's `--selftest` only proves something once it
  registers tools). Run after 048 to avoid overlapping edits in `README.md`/`SKILL.md`.
- **Category**: dx
- **Planned at**: commit `7e3a92b`, 2026-09-10

## Why this matters

Three small things that all bite fresh environments:

1. **`pip install mcp` is unbounded at seven sites** (docs and the server's own error text),
   while the PEP 723 header pins `mcp>=1.2,<2` because *"MCP SDK 2.0.0 removed
   mcp.server.fastmcp, so an unbounded resolve broke every fresh environment"* (C33). The
   documented fallback reproduces the incident the pin exists to prevent.
2. **The CI smoke job cannot fail.** It installs `uv` with `curl … | sh || true` and, if that
   fails, prints a notice and skips. Combined with plan 047 (selftest registers tools), a real
   `uv` step turns the smoke job into the one place the SDK path is exercised on every push.
3. **The matrix stops at 3.12.** Python 3.13 is current on developer machines (the maintainer
   runs 3.13.7 locally, and `python check.py` passes there — also under
   `PYTHONWARNINGS=error::DeprecationWarning`). Add the leg so CI proves it.

## Current state

- `.github/workflows/ci.yml` (after plan 042 it also carries `workflow_dispatch:`):

  ```yaml
      strategy:
        fail-fast: false
        matrix:
          os: [ubuntu-latest, windows-latest]
          python: ['3.10', '3.11', '3.12']
  ```

  and the smoke job:

  ```yaml
    server-smoke:
      # The uv/PEP 723 launch path is the documented install story — smoke it.
      # Infra-tolerant: if uv cannot be provisioned, SKIP with a visible notice;
      # never fail the pipeline on runner infrastructure.
      name: MCP server smoke (uv / PEP 723)
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4

        - name: Server selftest via uv
          shell: bash
          run: |
            if ! command -v uv >/dev/null 2>&1; then
              curl -LsSf https://astral.sh/uv/install.sh | sh || true
              export PATH="$HOME/.local/bin:$PATH"
            fi
            if command -v uv >/dev/null 2>&1; then
              uv run plugins/tamheed/server/tamheed_server.py --selftest
            else
              echo "::notice::uv unavailable on this runner — server smoke SKIPPED (infra, not a failure)"
            fi
  ```

- The seven `pip install mcp` sites (`grep -rn 'pip install mcp' --include='*.md' --include='*.py' . | grep -v plans/ | grep -v docs/history | grep -v CHANGELOG`):
  - `CONTRIBUTING.md:26` — `(PEP 723), or \`pip install mcp\`. The in-process test suites don't need it.`
  - `docs/install.md:21` — `zero setup (PEP 723), or \`pip install mcp\` as the fallback — see`
  - `docs/migrate-from-keystone.md:49` — `` `pip install mcp` is the fallback, see `plugins/tamheed/server/README.md`). ``
  - `plugins/tamheed/server/README.md:22` — `` 2. **pip fallback:** `pip install mcp`, then `python tamheed_server.py --package-dir <root>`. ``
  - `plugins/tamheed/server/tamheed_server.py:2888` — `_SDK_ERROR = ("… launch with 'uv run tamheed_server.py' (PEP 723 fetches it) or 'pip install mcp'.")`
  - `plugins/tamheed/SKILL.md:28` — `` setup (PEP 723), or `pip install mcp` as the fallback. See `server/README.md`. ``
  - `README.md:67` — `` … or `pip install mcp` as the ``
- Tests pinned to that text (`tests/test_mcp_contract.py`):
  - `:1679` — `self.assertIn("pip install mcp", message)` (the simulated-ImportError `serve()` test).
  - `:1703` — `self.assertNotIn("pip install mcp.", message)` (the incompatible-SDK test — "no
    install-what-you-have advice"; the `serve()` message for that branch already says
    `pip install 'mcp<2'`).
- `check.py` lint 6 requires the PEP 723 line to match `dependencies = ["mcp>=[0-9.]+,<2"]` —
  this plan does not change the pin.
- The version-stamped files (lint 8) include `README.md`, `plugins/tamheed/server/README.md`,
  `plugins/tamheed/SKILL.md` — edit only the quoted phrase in each.
- `docs/install.md:20-22` currently says `uv` "launches it with zero setup" but never says
  how to get `uv`.

### Release discipline (this repo's `check.py` will fail you otherwise)

- Do NOT bump `plugins/tamheed/.claude-plugin/plugin.json` (lint 4).
- CHANGELOG note goes under `## [Unreleased]` (line 12), `### Changed`.
- Do NOT edit the version string in the five version-stamped files.
- Do NOT widen or touch the PEP 723 pin (lint 6, locked open item).
- Lint 10 checks path tokens in `SKILL.md`/`server/README.md` resolve — the new text adds none.
- Do NOT touch `plugins/tamheed/prompts/*.md`; goldens unchanged.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Sites left | `grep -rn 'pip install mcp\b' --include='*.md' --include='*.py' . \| grep -v 'plans/\|docs/history\|CHANGELOG'` | no output |
| Contract suite | `python tests/test_mcp_contract.py` | `OK` |
| Full gate | `python check.py` | `ALL CHECKS PASSED` |
| Latest setup-uv tag | `gh api repos/astral-sh/setup-uv/releases/latest --jq .tag_name` | `vN.x.y` |
| Watch CI | `gh run list --workflow CI --limit 1`; `gh run watch <id>` | `success` |

## Scope

**In scope** (the only files you should modify):
- `.github/workflows/ci.yml`
- The seven `pip install mcp` sites listed above
- `tests/test_mcp_contract.py` — the two assertions at ~:1679 and ~:1703
- `docs/install.md` — one sentence on installing `uv`
- `CHANGELOG.md` — `## [Unreleased]`
- `plans/README.md` — your status row

**Out of scope** (do NOT touch, even though they look related):
- The PEP 723 header / `mcp` floor. Raising `>=1.2` to a newer floor is a recorded future
  option, not this plan.
- `actions/checkout@v4`, `actions/setup-python@v5` — current majors; bumping is not worth a
  diff. SHA-pinning — declined (read-only `permissions: contents: read`, no secrets).
- Python 3.14 — not verified locally; do not add.
- `.github/workflows/eval.yml`.

## Git workflow

- `main` or a local branch `advisor/052-ci-deps`; one commit:
  `ci: real uv step, py3.13 leg; docs: bounded pip install fallback (plan 052)`.
- Pushing is needed to verify the CI half; do NOT push unless the operator instructed it —
  otherwise finish Steps 1–4 and hand Step 5 over.

## Steps

### Step 1: Bound the pip fallback text

At each of the six Markdown sites replace `` `pip install mcp` `` with
`` `pip install "mcp<2"` `` (double quotes — works in bash, cmd and PowerShell). In
`tamheed_server.py:2888` change `or 'pip install mcp'.` to `or 'pip install \"mcp<2\"'.`
(the string is inside a Python `"…"` literal — use `\"` or switch the inner quotes to single
quotes: `or pip install 'mcp<2'.` — pick one and keep the `serve()` incompatible-SDK message's
existing `pip install 'mcp<2'` style for consistency: **use single quotes in the Python
string**).

Update the two test assertions:
- `:1679`: `self.assertIn("pip install 'mcp<2'", message)`
- `:1703`: leave as is (`assertNotIn("pip install mcp.", …)` still holds and still guards the
  "install what you have" regression).

**Verify**: the "Sites left" grep → no output; `python tests/test_mcp_contract.py` → `OK`.

### Step 2: Say how to get `uv`

In `docs/install.md`, after the sentence ending `… as the fallback — see …server/README.md).`
add one sentence:
`Install \`uv\` once per machine: <https://docs.astral.sh/uv/getting-started/installation/> (\`pipx install uv\`, \`winget install astral-sh.uv\`, or the one-line installer).`

**Verify**: `python check.py lint` → no `FAIL` (docs/ is unlinted, but the habit).

### Step 3: A real `uv` step in CI

Replace the `server-smoke` job body with:

```yaml
  server-smoke:
    # The uv/PEP 723 launch path is the documented install story — smoke it for real:
    # --selftest registers every tool with the SDK (plan 047) and exits 1 on failure.
    name: MCP server smoke (uv / PEP 723)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@<MAJOR>
      - name: Server selftest via uv
        shell: bash
        run: uv run plugins/tamheed/server/tamheed_server.py --selftest
```

where `<MAJOR>` is the **exact** tag of the latest `astral-sh/setup-uv` release
(`gh api repos/astral-sh/setup-uv/releases/latest --jq .tag_name` → e.g. `v10.1.0` → use
`v10.1.0`). Executor finding 2026-09-11: upstream stopped publishing floating major tags after
`v7` (`v10` does not resolve), so a bare `vN` would fail at action resolution; pin the full tag.
Drop the `|| true` / notice branch entirely — an unavailable `uv` is now a failing step, which
is the point.

### Step 4: The 3.13 leg

Change `python: ['3.10', '3.11', '3.12']` to `python: ['3.10', '3.11', '3.12', '3.13']`.
Keep `fail-fast: false`.

**Verify (local)**: `python --version` → 3.13.x if available, then `python check.py` →
`ALL CHECKS PASSED`; if 3.13 is not installed locally, note that and rely on Step 5.

### Step 5 (operator, or executor if instructed): push and watch

Commit, push, then `gh run list --workflow CI --limit 1` and `gh run watch <id>`.

**Verify**: all 8 `check` legs `success`; `server-smoke` `success` with a log line
`mcp sdk: ok (…) — 18/18 tools registered`.

### Step 6: CHANGELOG

Under `## [Unreleased]` → `### Changed`:

```markdown
- CI: the MCP server smoke job installs `uv` with `astral-sh/setup-uv` and fails on a failed
  `--selftest` (it used to skip); Python 3.13 joins the matrix. Docs and the server's error
  text now say `pip install "mcp<2"` — the unbounded fallback reproduced the C33 incident the
  PEP 723 pin prevents (advisor plan 052).
```

**Verify**: `python check.py` → `ALL CHECKS PASSED`.

## Test plan

- Modified assertion `:1679`; the suite must stay green SDK-free.
- The real test is the CI run in Step 5 (8 + 1 jobs green).

## Done criteria

- [ ] "Sites left" grep → no output
- [ ] `grep -n "astral-sh/setup-uv@" .github/workflows/ci.yml` → one hit; `grep -n '|| true' .github/workflows/ci.yml` → none
- [ ] `grep -n "'3.13'" .github/workflows/ci.yml` → one hit
- [ ] `python tests/test_mcp_contract.py` → `OK`; `python check.py` → `ALL CHECKS PASSED`
- [ ] A CI run on the pushed commit with all `check` legs and `server-smoke` `success` (URL in the index row)
- [ ] `git status` shows only in-scope files
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:

- Plan 042 has not recorded a green run — do this plan after it.
- The 3.13 leg fails on either OS: report `gh run view <id> --log-failed` output; do not
  remove the leg or patch code here.
- `server-smoke` fails with fewer than 18 tools registered or a registration exception — a
  real serving defect (plan 047 made it visible); report verbatim.
- `gh api repos/astral-sh/setup-uv/releases/latest` is unreachable — do not guess the tag;
  report and leave Step 3 undone.

## Maintenance notes

- The smoke job is now load-bearing: a new tool that FastMCP rejects fails CI. That is
  intended; reviewers should read the smoke log when a tool is added.
- When 3.14 is verified locally (`python check.py` under 3.14 with
  `PYTHONWARNINGS=error::DeprecationWarning`), adding the leg is a one-token change here.
- The `mcp` floor (`>=1.2`) is older than any version anyone has run recently; raising it is
  a deliberate decision recorded as a future option — verify the lowest working version first.
