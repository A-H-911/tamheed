"""findings_36 review, revision 2 (read-only): calibrate the instruments behind M1-M4.

Questions this answers, each over EVERY transcript under ~/.claude/projects:
  C1  per (entrypoint, build): transcripts, how many hold a SessionStart hook row, how many hold
      ANY hook attachment row at all (if a build writes no hook rows of any event, a zero for
      SessionStart is the instrument's limit, not a finding).
  C2  the `cli` transcripts with no SessionStart row: size and first/last timestamps.
  C3  hook_success rows with BOTH stdout and stderr empty: do they exist, for which commands?
      (decides whether "a silent run leaves no row" is specific to one hook or general).
  C4  tamheed hook rows: count, by emptiness of stdout.
"""
import collections
import json
from pathlib import Path

ROOT = Path.home() / ".claude" / "projects"

by_kind = collections.defaultdict(lambda: {"n": 0, "ss": 0, "anyhook": 0})
cli_no_ss = []
empty_rows = collections.Counter()
nonempty_rows = collections.Counter()
tamheed = collections.Counter()
hook_events_by_ep = collections.defaultdict(collections.Counter)

for f in ROOT.glob("*/*.jsonl"):
    ep = ver = first = last = None
    ss = anyhook = rows = 0
    try:
        with f.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                rows += 1
                if '"attachment"' not in line and ep is not None:
                    if '"timestamp"' in line:
                        i = line.find('"timestamp":"')
                        if i >= 0:
                            last = line[i + 13:i + 37]
                    continue
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if ep is None and r.get("entrypoint"):
                    ep, ver = r.get("entrypoint"), r.get("version")
                t = r.get("timestamp")
                if t:
                    first = first or t
                    last = t
                a = r.get("attachment") or {}
                typ = str(a.get("type") or "")
                if not typ.startswith("hook"):
                    continue
                anyhook += 1
                ev = str(a.get("hookEvent") or a.get("hookName") or "")
                hook_events_by_ep[(r.get("entrypoint"), r.get("version"))][ev.split(":")[0]] += 1
                if ev.startswith("SessionStart"):
                    ss += 1
                if typ == "hook_success":
                    cmd = str(a.get("command"))[:60]
                    out = str(a.get("stdout") or "").strip()
                    err = str(a.get("stderr") or "").strip()
                    if not out and not err:
                        empty_rows[cmd] += 1
                    else:
                        nonempty_rows[cmd] += 1
                    if cmd.startswith("tamheed: reading"):
                        tamheed["printed" if out else "empty"] += 1
    except OSError:
        continue
    k = by_kind[(ep, ver)]
    k["n"] += 1
    k["ss"] += 1 if ss else 0
    k["anyhook"] += 1 if anyhook else 0
    if ep == "cli" and not ss:
        cli_no_ss.append((f.parent.name[-30:], f.stem[:8], rows, first, last))

print("C1 (entrypoint, build): transcripts / with SessionStart row / with any hook row")
for key, v in sorted(by_kind.items(), key=str):
    print("  ", key, v["n"], v["ss"], v["anyhook"])
print("C1b hook events seen, by (entrypoint, build)")
for key, c in sorted(hook_events_by_ep.items(), key=str):
    print("  ", key, dict(c))
print("C2 cli transcripts with no SessionStart row")
for x in cli_no_ss:
    print("  ", x)
print("C3 hook_success rows with stdout AND stderr empty:", sum(empty_rows.values()))
for cmd, n in empty_rows.most_common(12):
    print("  ", n, repr(cmd), "| same command non-empty:", nonempty_rows.get(cmd, 0))
print("C4 tamheed hook rows:", dict(tamheed))
