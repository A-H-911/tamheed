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

Invoke it as **`/tamheed:tamheed`** — plugin skills are namespaced by the plugin name. Or just describe a
planning task; the skill's description triggers it automatically. When Claude Code asks to approve the
`tamheed` MCP server (per-server approval), say yes — it is the only write path into a package. To update
later, see [Upgrading](#upgrading-an-installed-plugin) — refreshing the marketplace alone does not update the plugin.

To try it before installing (no marketplace needed):

```text
claude --plugin-dir ./plugins/tamheed
```

## Upgrading an installed plugin

Refreshing the marketplace only refreshes the catalog; the installed plugin is a second step, and
the running MCP server keeps the old code until Claude Code restarts.

```text
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed      # "restart required to apply"
```

(In a session: `/plugin marketplace update tamheed`, then `/plugin` → Installed → tamheed → update.)
Restart Claude Code, then check `~/.claude/plugins/cache/tamheed/tamheed/<version>/` exists. If the
tools are unreachable after the restart, run the self-test before diagnosing anything else — it
registers the whole tool surface and exits 1 on failure:
`uv run <that cache dir>/server/tamheed_server.py --selftest`.

**Around the upgrade, in a repo that carries a package** (all through the MCP tools):

1. *Before:* commit the package (that commit is the rollback), `package_close()` in whichever
   session holds the lock — the store never guesses that a `data/.lock` is stale — and keep a
   baseline of `gate_run()`, `readiness_check("package")` and `package_verify()`.
2. *After:* `server_info()` names the new version. With no package open,
   `package_migrate(name)` previews any registry sync or relocate; on a current store it answers
   "nothing to migrate", which is the happy path. A MAJOR release says so in the CHANGELOG and
   `package_open` refuses until the staged migration runs.
3. `package_open(name)`, then `gate_run()` / `readiness_check("package")` — compare with the baseline.
4. `handoff_emit(target_dir, refresh_stock=true)` — refreshes only the stock prompts you never
   customised and re-renders the tool-owned note; customised prompts are listed with the release
   their stock last changed, for a hand-merge. Never reach for `force` to get there.
5. `export_html()` — `review.html` and `csv/` are derived and deterministic, so a release that
   changes rendering shows up as a one-time diff if you track them (4.8.0: formula-shaped CSV
   cells are quote-prefixed, ids order numerically). `data/*.jsonl` must not change from an idle
   open and close; `package_verify()` confirms it.

## Claude Code — manual / standalone

Copy the bundle into a skills directory to get the shorter, un-namespaced `/tamheed`:

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
`plugins/tamheed/SKILL.md`, let it load the `references/` beside it on demand, and register the server from
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
