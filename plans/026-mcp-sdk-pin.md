# Plan 026 (B22): Pin the MCP SDK; truthful startup diagnostics

## Status

**DONE (2026-08-08)** — one code phase + close-out, `check.py` green; released as
**v2.7.1** (PATCH — dependency bound + startup-diagnostic honesty; no behavior change
past startup, no schema migration). Evidence: the twelfth ACMP field report
(`evidence/acmp-field-report-12-2026-08-08.md`) — an incident report hours after
findings_11: **MCP SDK 2.0.0 removed `mcp.server.fastmcp`**, and the unbounded
`dependencies = ["mcp"]` in the PEP 723 header made every freshly resolved environment
unable to start the server, across ALL plugin versions (cached `uv` environments masked
it — 2.6.0 "worked" only because its environment predated SDK 2.0.0). Cluster **C33**.
The report also retracts findings_11 §C ("harness-side reconnect failure") — §C only;
that run's in-process verifications stand.

## What shipped

1. **A1 — the pin**: `dependencies = ["mcp>=1.2,<2"]`, with a header comment forbidding
   widening without the deliberate port. Verified end-to-end: `uv run … --selftest` on a
   fresh resolve reports `mcp sdk: ok (1.28.1)`.
2. **A2-class — the guard tells the truth**: `serve()`'s ImportError path prints the
   CAUGHT exception and distinguishes *absent* (install guidance + the real error) from
   *incompatible* (`mcp <version> is installed but does not provide mcp.server.fastmcp —
   this build requires mcp<2`) — the old hint advised installing the package that was
   already present and was the cause (an hour lost to three confident wrong
   conclusions). `_mcp_version()` prefers the module's own `__version__`, then
   distribution metadata (the shipped SDK exposes no attribute).
3. **Ask 4 — selftest probes serving**: `--selftest` reports
   `mcp sdk: ok (<version>)` / `UNAVAILABLE for serving (<error>)` informationally,
   never failing (the contract tests run SDK-free by design) — a passing selftest can no
   longer be mistaken for a serving server (the broken import was the one path no health
   check touched).
4. **Close-out**: server README bounded-dependency note; findings_12 archived (C33, its
   header carrying the findings_11 §C retraction — the C32 header's harness-side note is
   SUPERSEDED, never edited); plans/README row + alignment record; CHANGELOG `[2.7.1]` +
   plugin.json (version-sync lint); tag v2.7.1. Three tests.

## Verification

`check.py` green (~201 tests, 3 new; the missing-SDK test now also asserts the caught
exception is shown). Live probe: `uv run plugins/tamheed/server/tamheed_server.py
--selftest` → `mcp sdk: ok (1.28.1)` on a fresh PEP 723 resolve — the exact path the
incident broke. **Acceptance (maintainer): ACMP upgrades to 2.7.1 and the MCP transport
reconnects on a fresh resolve.**

## Deferred / rejected

- **Port `serve()` to `mcp.server.mcpserver` (report ask 2)** — DEFERRED, deliberate
  work on its own schedule once the pin has bought the time (the report's own framing);
  the pin comment and this doc are the record. Never widen the pin without it.
- Making the selftest SDK probe fatal — the contract tests and CI run SDK-free by
  design; informational is the correct strength.
