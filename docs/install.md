# Installing Tamheed

Tamheed ships as a self-contained bundle at [`../plugins/tamheed/`](../plugins/tamheed). Everything the
skill reads or invokes at runtime lives inside that one directory, so it installs and runs as a single intact
unit. Pick the path that matches your tool.

> Arriving from **Keystone** (the frozen v1 predecessor)? Existing v1 packages keep working with the
> [old repository](https://github.com/A-H-911/keystone); when you're ready, follow the migration runbook:
> [`migrate-from-keystone.md`](migrate-from-keystone.md).

## Capability tiers

What works depends on whether the agent can run the MCP server:

| Tier | Environment | Planning &amp; package generation | Tamheed MCP server (the write path) |
|---|---|---|---|
| **Full** | Claude Code, or any MCP-capable agent with a shell/Python | ✅ | ✅ auto-starts via the bundled `.mcp.json` |
| **No MCP host** | File read/write only (e.g. a chat-only environment) | ⚠️ planning conversation only | ❌ no package store — packages need the server |

Python **≥3.10** is required for the MCP server (the `mcp` SDK's floor; ASM-D). `uv` launches it with
zero setup (PEP 723), or `pip install "mcp<2"` as the fallback — see
[`../plugins/tamheed/server/README.md`](../plugins/tamheed/server/README.md).
Install `uv` once per machine: <https://docs.astral.sh/uv/getting-started/installation/> (`pipx install uv`,
`winget install astral-sh.uv`, or the one-line installer).
No specific model, vendor, or repo provider is required. (The v1 repository bootstrapper was removed in
v2 — ASM-B; the chat-only generation path ended with v1.)

## Claude Code — plugin (recommended)

This repository is its own plugin marketplace (see [`../.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json)).

```text
/plugin marketplace add A-H-911/tamheed
/plugin install tamheed@tamheed
```

Invoke the front door as **`/tamheed:tamheed`** — plugin skills are namespaced by the plugin name (since
v5 it lives at `skills/tamheed/SKILL.md`, beside the plugin's other skills). Or just describe a planning
task; the skill's description triggers it automatically. The plugin also ships the execution surface:
eight discipline skills, model-invoked and named by the note and the tool results (`tamheed:package-writes`,
`tamheed:reading-the-record`, `tamheed:operator-interview`, `tamheed:written-claims`, `tamheed:test-evidence`,
`tamheed:measurement-evidence`, `tamheed:ci-evidence`, `tamheed:session-handoff`) and sixteen operator-invoked scenario skills
(`/tamheed:orient-resume`, `/tamheed:slice-kickoff`, `/tamheed:progress-sync`, … — the emitted
`<package>/prompts/README.md` maps every situation). Since v5.1 seven of the eight are hidden
from the `/` menu (`user-invocable: false`) and the eighth, `/tamheed:session-handoff`, takes both routes.

**Project-only enablement (the field's FB-022, measured).** `enabledPlugins` merges **key by key across
scopes** — the highest-precedence scope that mentions the plugin id wins (user < project < local). A
`true` at user scope therefore reaches every project, and adding a project entry alone never narrows it.
To enable tamheed for one project only: install (or enable) it at **project scope from the start**
(`claude plugin install tamheed@tamheed --scope project`), or, when it is already enabled at user scope,
**disable it there first, then enable it at project scope** — `claude plugin disable tamheed@tamheed
--scope user`, then `claude plugin enable tamheed@tamheed --scope project`, which writes
`{"enabledPlugins": {"tamheed@tamheed": true}}` into `.claude/settings.json`. Run in that order: the
enable command checks the merged effective state, not the project file, and refuses "already enabled at
project scope" while the user entry exists (a Claude Code bug, reported 2026-09-25); between the disable
and the enable the project has no plugin, so do it with no package open. A project without a package
sees only the discipline descriptions, which never fire without one. When Claude Code asks to approve the
`tamheed` MCP server (per-server approval), say yes — it is the only write path into a package. To update
later, see [Upgrading](#upgrading-an-installed-plugin) — refreshing the marketplace alone does not update the plugin.

To try it before installing (no marketplace needed):

```text
claude --plugin-dir ./plugins/tamheed
```

**The SessionStart hook (v5.1).** The plugin ships one hook (`hooks/hooks.json`): on every session
start, resume, clear, compaction and fork it runs `server/resume_hook.py` (stdlib, ~0.1 s through
`uv run --no-project`, plus the lockless load of the package) and prints the package's **resume block**
— the latest `handoff` journal entry with its corrections, how many work entries followed it, the
open feedback and slices, the lock holder and the next step — into the model's context. It prints
nothing in a project whose `CLAUDE.md` (or one `@`-imported file) carries no tamheed note, withholds an
instruction-shaped handoff, caps itself at 40 lines (up to 25 lines / 4,000 characters of the entry
itself — the resume block's own cap, since v5.2), and on any failure prints one line and exits 0.
Its lock line says what the store observed about the holder (v5.3): after a Claude Code process
restart the previous server's pid is dead, and the line reads `holder observed not-running —
package_unlock(confirm=true) on the operator's word`. **Tracing the hook (v5.3, opt-in):** create an
empty file outside any package, set `TAMHEED_HOOK_LOG` to its path (your shell, or the `env` block of
your USER settings), and every run appends one line — `<utc> version=<x>
source=<startup|resume|clear|compact|fork> lines=N chars=N status=printed|silent|error:<Class>
session=<id>` — never the entry's text. **`version=` (v5.6)** is the hook's own release, read from
the bundle's manifest before any note is looked for, so a silent line carries it too: a running
session keeps the hook it loaded, and only the line says which one ran. A line with no
`version=` was written by a hook older than 5.6.0; a value that is not a plain token is written
`-`. The field sits right after the timestamp and not at the end, where a new key usually goes,
because the tail is this line's documented instrument; read the line by key, never by position.
The `session=` tail (v5.4) is the event's own `session_id`, which is also the file name of that
session's transcript under `~/.claude/projects/<project>/`; a value that is absent or not a plain
token is written `-`. **Attribute a line by its `session=`, never by its counts:** every session
that runs the plugin's hook in the folder prints the same block, and that includes headless
sessions another tool starts there (a summariser, a scheduled run) — the field read a verdict about
the operator's session from such a line, equal to a replay of the block to the character. A line
carrying YOUR session's id with no block in your context means the hook ran and the output was not
delivered; no line with your id means it did not run in your session — read that only once a run
you know delivers (a compaction) has written a line with your id, which proves the variable reaches
the hook at all. **Who writes a line (v5.5, measured on one machine, Claude Code builds 2.1.204
to 2.1.283):** a session that LOADED the plugin, in a project that enables it, running a hook of
5.3.0 or later. Enablement is read where the session STARTS: Claude Code's settings page says it
"reads the shared .claude/settings.json from the session's primary working directory, so to use
a file committed at the repository root, start Claude Code there". A session started in a
subfolder of an enabling project therefore loads no plugin. The field saw it once (v5.6): another
tool's headless session inherited a shell that had moved into a scratch folder, listed no
plugin's skill to its model, and wrote no line — so a missing line does not show that such a
session did not run. The field confirmed the rule with its own method, the skill listing in each
transcript. Every interactive and every headless command-line session there did. Sessions
another tool started through the Agent SDK's Python entry did not: over six hundred of them, and
not one listed a plugin's skill to its model, so no plugin hook was there to run. Whether an SDK
session loads a project's settings is its caller's choice (the SDK's `settingSources` option), so
this page promises neither. A running session keeps the plugin version it loaded until a reload
or a restart (Claude Code's plugin loading reference: "The running session keeps the versions it
loaded"), so a session started before 5.3.0 was installed writes no line until then. A project
with no tamheed note writes `lines=0 chars=0 status=silent`; a project where the plugin is
disabled writes none, and neither does a session started below the folder that enables it. **Cross-check in the transcript:** `~/.claude/projects/<project>/<id>.jsonl`
holds a `SessionStart` hook row whose `command` is the hook's status message ("tamheed: reading
the package's resume state...") within about a second of a `printed` line. A `silent` run leaves
NO row: no transcript on the measured machine holds a hook row whose stdout and stderr are both
empty, so for a silent line the tail is the only attribution. Versions of this page before 5.5.0
said every session in an enabling project appends a line; that was a rule, not a count. The file
is yours to truncate. A headless session that loads the plugin receives the resume block as any
session does: Claude Code gives a hook no documented way to tell the two apart.
Opt-out: disable the plugin for that project (`enabledPlugins`, the FB-022 recipe above) — that is
the only per-plugin switch; `disableAllHooks` in the project's settings disables EVERY hook of every
tool you run there, not just this one. If your
Claude Code build drops plugin `SessionStart` output (a bug reported against early-2026 builds;
measured working on 2.1.283), the same command works as a user or project hook in `settings.json`:

```json
{"hooks": {"SessionStart": [{"matcher": "startup|resume|clear|compact|fork",
  "hooks": [{"type": "command",
             "command": "uv run --no-project \"${CLAUDE_PLUGIN_ROOT}/server/resume_hook.py\"; exit 0",
             "timeout": 10}]}]}}
```

(outside a plugin, replace `${CLAUDE_PLUGIN_ROOT}` with the installed plugin's path). The same block
is returned by `package_open` and `server_info`, so nothing is lost without the hook — it is the
free copy after a compaction.

## Upgrading an installed plugin

Refreshing the marketplace only refreshes the catalog; the installed plugin is a second step, and
the running MCP server keeps the old code until the plugin is reloaded (`/reload-plugins` —
observed sufficient in the field for the MCP server three times, on 5.1.0, 5.2.0 and 5.3.0 — or a
full Claude Code restart).

```text
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed      # "restart required to apply"
```

Updated skills in a cached marketplace plugin arrive with `/reload-plugins` (documented since
2026-09: "apply pending plugin changes to the running session without restarting it" — plugins,
skills, hooks and MCP servers; closing the `/plugin` panel with pending changes runs it for you; a
reload that would add or remove an MCP server is refused without `--force`) followed by
`/reload-skills` (measured in the field on 5.1.0 — the model's skill listing showed the new set — and
still undocumented). **A plugin reload does not run `SessionStart`.** Measured 2026-09-27 over every
session transcript on the maintainer's machine: 24 reloads on Claude Code builds 2.1.261 to 2.1.283,
in three sessions of one project, and no `SessionStart` event of ANY plugin's hook within 30
seconds of any of them. Where one followed within minutes it has its own cause on the record: a
compaction the operator entered 5 seconds after the reload, and the restart described next. After
the other 22 the next one, where one followed at all, came no sooner than 41 minutes later. The control: each of 19
compactions ran them. Versions of this page before 5.4.0 said a reload on
5.1.0 delivered the resume block as `SessionStart:resume`. That delivery was a Claude Code
**restart**: the reload's records carry build 2.1.282, and the `SessionStart:resume` 37 seconds
later is that session's first record on 2.1.283. What a reload does do for the hook is documented
(Claude Code's plugin loading reference: after an update, hook commands "keep using the previous
version's path. Run `/reload-plugins` to switch hooks, MCP servers, and LSP servers to the new
path") and was observed once (2.1.283): the first `SessionStart` after the 5.3.0 reload ran the
5.3.0 hook, with no restart between. Whether a reload FIRES `SessionStart` is stated on no page;
the 24 reloads above are the evidence. So after an upgrade by reload the block reaches the agent through `package_open` /
`server_info` (the same block), and through the hook at the next restart, resume, clear or
compaction. A build newer than those measured may differ; the trace's `session=` settles it in one
line.
Claude Code's size cap on a hook's stdout is undocumented but exists (its changelog for 2.1.283
counts "oversized outputs saved to a file"); a 3,615-character block was measured arriving whole.

(In a session: `/plugin marketplace update tamheed`, then `/plugin` → Installed → tamheed → update.)
Reload or restart, then check `~/.claude/plugins/cache/tamheed/tamheed/<version>/` exists. That
folder says the release is INSTALLED, never that a session runs it: the previous version's folder
stays beside it (Claude Code's plugin loading reference: an update "writes an .orphaned_at marker
into the previous version directory. It removes that directory in a background cleanup 14 days
later, so a session that already loaded the old version keeps running"). Three readings say what
runs (v5.6): `server_info()` names the MCP server's version, a trace line's `version=` the
hook's, and `package_verify()`'s `review_exported_by` the release that exported the review page.
To check
the installed tree against a release tag, compare through git or on LF-normalised bytes, and leave
out the run-time folders (`__pycache__/`, `.in_use/`): on Windows the marketplace clone checks out
with CRLF, and a byte compare then reads EVERY file as different (the field measured 86 of 86,
each file's size gap equal to its count of carriage returns). If the
tools are unreachable afterwards, run the self-test before diagnosing anything else — it
registers the whole tool surface and exits 1 on failure:
`uv run <that cache dir>/server/tamheed_server.py --selftest`. Prefer the interpreter the LIVE
server uses: a bare `uv run` may resolve a fresh environment and describe a configuration
that is not the one in service.

**Around the upgrade, in a repo that carries a package** (all through the MCP tools):

1. *Before:* commit the package (that commit is the rollback), `package_close()` in whichever
   session holds the lock, and keep a
   baseline of `gate_run()`, `readiness_check("package")` and `package_verify()`.
2. *After:* `server_info()` names the new version. With no package open,
   `package_migrate(name)` previews any registry sync or relocate; on a current store it answers
   "nothing to migrate", which is the happy path. A MAJOR release says so in the CHANGELOG; when it
   changes the store's shape, `package_open` refuses until the staged migration runs — **5.0.0 does
   not**: it changes the handoff contract, the store stays v4-shaped (`schema_version` reads 6 after
   migration `006_carries.sql`, applied at connect with no operator step). **5.1.0 does not either**:
   `007_handoff.sql` (the `handoff` journal kind, `skills.upstreamed_to`) applies at connect,
   `schema_version` reads 7, and `skills.jsonl` rewrites once on the first store WRITE (every
   table is written on every commit; the first `package_verify` before that write reads
   `verified: false, dirty: ["skills.jsonl"]`, as the field measured) — every column serialises,
   so each row gains `"upstreamed_to": null`; commit it with the rest. **5.2.0 changes no store
   shape either**: no migration, `schema_version` stays 7, no JSONL rewrite.
   **If the holder is already gone** (the usual state after an upgrade: reloading ends the
   session that held the lock) there is nothing to `package_close()`. The refusal itself says
   what the store observed about the holder; `package_unlock(name)` reports it on demand, and
   `package_unlock(name, confirm=true)` — the operator's words — removes a lock whose holder was
   observed `not-running` or `reused`, journaled. It refuses on `alive` and `unobservable`
   (another host, a container): there, removing `data/.lock` by hand stays the deliberate path.
3. `package_open(name)`, then `gate_run()` / `readiness_check("package")` — compare with the baseline.
4. `handoff_emit(target_dir, refresh_stock=true)` — refreshes the operator guide when you never
   customised it, re-renders the tool-owned note (v5 since 5.0.0: obligations + lessons, the
   cheat-sheet gone, the plugin's skills named) and **deletes the retired 4.x scenario files that
   are byte-equal to a shipped release** (reported `retired`; a customised copy is kept and named —
   keep it as a project prompt under a new name, or delete it yourself). A customised guide is
   listed with the release its stock last changed, for a hand-merge. Never reach for `force` to get
   there.
5. `export_html()` — `review.html` and `csv/` are derived and deterministic, so a release that
   changes rendering shows up as a one-time diff if you track them (4.8.0: formula-shaped CSV
   cells are quote-prefixed, ids order numerically). Until that export `package_verify()` reads
   `review_current: true` over the page the OLDER release wrote — the key compares the digest
   stamped in the page, so it says the page's data is current and nothing about its exporter;
   `review_exported_by` (v5.6) names the release that exported it, and reads `null` on a page
   exported before 5.6.0. Export after the LAST write of the close-out and before the commit that
   carries the page (`tamheed:package-writes`). `data/*.jsonl` must not change from an idle
   open and close; `package_verify()` confirms it.

## Claude Code — manual / standalone

Copy the bundle into a skills directory. Because the bundle carries `.claude-plugin/plugin.json`, the
docs say it loads there as a plugin named `tamheed@skills-dir`; whether that route discovers the nested
`skills/` directory (the front door and the execution skills since v5) is not documented and was not
measured — the marketplace route above is the supported one.

```text
# user scope (available in every project)
~/.claude/skills/tamheed/           ← the contents of plugins/tamheed/

# or project scope (this repo only)
<your-repo>/.claude/skills/tamheed/
```

```bash
# example, user scope
mkdir -p ~/.claude/skills/tamheed
cp -r plugins/tamheed/* ~/.claude/skills/tamheed/
```

## Other MCP-capable agents (generic)

Any agent that can read files *and run MCP servers* can use Tamheed: point it at
`plugins/tamheed/skills/tamheed/SKILL.md`, let it load the bundle's `references/` on demand, and register the server from
`plugins/tamheed/.mcp.json` (or launch `server/tamheed_server.py --package-dir <root>` yourself). The
bundle is self-contained, so copying the folder is all that's needed. Without an MCP host the methodology
is readable but packages cannot be created — see the capability tiers above.

## Verifying a local checkout

```bash
# everything CI runs — the 8 suites, the lint battery, canonical form, eval fixtures
python check.py

# the MCP server's tool surface (uv fetches the SDK via PEP 723; no install step)
uv run plugins/tamheed/server/tamheed_server.py --selftest
```
