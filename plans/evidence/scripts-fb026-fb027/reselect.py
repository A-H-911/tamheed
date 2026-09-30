"""M71 (plans 165-169): a ToolSearch `select:` of a tool the session had ALREADY recorded in
the same context (no compaction between) - did a new record follow within two minutes? Split
by whether a `--resume` happened between the record and the re-select. Counts only.

Run:  PYTHONIOENCODING=utf-8 python reselect.py <projects root>
HORIZON: the harness sweeps old transcripts; counts hold for the day they were taken.
"""
import json, sys, glob, collections, os
sys.stdout.reconfigure(encoding="utf-8")
c = collections.Counter(); ex = []
for f in glob.glob(os.path.join(sys.argv[1], "*", "*.jsonl")):
    epoch = 0; rec = {}; resumed_since = set(); pending = []; done = []  # pending: (names, ts, resumed?)
    try:
        lines = open(f, encoding="utf-8", errors="replace")
    except Exception:
        continue
    for l in lines:
        if "compact_boundary" not in l and "SessionStart:resume" not in l and "deferred_tools_record" not in l and "select:" not in l:
            continue
        try:
            o = json.loads(l)
        except Exception:
            continue
        ts = o.get("timestamp", "")
        if o.get("type") == "system" and o.get("subtype") == "compact_boundary":
            epoch += 1; rec = {}; resumed_since = set(); done += pending; pending = []; continue
        if o.get("type") == "attachment":
            a = o["attachment"]
            if a.get("type") == "hook_success" and a.get("hookName") == "SessionStart:resume":
                resumed_since = set(rec)      # tools recorded before this resume
            elif a.get("type") == "deferred_tools_record":
                names = {e.get("name") for e in a.get("entries", [])}
                for p in pending:
                    hit = p["names"] & names
                    if hit and ts[:16] <= p["ts"][:16] + "z" and ts[:13] == p["ts"][:13] and abs(int(ts[14:16]) - int(p["ts"][14:16])) <= 2:
                        p["rerecorded"] |= hit
                for n in names:
                    rec[n] = ts
            continue
        if o.get("type") == "assistant":
            for b in o.get("message", {}).get("content", []) or []:
                if b.get("type") == "tool_use" and b.get("name") == "ToolSearch":
                    q = str(b.get("input", {}).get("query", ""))
                    if q.startswith("select:"):
                        names = {n.strip() for n in q[7:].split(",")}
                        already = names & set(rec)
                        if already:
                            pending.append({"names": already, "ts": ts, "rerecorded": set(),
                                            "resumed": bool(already & resumed_since), "f": f})
    for p in done + pending:
        k = ("after a resume" if p["resumed"] else "same context", "re-recorded" if p["rerecorded"] else "not re-recorded")
        c[k] += 1
        if p["resumed"] and len(ex) < 6:
            ex.append((p["f"][:45], p["ts"][:19], sorted(p["names"])[0][-30:], bool(p["rerecorded"])))
for k, v in sorted(c.items()):
    print(v, k)
print(ex)
