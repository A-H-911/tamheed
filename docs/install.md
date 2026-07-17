# Installing Keystone

Keystone ships as a self-contained bundle at [`../plugins/tamheed/`](../plugins/tamheed). Everything the
skill reads or invokes at runtime lives inside that one directory, so it installs and runs as a single intact
unit. Pick the path that matches your tool.

## Capability tiers

What works depends on whether the agent can read files and run local processes:

| Tier | Environment | Planning &amp; package generation | Tamheed MCP server (the write path) |
|---|---|---|---|
| **Full** | Claude Code, or any MCP-capable agent with a shell/Python | ✅ | ✅ auto-starts via the bundled `.mcp.json` |
| **No MCP host** | File read/write only | ⚠️ planning conversation only | ❌ no package store — v2 packages need the server |

Python **≥3.10** is required for the MCP server (the `mcp` SDK's floor; ASM-D). `uv` launches it with
zero setup (PEP 723), or `pip install mcp` as the fallback — see `plugins/tamheed/server/README.md`.
No specific model, vendor, or repo provider is required. (The v1 repository bootstrapper was removed in
v2 — ASM-B.)

## Claude Code — plugin (recommended)

This repository is its own plugin marketplace (see [`../.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json)).

```text
/plugin marketplace add A-H-911/keystone
/plugin install keystone@keystone
```

Invoke it as **`/keystone:keystone`** — plugin skills are namespaced by the plugin name. Or just describe a
planning task; the skill's description triggers it automatically. To update later: `/plugin marketplace update keystone`.

To try it before installing (no marketplace needed):

```text
claude --plugin-dir ./plugins/tamheed
```

## Claude Code — manual / standalone

Copy the bundle into a skills directory to get the shorter, un-namespaced `/keystone`:

```text
# user scope (available in every project)
~/.claude/skills/keystone/          ← the contents of plugins/tamheed/

# or project scope (this repo only)
<your-repo>/.claude/skills/keystone/
```

```bash
# example, user scope
mkdir -p ~/.claude/skills/keystone
cp -r plugins/tamheed/* ~/.claude/skills/keystone/
```

## Claude.ai / Agent Skills

Upload the `plugins/tamheed/` folder as an Agent Skill. It has `SKILL.md` at its root and follows the
tool-agnostic [Agent Skills](https://agentskills.io) standard. Script execution depends on the environment
(see the capability tiers above).

## Other agents (generic)

Any agent that can read files can use Keystone: point it at `plugins/tamheed/SKILL.md` and let it load the
`references/`, `templates/`, and `schemas/` beside it on demand. The bundle is self-contained, so copying the
folder is all that's needed. Local script execution (repo bootstrap, validation) requires a shell/Python.

## Verifying a local checkout

```bash
# validator self-test (stdlib only)
python tests/test_validate_package.py

# validate a generated package
python plugins/tamheed/scripts/validate_package.py <package-dir>

# preview a repo bootstrap without writing anything
uv run plugins/tamheed/server/tamheed_server.py --selftest
```
