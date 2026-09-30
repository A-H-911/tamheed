"""M71 (plans 165-169): over every transcript under a projects root, when is a loaded tool's
definition recorded AGAIN - after a compaction, or with none between? Counts only.

Run:  PYTHONIOENCODING=utf-8 python records_census.py <projects root>
      <projects root>  the folder that holds one folder of session transcripts per project
HORIZON: the harness sweeps old transcripts; the script prints the window it read.
"""
import json, sys, glob, collections, os, os
sys.stdout.reconfigure(encoding="utf-8")
root = sys.argv[1]
files = glob.glob(os.path.join(root, "*", "*.jsonl"))
sessions = 0; with_rec = 0
rerec_after_compact = 0; rerec_no_compact = 0; rerec_after_clear = 0
changed_text = collections.Counter()
resume_then_use_no_rerec = 0
examples = []
oldest = "9"; newest = ""
for f in files:
    last = {}           # tool -> (desc, epoch) where epoch counts compactions/clears
    epoch = 0; resumes = 0; seen_rec = False
    try:
        fh = open(f, encoding="utf-8", errors="replace")
    except Exception:
        continue
    sessions += 1
    for l in fh:
        if '"deferred_tools_record"' not in l and "compact_boundary" not in l and "SessionStart:" not in l:
            continue
        try:
            o = json.loads(l)
        except Exception:
            continue
        ts = o.get("timestamp", "")
        if ts:
            oldest = min(oldest, ts); newest = max(newest, ts)
        if o.get("type") == "system" and o.get("subtype") == "compact_boundary":
            epoch += 1; continue
        if o.get("type") != "attachment":
            continue
        a = o["attachment"]
        if a.get("type") == "hook_success" and a.get("hookEvent") == "SessionStart":
            if a.get("hookName") in ("SessionStart:clear", "SessionStart:compact"):
                pass
            continue
        if a.get("type") != "deferred_tools_record":
            continue
        seen_rec = True
        for e in a.get("entries", []):
            n = e.get("name"); d = e.get("description", "")
            if n in last:
                pd, pe = last[n]
                if pe == epoch:
                    rerec_no_compact += 1
                    if len(examples) < 6: examples.append((f[:60], n, ts))
                else:
                    rerec_after_compact += 1
                if pd != d:
                    changed_text[(n.split("__")[-1], "same-epoch" if pe == epoch else "after-compaction")] += 1
            last[n] = (d, epoch)
    if seen_rec: with_rec += 1
print("transcripts", sessions, "with a record", with_rec, "window", oldest[:19], newest[:19])
print("a tool recorded again after a compaction:", rerec_after_compact)
print("a tool recorded again with NO compaction between:", rerec_no_compact, examples)
print("recorded text changed:", dict(changed_text))
