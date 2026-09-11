# Plan 047: `--selftest` registers every tool with FastMCP so "selftest passes" means "serving works"

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` (section "Advisor audit 2026-09-10") — unless a reviewer
> dispatched you and told you they maintain the index.
>
> **Drift check (run first)**: `git diff --stat 7e3a92b..HEAD -- plugins/tamheed/server/tamheed_server.py tests/test_mcp_contract.py plugins/tamheed/server/README.md CHANGELOG.md`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none (plan 052 makes the CI smoke job depend on this being meaningful)
- **Category**: tests
- **Planned at**: commit `7e3a92b`, 2026-09-10

## Why this matters

The contract tests run the tool functions in-process and never import the MCP SDK (by
design, D-U3). The only path that exercises the SDK is `serve()`, which is never run under
test, and `--selftest`, which today imports `FastMCP` and stops — it never calls
`app.tool(...)`. FastMCP builds each tool's JSON schema from the function signature and
type hints *at registration*; a tool with a signature the SDK rejects (an unsupported
annotation, a `*args`, a default it cannot serialize) is a server that starts, registers
nothing or crashes, and every check in this repo stays green. Field evidence C33 was
exactly this class ("selftest passes" mistaken for "serving works"). Verified 2026-09-10:
with mcp 1.27.2 all 18 tools register today — so this plan is a *tripwire*, not a fix: make
selftest do the registration and count, and let the CI smoke job (plan 052) run it.

## Current state

- `plugins/tamheed/server/tamheed_server.py`
  - The PEP 723 header (:1–4): `dependencies = ["mcp>=1.2,<2"]` — `uv run` resolves it.
  - `TOOLS` dict at :2861 — `name -> (function, description)`, 18 entries.
  - `selftest()` :2904–2916:

    ```python
    def selftest() -> int:
        print(f"tamheed MCP server — {len(TOOLS)} tools")
        for name, (_, desc) in TOOLS.items():
            print(f"  {name}: {desc}")
        # C33 (ask 4): the broken import was the ONE path no health check touched —
        # report SDK availability without failing (the contract tests run SDK-free by
        # design, and the tool surface itself needs no SDK).
        try:
            from mcp.server.fastmcp import FastMCP  # noqa: F401
            print(f"mcp sdk: ok ({_mcp_version()})")
        except ImportError as exc:
            print(f"mcp sdk: UNAVAILABLE for serving ({exc})")
        return 0
    ```

  - `serve()` :2919–2941 — the registration loop it should share:

    ```python
        app = FastMCP("tamheed")
        for name, (func, desc) in TOOLS.items():
            app.tool(name=name, description=desc)(func)
        app.run()  # stdio transport
        return 0
    ```

  - `main()` :2944 — `--selftest` → `return selftest()`.
- `tests/test_mcp_contract.py`
  - `test_selftest_reports_sdk_availability` (~:1705) asserts `main(["--selftest"])` returns 0
    and prints `mcp sdk:`; `test_selftest_lists_full_tool_surface` (~:1714) asserts every tool
    name is printed. Both run with or without the SDK installed.
  - A "simulated ImportError" test around :1679–1703 patches `sys.modules` to make
    `mcp.server.fastmcp` unimportable and asserts the `serve()` error text; it must keep passing.
- `plugins/tamheed/server/README.md` documents `--selftest` as "list tools and exit"
  (`grep -n selftest plugins/tamheed/server/README.md`).
- Listing registered tools on FastMCP 1.x: `app.list_tools()` is a coroutine → use
  `asyncio.run(app.list_tools())`; it returns a list of `Tool` objects with `.name`.
  (Verified on 1.27.2: `len(asyncio.run(app.list_tools()))` → `18`.)
- `.github/workflows/ci.yml` `server-smoke` job runs
  `uv run plugins/tamheed/server/tamheed_server.py --selftest` when `uv` is available.

### Release discipline (this repo's `check.py` will fail you otherwise)

- Do NOT bump `plugins/tamheed/.claude-plugin/plugin.json` (lint 4).
- CHANGELOG note goes under `## [Unreleased]` (line 12), `### Changed`.
- `plugins/tamheed/server/README.md` is one of the five version-stamped files (lint 8): edit
  the `--selftest` sentence only; leave the version string alone.
- Lint 10 checks path tokens in `server/README.md` resolve — don't add new paths.
- Do NOT touch `plugins/tamheed/prompts/*.md`; do NOT hand-edit goldens.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Contract suite | `python tests/test_mcp_contract.py` | `OK` |
| Selftest, SDK present | `uv run plugins/tamheed/server/tamheed_server.py --selftest` | prints `mcp sdk: ok (…) — 18/18 tools registered`, exit 0 |
| Selftest, no SDK | `python -S -c "..."` is overkill — use the existing simulated-ImportError test | — |
| Full gate | `python check.py` | `ALL CHECKS PASSED` |
| Is uv here? | `uv --version` | a version string |

## Scope

**In scope** (the only files you should modify):
- `plugins/tamheed/server/tamheed_server.py` — `selftest()`, `serve()`, a new `_build_app()`.
- `tests/test_mcp_contract.py` — extend the two selftest tests.
- `plugins/tamheed/server/README.md` — the one sentence describing `--selftest`.
- `CHANGELOG.md` — `## [Unreleased]`.
- `plans/README.md` — your status row.

**Out of scope** (do NOT touch, even though they look related):
- `.github/workflows/ci.yml` — plan 052 (after plan 042 has produced a run).
- The PEP 723 pin / porting to `mcp.server.mcpserver` — locked open item, lint-guarded.
- Tool signatures. If registration fails for a tool, that is a STOP-and-report (a real
  finding), not something to patch in this plan.

## Git workflow

