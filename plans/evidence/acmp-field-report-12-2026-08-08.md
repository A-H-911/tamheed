<!-- Archived by plan 026 Phase 2 (field-evidence C33). Verbatim copy of the twelfth ACMP
operator field report (findings_12.md): an INCIDENT report hours after findings_11 —
MCP SDK 2.0.0 removed mcp.server.fastmcp and Tamheed's unbounded PEP 723 dependency
("mcp") made every freshly resolved environment unable to start the server, across ALL
plugin versions (cached uv environments masked it). Verified fix: pin mcp<2 (clean
handshake, mcp 1.28.1). §A2-class guard defect: the ImportError message advised
installing the package that was already present and was the cause, swallowing the real
exception (an hour lost to three wrong conclusions). CARRIES THE RETRACTION of
findings_11 §C (the "harness-side reconnect failure" attribution) — §C only; that
report's in-process §A/§B verifications stand, and its own transport caveat was the
correct hedge. Supersedes the C32 header's harness-side note accordingly (evidence is
superseded, never edited). Drove v2.7.1. Do not edit: evidence, not documentation. -->

# Tamheed 2.7.0 — field report: an unpinned `mcp` dependency now stops every version from starting

**Context.** Eleventh run, and an unplanned one — an incident report rather than a verification pass.
Written 2026-08-08, hours after `findings_11.md` closed the C31 cycle clean. Same **2.7.0** plugin.
It exists because the MCP server would not connect after the 2.6.0 → 2.7.0 upgrade, and the cause is
neither the upgrade nor the harness: the **MCP Python SDK released 2.0.0**, and Tamheed's PEP 723
header pins nothing. Live-package writes this run: **zero**. file:line refs are into the 2.7.0 plugin
source. Every claim below was observed directly unless marked unverified.

**Bottom line.** One HIGH defect, external trigger, and the blast radius is everything: **no version
of Tamheed can start its MCP server on a freshly resolved environment.** Not 2.7.0, not 2.6.0 — the
dependency line is byte-identical across both, and 2.6.0 only still runs here because its `uv`
environment was cached *before* SDK 2.0.0 existed. The quick fix is one character class in one line.
This report also **retracts `findings_11.md` §C**, which attributed the same symptom to a harness
reconnect failure and stated it was not a Tamheed defect. It is one (§B).

---

## A. The defect

### A1. `dependencies = ["mcp"]` is unbounded, and SDK 2.0.0 removed the module `serve()` imports

`tamheed_server.py` line 3, **identical in 2.6.0 and 2.7.0**:

```python
# dependencies = ["mcp"]
```

`serve()` — also byte-identical across both versions, 11 lines, verified by diff — imports:

```python
from mcp.server.fastmcp import FastMCP
```

MCP SDK **2.0.0** does not have that module. Measured in the failing environment by patching the
guard on a *copy* of the plugin (the install was not modified):

```
MCP VERSION: 2.0.0
MCP PATH   : …\uv\cache\environments-v2\tamheed-server-…\Lib\site-packages\mcp\__init__.py
ModuleNotFoundError: No module named 'mcp.server.fastmcp'
```

The package still ships `mcp.server`; `fastmcp` is simply gone from it:

```
mcp 2.0.0 top-level:      ['cli', 'client', 'os', 'server', 'shared', 'types']
mcp 2.0.0 mcp.server.*:   ['__main__', '_otel', '_streamable_http_modern', 'apps', 'auth',
                           'caching', 'connection', 'context', 'elicitation', 'extension',
                           'lowlevel', 'mcpserver']
hasattr(mcp, 'FastMCP'):  False
```

`mcpserver` looks like the successor to `fastmcp`, so this is a rename/restructure in a major
release rather than a deletion — but there is no top-level `FastMCP` alias to soften it.

**Why this is not a 2.7.0 regression, and why that makes it worse.** The header and `serve()` are the
same in both versions, so 2.6.0 has the identical defect. It keeps working on this machine only
because its `uv` environment was resolved before 2.0.0 shipped and is still cached. Proven by running
the same MCP `initialize` handshake against both:

```
2.6.0 →  {"result":{…,"serverInfo":{"name":"tamheed","version":"1.28.1"}}}     (cached env)
2.7.0 →  tamheed MCP server requires the 'mcp' SDK …                          (fresh env)
```

So the failure is not "the upgrade broke it". It is **"any environment resolved from now on is
broken"** — which includes every new install, every CI runner, every colleague cloning the plugin,
and every existing user the moment their `uv` cache is cleaned or keyed differently. The upgrade was
merely what forced a fresh resolve here.

**Verified fix.** Pinning below the major restores it immediately — same handshake, clean result:

```
uv run --with "mcp<2" …/2.7.0/server/tamheed_server.py --package-dir .
  →  {"result":{…,"serverInfo":{"name":"tamheed","version":"1.29.0"}}}
```

