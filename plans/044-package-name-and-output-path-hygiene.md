# Plan 044: Validate the package name on every tool that resolves one, and guard `export_html`'s output path

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` (section "Advisor audit 2026-09-10") — unless a reviewer
> dispatched you and told you they maintain the index.
>
> **Drift check (run first)**: `git diff --stat 7e3a92b..HEAD -- plugins/tamheed/server/tamheed_server.py tests/test_mcp_contract.py tests/test_export_html.py SECURITY.md CHANGELOG.md`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none (independent of 043; if both are executed, run 043 first so the
  `entity_upsert` tail is settled before you touch the file)
- **Category**: security
- **Planned at**: commit `7e3a92b`, 2026-09-10

## Why this matters

`SECURITY.md` promises: *"No path traversal — the MCP server validates package names as a
single kebab-case segment … a malicious name is rejected and writes nothing."* That is true
for `package_create` only. `package_open`, `package_verify(name=…)` and `package_migrate`
build `PACKAGE_ROOT / name` from the raw argument: `package_open("../../other-project/pkg")`
opens (and, on close, rewrites in canonical form) any directory that has a `data/`
subdirectory, and `package_migrate("../x", confirm=True)` deletes and rewrites `data/*.jsonl`
there. The caller is an agent acting on untrusted brief/repository text, which is exactly the
trust boundary SECURITY.md describes. Separately, `export_html(output=…)` writes wherever it
is told with no check at all, and creates a `csv/` directory beside that path. This plan makes
the documented claim true with one helper applied at four sites, and gives `export_html` the
minimum overwrite guard (must end in `.html`; an existing file must be one we emitted).

## Current state

Line numbers below are at `7e3a92b`; earlier advisor plans (043) shift them by a line or two.
Compare the **excerpts**, not the numbers — a matching excerpt at a nearby line is not drift.

- `plugins/tamheed/server/tamheed_server.py` — the MCP server.
  - The regex and its only use:

    ```python
    # :52
    _NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")

    # package_create, :412-414
        if not _NAME_RE.match(name):
            return _err(f"invalid package name {name!r} (kebab-case, [a-z0-9-])")
        pkg_dir = PACKAGE_ROOT / name
    ```

  - `package_open(name)` at :565–588 — no validation:

    ```python
        pkg_dir = PACKAGE_ROOT / name
        if not (pkg_dir / "data").exists():
            return _err(f"package '{name}' not found under {PACKAGE_ROOT}")
        stored = _stored_package_version(pkg_dir)
    ```

  - `package_verify(name: str | None = None, record: bool = False)` at :608 — with `name`
    given it resolves `PACKAGE_ROOT / name` the same way (read the function; the resolution
    line is near the top, after the docstring).
  - `package_migrate(name, confirm=False)` at :2541 — same shape:

    ```python
        pkg_dir = PACKAGE_ROOT / name
        data = pkg_dir / "data"
        if not data.exists():
            return _err(f"package '{name}' not found under {PACKAGE_ROOT}")
    ```

  - `export_html(output: str | None = None)` at :2799–2836:

    ```python
        path = Path(output) if output else PACKAGE_ROOT / _CURRENT_NAME / "review.html"
        path.write_text(text, encoding="utf-8", newline="\n")
        ...
        csv_dir = path.parent / "csv"
    ```

  - `_read_jsonl_tables(data_dir)` at :2525–2538 keys tables by `path.stem` of every
    `data/*.jsonl`; `package_migrate` later interpolates that stem into
    `f"PRAGMA table_info({tname})"` (:2630). `sqlite3.Connection.execute` refuses multiple
    statements, so this is not an injection, but a stem outside `[a-z_]` is never a table and
    is worth refusing with a clear message rather than a SQL error.
  - `_err(message, **extra)` at :348 builds `{"ok": False, "error": message, ...}`.
- `SECURITY.md:30-32` — the claim to make true:

  ```
  - **No path traversal** — the MCP server validates package names as a single kebab-case segment
    (`^[a-z0-9][a-z0-9-]*$`, `.`/`..` unrepresentable) under the declared `--package-dir` (CWE-22);
    a malicious name is rejected and writes nothing.
  ```

- Tests: `tests/test_mcp_contract.py` (`McpContractTest`, `setUp` sets `srv.PACKAGE_ROOT` to a
  temp dir; `make_complete_package("demo")` builds a full package). `tests/test_export_html.py`
  (`ExportHtmlTest`, `_open_demo_copy()` copies `generated-samples/support-triage-agent-v2/data`
  into the temp root and opens it; `test_csv_links_and_files` is the CSV exemplar).
- The viewer's HTML starts with a fixed prologue produced by `export_html.render` — look at the
  first ~5 lines of `plugins/tamheed/server/export_html.py`'s `render()` output; whatever the
  first line is (a `<!doctype html>` line followed by markup mentioning `tamheed`) is the
  signature used in Step 3. Confirm with:
  `python -c "import sys; sys.path.insert(0,'plugins/tamheed/server'); import export_html as v; print(open('generated-samples/support-triage-agent-v2/review.html', encoding='utf-8').read(200))"`
  — if that file does not exist, generate one in a temp package via `export_html()` first.

### Release discipline (this repo's `check.py` will fail you otherwise)

- Do NOT bump `plugins/tamheed/.claude-plugin/plugin.json` (lint 4).
- CHANGELOG note goes under the existing `## [Unreleased]` heading (line 12), `### Fixed`.
- Do NOT edit the version string in the five version-stamped files (root `README.md`,
  `plugins/tamheed/server/README.md`, `plugins/tamheed/prompts/README.md`,
  `plugins/tamheed/SKILL.md`, `plugins/tamheed/references/artifact-catalog.md`).
- Do NOT touch `plugins/tamheed/prompts/*.md`.
- Goldens (`evals/sample-results/**`, `generated-samples/**`) must not change in this plan.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Contract suite | `python tests/test_mcp_contract.py` | `OK` |
| Viewer suite | `python tests/test_export_html.py` | `OK` |
| Full gate | `python check.py` | `ALL CHECKS PASSED` |
| Find call sites | `grep -n 'PACKAGE_ROOT / name' plugins/tamheed/server/tamheed_server.py` | 4 hits before, 4 after (each now preceded by the guard) |

## Scope

**In scope** (the only files you should modify):
- `plugins/tamheed/server/tamheed_server.py`
- `tests/test_mcp_contract.py`, `tests/test_export_html.py`
- `SECURITY.md` — lines 30–32 only (the regex text)
- `CHANGELOG.md` — `## [Unreleased]`
- `plans/README.md` — your status row

**Out of scope** (do NOT touch, even though they look related):
- `handoff_emit`'s `target_dir` handling — it is an operator-supplied *target project*
  directory by design (it already rejects subdir-shaped prompt names; see
  `test_handoff_emit_subdir_rejected`). Not this plan.
- `package_adopt(source_dir, …)` — reads an arbitrary operator-named directory by design.
- `entity_export` paths — locked by plan 041 (absolute paths recorded deliberately).
- `SECURITY.md:28` (the `scripts/scratch_diff.py` path) and `:27` ("no git commands") — plan 048.
- Changing `_NAME_RE` itself.

## Git workflow

- `main` or a local branch `advisor/044-name-path-hygiene`; conventional commit, e.g.
  `fix: validate package names on open/verify/migrate; guard export_html output (plan 044)`.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: One helper, four call sites

Directly below `_NAME_RE` (line 52) add:

```python
def _bad_name(name) -> dict | None:
    """Every tool that turns a name into PACKAGE_ROOT / name goes through here (plan 044:
    SECURITY.md's traversal claim was true of package_create only)."""
    if not isinstance(name, str) or not _NAME_RE.match(name):
        return _err(f"invalid package name {name!r} (kebab-case, [a-z0-9-], one segment)")
    return None
```

Then, at each of the four sites, insert the guard immediately before `pkg_dir = PACKAGE_ROOT / name`:

```python
    if err := _bad_name(name):
        return err
```

- `package_create`: replace the existing two-line `if not _NAME_RE.match(name): return _err(...)`
  with the guard (keeps behaviour, one source of truth).
- `package_open`: before `pkg_dir = PACKAGE_ROOT / name`.
- `package_verify`: only when `name is not None` (with `name=None` it verifies the open package).
- `package_migrate`: before `pkg_dir = PACKAGE_ROOT / name`.

Note: the "already open" checks that precede these lines in `package_create`/`package_open`/
`package_migrate` stay first — a bad name on a busy server should still say "already open".

**Verify**: `python tests/test_mcp_contract.py` → `OK`. Then, from the repo root:
`python -c "import sys,tempfile,pathlib; sys.path.insert(0,'plugins/tamheed/server'); import tamheed_server as s; s.PACKAGE_ROOT=pathlib.Path(tempfile.mkdtemp()); print(s.package_open('../x')['error']); print(s.package_migrate('../x')['error']); print(s.package_verify('../x')['error'])"`
→ three lines each starting `invalid package name '../x'`.

### Step 2: Refuse non-table stems in `_read_jsonl_tables`

In `_read_jsonl_tables`, after `for path in sorted(data_dir.glob("*.jsonl")):` add:

```python
        if not re.fullmatch(r"[a-z][a-z0-9_]*", path.stem):
            raise ValueError(f"{path.name}: not a canonical table file (data/ holds only"
                             " <table>.jsonl — move or delete it)")
```

The caller (`package_migrate` :2606) already catches `ValueError` and returns `_err(str(exc))`.

**Verify**: `python tests/test_migrate_v3to4.py` → `OK`.

### Step 3: Guard `export_html(output)`

Replace the two lines

```python
    path = Path(output) if output else PACKAGE_ROOT / _CURRENT_NAME / "review.html"
    path.write_text(text, encoding="utf-8", newline="\n")
```

with

```python
    path = Path(output) if output else PACKAGE_ROOT / _CURRENT_NAME / "review.html"
    if output:
        # plan 044: `output` is a free path from an agent; the only files this tool may
        # replace are review surfaces it emitted. Same memoryless rule as _managed_emit.
        if path.suffix.lower() != ".html":
            return _err(f"output must be a .html path (got {output!r})")
        if path.exists() and not path.read_text(encoding="utf-8",
                                                errors="replace").startswith(_HTML_PROLOGUE):
            return _err(f"{output} exists and is not a Tamheed review surface — refusing to"
                        " overwrite; choose another path or delete it first")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
```

and define `_HTML_PROLOGUE` next to `_NAME_RE` as the exact first line the viewer emits (find
it as described in "Current state"; e.g. `_HTML_PROLOGUE = "<!doctype html>"` if that is the
first line — use the literal bytes the renderer produces, not a guess). If the prologue alone
is too generic to identify a Tamheed file, extend it to the first line *plus* the first
occurrence of `tamheed` within the first 300 characters — keep it to a single `startswith`/
`in` check; no parsing.

**Verify**: `python tests/test_export_html.py` → `OK` (the default path and the existing
`output=` uses still work — check `grep -n 'export_html(' tests/*.py evals/*.py` for callers
that pass `output` and run those suites).

### Step 4: Tests

`tests/test_mcp_contract.py`, class `McpContractTest`, after `test_selftest_lists_full_tool_surface`
or any sensible spot:

```python
    def test_package_name_validated_on_every_resolving_tool(self):
        """Plan 044: SECURITY.md's traversal claim covered package_create only."""
        make_complete_package("demo")
        srv.package_close()
        for bad in ("../demo", "demo/../demo", "..", "DEMO", "a b", ""):
            for tool in (srv.package_open, srv.package_migrate, srv.package_verify):
                out = tool(bad)
                self.assertFalse(out.get("ok"), (tool.__name__, bad, out))
                self.assertIn("invalid package name", out["error"], (tool.__name__, bad))
        self.assertIsNone(srv._CURRENT)                    # nothing was opened
        self.assertTrue(srv.package_open("demo")["ok"])   # the good name still opens
```

The load-bearing assertions are the refusals and `srv._CURRENT is None`.

`tests/test_export_html.py`, class `ExportHtmlTest`:

```python
    def test_export_output_guard(self):
        """Plan 044: `output` may only replace a review surface Tamheed emitted."""
        self._open_demo_copy()
        foreign = Path(self._tmp.name) / "notes.html"
        foreign.write_text("<p>mine</p>", encoding="utf-8")
        out = srv.export_html(output=str(foreign))
        self.assertFalse(out["ok"]); self.assertIn("not a Tamheed review surface", out["error"])
        self.assertEqual(foreign.read_text(encoding="utf-8"), "<p>mine</p>")
        self.assertFalse(srv.export_html(output=str(Path(self._tmp.name) / "x.txt"))["ok"])
        ok_path = Path(self._tmp.name) / "out" / "review.html"
        self.assertTrue(srv.export_html(output=str(ok_path))["ok"])   # fresh path: fine
        self.assertTrue(srv.export_html(output=str(ok_path))["ok"])   # our own file: fine
```

**Verify**: `python tests/test_mcp_contract.py` → `OK`; `python tests/test_export_html.py` → `OK`.

### Step 5: Docs + CHANGELOG

- `SECURITY.md:31`: change `` (`^[a-z0-9][a-z0-9-]*$`, `.`/`..` unrepresentable) `` to
  `` (`^[a-z0-9][a-z0-9-]{0,63}$`, applied by every tool that resolves a name — create, open, verify, migrate; `.`/`..` unrepresentable) ``.
- `CHANGELOG.md` under `## [Unreleased]` → `### Fixed`:

  ```markdown
  - Package names are validated on `package_open`, `package_verify` and `package_migrate`,
    not only on `package_create` — SECURITY.md's traversal claim is now true of every tool
    that resolves a name; `export_html(output=…)` refuses to overwrite a file it did not emit
    and requires a `.html` path (advisor plan 044).
  ```

**Verify**: `python check.py` → `ALL CHECKS PASSED`.

## Test plan

- New: `test_package_name_validated_on_every_resolving_tool` (contract),
  `test_export_output_guard` (viewer). Model on the neighbouring tests named above.
- Existing that exercise the touched paths and must stay green: `test_package_migrate_is_staged`,
  `test_package_verify_round_trip_report_and_record`, `test_csv_links_and_files`, the whole
  `tests/test_migrate_v3to4.py`, `tests/test_eval_runner.py` (drives `package_open` by name).
- Verification: `python check.py` → `ALL CHECKS PASSED`.

## Done criteria

- [ ] `grep -c '_bad_name(name)' plugins/tamheed/server/tamheed_server.py` → `4`
- [ ] `grep -n '_NAME_RE.match' plugins/tamheed/server/tamheed_server.py` → exactly one hit, inside `_bad_name`
- [ ] `python tests/test_mcp_contract.py`, `python tests/test_export_html.py`, `python tests/test_migrate_v3to4.py` → all `OK`
- [ ] `python check.py` → `ALL CHECKS PASSED`
- [ ] `git status` shows only in-scope files; `git diff --stat -- evals generated-samples` is empty
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:

- Any of the four `PACKAGE_ROOT / name` sites is not where "Current state" says (drift).
- `grep -n 'export_html(' evals/ tests/ lab/` shows a caller passing an `output` that is not
  `.html` or that points at a non-Tamheed existing file — report; do not widen the guard.
- A test in `tests/test_eval_runner.py` or `evals/pkg_check.py` opens packages by a name that
  fails `_NAME_RE` (e.g. contains uppercase or a slash) — the fixture names are the operator's;
  report instead of loosening the regex.
- You want to change `_NAME_RE`.

## Maintenance notes

- Rule for reviewers: any new tool parameter that is joined onto `PACKAGE_ROOT` must go through
  `_bad_name`. `grep -n 'PACKAGE_ROOT /' tamheed_server.py` should show only `_bad_name`-guarded
  sites plus the `_CURRENT_NAME`-based ones (already validated at open).
- The `export_html` guard is memoryless like `_managed_emit`: it recognises our own output by
  its prologue, not by a ledger. If the viewer's first line ever changes, update
  `_HTML_PROLOGUE` in the same commit (the new test will catch a mismatch because the second
  export to `ok_path` would be refused).
- Deferred deliberately: `csv/` sits beside the output path and is force-overwritten by design
  (C27/D2); the guard on the `.html` path is what stops the directory landing somewhere hostile.
