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
| **No MCP host** | File read/write only (e.g. a chat-only environment) | ⚠️ planning conversation only | ❌ no package store — v2 packages need the server |

Python **≥3.10** is required for the MCP server (the `mcp` SDK's floor; ASM-D). `uv` launches it with
zero setup (PEP 723), or `pip install mcp` as the fallback — see
[`../plugins/tamheed/server/README.md`](../plugins/tamheed/server/README.md).
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
later: `/plugin marketplace update tamheed`.

To try it before installing (no marketplace needed):

```text
claude --plugin-dir ./plugins/tamheed
```

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
# everything CI runs — 7 suites, v1 goldens, structure lint, canonical form, eval sample
python check.py

# the MCP server's tool surface (uv fetches the SDK via PEP 723; no install step)
uv run plugins/tamheed/server/tamheed_server.py --selftest

# validate a *v1* package against the frozen v1 gate engine (migration contract)
python plugins/tamheed/scripts/validate_package.py generated-samples/support-triage-agent
```
