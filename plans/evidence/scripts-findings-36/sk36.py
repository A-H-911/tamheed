"""findings_36 review (read-only): a third instrument for the SDK-Python question.

A transcript that records no hook row of any event cannot say whether a hook ran. What the
harness LISTED to the model can: a session that loaded plugins names their skills and tools in
its own listing attachments. For every transcript, by (entrypoint, build):
  - how many carry a skill listing at all;
  - how many of those name at least one plugin skill (a `name:skill` prefix) or a plugin MCP tool.
"""
import collections
import json
import re
from pathlib import Path

ROOT = Path.home() / ".claude" / "projects"
LISTS = ("skill_listing", "deferred_tools_delta", "agent_listing_delta", "mcp_instructions_delta")
PLUGIN = re.compile(r"\b[a-z][a-z0-9-]+:[a-z][a-z0-9-]+\b|mcp__plugin_")

out = collections.defaultdict(lambda: {"n": 0, "listed": 0, "plugin": 0, "tamheed": 0})
for f in ROOT.glob("*/*.jsonl"):
    ep = ver = None
    listed = plugin = tamheed = False
    try:
        with f.open(encoding="utf-8", errors="replace") as fh:
            for n, line in enumerate(fh):
                if n > 60:
                    break
                if '"attachment"' not in line and ep is not None:
                    continue
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if ep is None and r.get("entrypoint"):
                    ep, ver = r.get("entrypoint"), r.get("version")
                a = r.get("attachment") or {}
                if a.get("type") in LISTS:
                    blob = json.dumps(a)
                    if a.get("type") == "skill_listing":
                        listed = True
                        if PLUGIN.search(blob):
                            plugin = True
                        if "tamheed:" in blob:
                            tamheed = True
                    elif "mcp__plugin_" in blob:
                        plugin = True
    except OSError:
        continue
    k = out[(ep, "2.1.204" if ver == "2.1.204" else "other builds")]
    k["n"] += 1
    k["listed"] += listed
    k["plugin"] += plugin
    k["tamheed"] += tamheed

print("(entrypoint, build): transcripts / with a skill listing / naming a plugin / naming tamheed")
for key, v in sorted(out.items(), key=str):
    print("  ", key, v["n"], v["listed"], v["plugin"], v["tamheed"])
