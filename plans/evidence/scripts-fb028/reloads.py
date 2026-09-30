"""M78 (plans 170-174): every session transcript on this machine that ran `/reload-plugins`,
and every `deferred_tools_record` in those sessions that lists tamheed's `progress_update`,
tagged by which release's description text the record carries. Read-only. Prints counts, ids,
timestamps, builds and text tags only - never a transcript's prose.

The question it answers: how many reloads happened inside a client process that spans a change
of a tamheed tool description? (One: the field's, session 5bc5eab5, 2026-09-30.)

Run:  PYTHONIOENCODING=utf-8 python reloads.py [<projects dir>]   (default ~/.claude/projects)
"""
import glob
import json
import os
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.claude/projects")
TOOL = "mcp__plugin_tamheed_tamheed__progress_update"
TAGS = (("5.8.0", "`entries` is a list"), ("5.7.0", "Each item is an object"),
        ("<=5.6.1", "Append progress entries (execution tracking)"))


def tag(text):
    return next((t for t, needle in TAGS if needle in text), "?")


hits = []
for f in sorted(glob.glob(os.path.join(ROOT, "*", "*.jsonl"))):
    reloads, records, builds = [], [], set()
    with open(f, encoding="utf-8", errors="replace") as fh:
        for n, line in enumerate(fh, 1):
            if "/reload-plugins" in line and "<command-name>" in line:
                o = json.loads(line)
                content = (o.get("message") or {}).get("content")
                # the local-command row itself, not a tool input that quotes the tag
                if o.get("type") == "user" and isinstance(content, str) \
                        and content.lstrip().startswith("<command-name>/reload-plugins"):
                    reloads.append((n, o.get("timestamp", "")[:19], o.get("version")))
            elif "deferred_tools_record" in line and TOOL in line:
                o = json.loads(line)
                records.append((n, o.get("timestamp", "")[:19], o.get("version"),
                                tag(json.dumps(o.get("attachment", {})))))
            if '"version"' in line[:800]:
                try:
                    v = json.loads(line).get("version")
                    if v:
                        builds.add(v)
                except Exception:
                    pass
    if reloads:
        hits.append((os.path.relpath(f, ROOT), sorted(builds), reloads, records))

# The plugin updates that changed a tamheed description, from installed_plugins.json's
# lastUpdated (5.7.0: three descriptions; 5.8.0: two). A reload SPANS such an update when the
# session recorded the tool before the update and reloaded after it: the record after the
# reload then shows whether the reload rebuilt the listing.
UPDATES = (("5.7.0", "2026-09-29T06:08:28"), ("5.8.0", "2026-09-30T19:41:41"))

print(f"sessions with /reload-plugins: {len(hits)}")
spanning = []
for f, builds, reloads, records in hits:
    print(f"\n{f}  builds {builds}  reloads {len(reloads)}  tamheed records {len(records)}")
    for n, ts, v in reloads[:6]:
        print(f"  reload   line {n} {ts} build {v}")
    for n, ts, v, t in records[:12]:
        print(f"  record   line {n} {ts} build {v} text {t}")
    for n, ts, v in reloads:
        # the newest description-changing update before this reload, if the session had
        # recorded the tool before that update
        spanned = [rel for rel, u in UPDATES if u < ts and any(r[1] < u for r in records)]
        if spanned:
            after = [(r[0], r[1], r[3]) for r in records if r[1] > ts][:2]
            spanning.append((f, n))
            print(f"  SPANS the {spanned[-1]} update: reload line {n} {ts}; records after it: {after}")
print(f"\nreloads inside a session that spans a description-changing update: {len(spanning)}")
