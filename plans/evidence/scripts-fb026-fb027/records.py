"""M71 (plans 165-169): the timeline of one session transcript - each time the client RECORDED
the entity_query tool's description (`deferred_tools_record`), each SessionStart hook batch,
each compaction boundary, and each server_info reading. Ids, times and OLD/NEW only; no text.

Run:  PYTHONIOENCODING=utf-8 python records.py <transcript.jsonl> [...]
OLD = the 5.6.1 one-liner; NEW = the 5.7.0 registered text.
HORIZON: the harness sweeps old transcripts; a later run reads a different set.
"""
import json, sys, glob, collections
sys.stdout.reconfigure(encoding="utf-8")
OLD = "Query one entity family with targeted columns"
def scan(f, verbose):
    ev = []
    for i, l in enumerate(open(f, encoding="utf-8", errors="replace")):
        if not l.strip():
            continue
        try:
            o = json.loads(l)
        except Exception:
            continue
        ts = o.get("timestamp", "")
        t = o.get("type")
        if t == "attachment":
            a = o["attachment"]
            k = a.get("type")
            if k == "deferred_tools_record":
                for e in a.get("entries", []):
                    if e.get("name", "").endswith("tamheed__entity_query"):
                        d = e.get("description", "")
                        ev.append((ts, i, "record", "OLD" if d == OLD else ("NEW" if d.startswith(OLD + ". Rows come") else "OTHER:" + d[:40])))
            elif k == "hook_success" and a.get("hookEvent") == "SessionStart":
                ev.append((ts, i, "start", a.get("hookName")))
            elif k == "deferred_tools_delta":
                ev.append((ts, i, "delta", "added=%d readded=%d removed=%d" % (len(a.get("addedNames", [])), len(a.get("readdedNames", [])), len(a.get("removedNames", [])))))
        elif t == "system" and o.get("subtype") in ("compact_boundary", "microcompact_boundary"):
            ev.append((ts, i, "compact", o.get("subtype")))
        elif t == "user" and isinstance(o.get("message", {}).get("content"), list):
            for b in o["message"]["content"]:
                if b.get("type") == "tool_result":
                    s = json.dumps(b.get("content"))
                    if '\\"version\\": \\"' in s and "migrations_head" in s:
                        v = s.split('\\"version\\": \\"')[1].split('\\"')[0]
                        ev.append((ts, i, "server_info", v))
    # collapse
    out = []
    for e in ev:
        key = (e[2], e[3].split(":")[0] if e[2] == "start" else e[3])
        if out and out[-1][0] == key:
            out[-1][2] += 1; out[-1][3] = e[0]
        else:
            out.append([key, e[0], 1, e[0]])
    return out
for f in sys.argv[1:]:
    print("==", f.replace("\\", "/").split("/")[-1][:8])
    for key, first, n, last in scan(f, True):
        print("  ", first[:19], "..", last[11:19], key[0], key[1], "x%d" % n)