**Suggested fix:** bound the dependency in the PEP 723 header — `dependencies = ["mcp>=1.2,<2"]` —
as the immediate release, then port `serve()` to `mcp.server.mcpserver` deliberately rather than
under pressure. An unbounded dependency on a pre-1.0-culture SDK is a standing hazard: the plugin's
own guarantee ("stdlib only" everywhere else, `no new runtime dependency (CON-001)") makes this the
single external surface, which is exactly the one worth pinning.

### A2. The guard's message is advice that cannot work — the §A2 family, one release later

`tamheed_server.py:970-971` and `:983-986`:

```python
except ImportError:
    print(_SDK_ERROR, file=sys.stderr)      # "requires the 'mcp' SDK … or 'pip install mcp'"
```

The SDK **is** installed. It is the wrong major. The message sends the reader to install the very
thing that is already present and is the cause — and it swallows the `ModuleNotFoundError` that says
so in one line. I lost roughly an hour to this and reached three confident wrong conclusions before
patching the guard on a copy to see the real exception; the truth was one `traceback.print_exc()`
away the whole time.

This is precisely the class `findings_10 §A2` raised and 2.7.0 fixed elsewhere: an error message that
states something untrue about the system. The C31 work made `entity_query` stop calling a writable
type "unknown"; this guard still tells an operator to install a package they already have.

**Suggested fix:** print the caught exception alongside the hint, and distinguish *absent* from
*incompatible* — e.g. `mcp is installed at <version> but does not provide mcp.server.fastmcp; this
build requires mcp<2`. Cheap, and it converts an hour into a minute.

## B. Retraction — `findings_11.md` §C was wrong

`findings_11.md` §C ("Unexpected — one, and it is not a Tamheed defect") states that the MCP server's
failure to reconnect was a **harness-side reconnect failure** and explicitly not a plugin fault. That
conclusion is **retracted**. The cause is §A1 above: the server could not start at all, because its
`serve()` import fails on SDK 2.0.0.

Retracted in place here rather than by editing that report, per the protocol `findings_4` set.
**Scope of the retraction, stated precisely so the rest is not discarded:**

- **§C only.** The §A verdict table (A1–A4 fixed), §B (C1 and D), and §D (threads continued) were all
  verified **in-process** — importing the module and calling the tool functions — and are unaffected
  by a transport that never started. Every one of those results still stands.
- The §C caveat I wrote at the time — *"this run verifies the tool functions and the store, not the
  MCP transport layer"* — turned out to be exactly the right hedge. It is what keeps the report's
  §A/§B valid; the error was in the sentence next to it, which drew a conclusion about a layer I had
  just said I had not tested.

**What led me wrong, recorded because the pattern repeats.** Three confident diagnoses, in order:
`.mcp.json` changed (it is byte-identical); the plugin needed re-authentication (a
`mcp-needs-auth-cache.json` entry — which **regenerated with a fresh timestamp after the restart**,
proving it was a symptom of each failed connect, not a cause); an unpinned SDK resolving to something
without `fastmcp` (right conclusion, reached for the wrong reason, and only confirmed once I stopped
hypothesising and printed the exception). The measured answer arrived only when the guard was
bypassed. **Reading a tool's error message is not evidence of the tool's behaviour** — the same
sentence `findings_10` closed on, and the second time this project has paid for it.

## C. Positives worth keeping exactly as they are

- **The defect is not in anything C31 changed.** `store.py`, the gates, the tool functions and the
  fixes verified in `findings_11` are all sound; 2.7.0 remains a good release wearing an external
  break. Worth stating plainly so the release is not judged by this.
- **Handlers being plain functions saved the day.** The module's own posture — *"Tool handlers are
  plain functions (in-process testable, no transport needed)"* — is what allowed a full C31
  verification while the transport was dead. That design choice earned its keep this week.
- **`--selftest` starts in 358 ms** and lists all 15 tools without importing the SDK. Useful, and
  worth knowing it proves nothing about serving: it is the one code path that skips the broken import.

## D. Asks, in priority order

1. **§A1 — bound the `mcp` dependency.** One line, and until it ships the plugin does not start for
   anyone whose environment resolves fresh. This outranks everything in `findings_10 §F`, all of
   which is now delivered.
2. **§A1 follow-up — port `serve()` to `mcp.server.mcpserver`** deliberately, on its own schedule,
   once the pin has bought the time.
3. **§A2 — make the guard print the caught exception** and distinguish absent from incompatible.
4. Consider whether `--selftest` should optionally exercise the SDK import, so "the server is
   healthy" cannot be concluded from a check that skips the only thing that was broken.

## E. Verdict

An external release broke a shipped guarantee through the one unbounded dependency in an otherwise
stdlib-only plugin, and the failure mode is the worst kind: **silent to the operator, fatal to the
process, and invisible to every diagnostic the plugin offers** — `--selftest` passes, `server_info`
returns 2.7.0 in-process, the launch config is unchanged, and the only thing that fails is the one
import no health check touches.

The fix is a character class. The lesson is smaller and older than the fix: the guard knew the answer
and printed a hint instead. This project has now written that sentence twice, in two consecutive
reports, about two different messages — which is the argument for treating error text as part of the
data contract rather than as UX polish.