- `main` or a local branch `advisor/047-selftest-registers`; one commit:
  `test: --selftest registers the tool surface with FastMCP and counts it (plan 047)`.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Share the registration loop

Add above `selftest()`:

```python
def _build_app():
    """The FastMCP app with every TOOLS entry registered — shared by serve() and
    --selftest (plan 047: registration is where the SDK validates signatures, and it
    was the one step no check exercised)."""
    from mcp.server.fastmcp import FastMCP
    app = FastMCP("tamheed")
    for name, (func, desc) in TOOLS.items():
        app.tool(name=name, description=desc)(func)
    return app
```

In `serve()`, keep the existing `try: from mcp.server.fastmcp import FastMCP … except
ImportError` diagnostic block exactly as is (it is the C33 error text under test), then
replace the three registration lines with `app = _build_app()` followed by `app.run()`.

**Verify**: `python tests/test_mcp_contract.py` → `OK` (the simulated-ImportError test still
sees the same message).

### Step 2: Make selftest register and count

Replace the `try` block in `selftest()` with:

```python
    try:
        import asyncio
        app = _build_app()
        registered = [t.name for t in asyncio.run(app.list_tools())]
        missing = sorted(set(TOOLS) - set(registered))
        print(f"mcp sdk: ok ({_mcp_version()}) — {len(registered)}/{len(TOOLS)} tools registered")
        if missing:
            print(f"  NOT registered: {', '.join(missing)}")
            return 1
    except ImportError as exc:
        print(f"mcp sdk: UNAVAILABLE for serving ({exc})")
    except Exception as exc:  # a signature the SDK rejects — the C33 class, made visible
        print(f"mcp sdk: registration FAILED ({type(exc).__name__}: {exc})")
        return 1
    return 0
```

Semantics: no SDK → still exit 0 with the UNAVAILABLE line (the contract tests run SDK-free);
SDK present but any tool fails to register → exit 1. Update `main()`'s argparse help from
`"list tools and exit"` to `"list tools, register them with the SDK if present, and exit"`.

**Verify**: `uv run plugins/tamheed/server/tamheed_server.py --selftest` → last line
`mcp sdk: ok (<version>) — 18/18 tools registered`, exit code 0
(`echo $?` / `$LASTEXITCODE`). If `uv` is not installed but `python -c "import mcp"` works,
`python plugins/tamheed/server/tamheed_server.py --selftest` is equivalent.

### Step 3: Tests

Extend the two existing tests (do not add a third that requires the SDK — the suite must
stay SDK-free):

```python
    def test_selftest_reports_sdk_availability(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = srv.main(["--selftest"])
        out = stdout.getvalue()
        self.assertIn("mcp sdk:", out)
        if "UNAVAILABLE" in out:
            self.assertEqual(code, 0)                       # SDK-free run stays informational
        else:                                               # SDK present: registration counted
            self.assertEqual(code, 0, out)
            self.assertIn(f"{len(srv.TOOLS)}/{len(srv.TOOLS)} tools registered", out)
```

Add one SDK-free test for the failure branch by simulating a rejected registration:

```python
    def test_selftest_fails_when_a_tool_does_not_register(self):
        """Plan 047: registration is where the SDK validates signatures."""
        from unittest import mock
        with mock.patch.object(srv, "_build_app", side_effect=TypeError("bad signature")):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = srv.main(["--selftest"])
        self.assertEqual(code, 1)
        self.assertIn("registration FAILED", stdout.getvalue())
```

**Verify**: `python tests/test_mcp_contract.py` → `OK`.

### Step 4: Docs + CHANGELOG

- `plugins/tamheed/server/README.md`: where `--selftest` is described, say it "lists the tools
  and, when the `mcp` SDK is importable, registers every tool with FastMCP and reports
  `N/N tools registered` (exit 1 on any registration failure)".
- `CHANGELOG.md` under `## [Unreleased]` → `### Changed`:

  ```markdown
  - `--selftest` now registers the whole tool surface with FastMCP when the SDK is present
    and exits 1 if any tool fails to register — the one step no check exercised (C33's
    class); SDK-free runs stay informational (advisor plan 047).
  ```

**Verify**: `python check.py` → `ALL CHECKS PASSED`.

## Test plan

- Modified: `test_selftest_reports_sdk_availability` (branches on SDK presence).
- New: `test_selftest_fails_when_a_tool_does_not_register` (mocked, SDK-free).
- Unchanged and must pass: `test_selftest_lists_full_tool_surface`, the simulated-ImportError
  `serve()` test.
- Manual: `uv run … --selftest` → `18/18 tools registered`.

## Done criteria

- [ ] `grep -c '_build_app()' plugins/tamheed/server/tamheed_server.py` → `3` (the `def` + serve + selftest)
- [ ] `uv run plugins/tamheed/server/tamheed_server.py --selftest` prints `18/18 tools registered` and exits 0
- [ ] `python tests/test_mcp_contract.py` → `OK`
- [ ] `python check.py` → `ALL CHECKS PASSED`
- [ ] `git status` shows only in-scope files
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:

- Neither `uv` nor an importable `mcp` (<2) is available locally — Step 2 cannot be verified;
  report and mark BLOCKED (the change is still safe to land, but say it is unverified).
- Registration reports fewer than 18 tools or raises — that is a real serving defect; report
  the tool name and the exception verbatim. Do not change a tool's signature here.
- `app.list_tools()` is not awaitable on the installed SDK version — print the SDK version and
  report; do not reach into `app._tool_manager`.

## Maintenance notes

- Every new tool added to `TOOLS` is now validated by `--selftest` under `uv` (and by CI's
  smoke job once plan 052 lands). A reviewer adding a tool should run it locally.
- When the mcpserver port (the locked open item) happens, `_build_app()` is the single place
  the construction changes.
