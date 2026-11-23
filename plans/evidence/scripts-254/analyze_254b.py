"""Plan 254, POST HOC analyses (written after the results were seen; never verdicts). Answers critic Y2-Y4,
Y9-Y12, Y15. Reads results/testA.jsonl and results/ab/*.jsonl, writes results/posthoc.json.

    python -I analyze_254b.py

1. Test A: Graphify minus search_defined, and each stratum's paired intervals (same draws as analyze_254).
2. Test A at file level (a hint counts if its file holds a true place), and false hints per true hint.
3. Test A: seed rows where Graphify returned no hint at all.
4. A/B: text read with tool-result lines under graphify-out/ and .claude/skills/graphify/ removed; real Graphify
   calls by command name (not by substring); range overlap tested both ways.
"""
import collections
import json
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = ["graphify", "search", "search_defined", "pyright", "cochange", "random", "most_changed"]


def boot_diff(rows: list, value, a: str, b: str) -> dict:
    per = {t: collections.defaultdict(list) for t in (a, b)}
    for r in rows:
        for t in (a, b):
            v = value(r, t)
            if v is not None:
                per[t][r["commit"]].append(v)
    commits = sorted(set(per[a]) & set(per[b]))
    if not commits:
        return {}
    m = {t: {c: sum(per[t][c]) / len(per[t][c]) for c in commits} for t in (a, b)}
    plan = {r["commit"]: r["plan"] for r in rows}
    groups = collections.defaultdict(list)
    for c in commits:
        groups[plan[c]].append(c)
    keys = sorted(groups)
    rng, diffs = random.Random(254), []
    for _ in range(2000):
        draw = [c for k in (rng.choice(keys) for _ in keys) for c in groups[k]]
        diffs.append(sum(m[a][c] - m[b][c] for c in draw) / len(draw))
    diffs.sort()
    d = sum(m[a][c] - m[b][c] for c in commits) / len(commits)
    return {"commits": len(commits), "diff": round(d, 4), "ci": [round(diffs[50], 4), round(diffs[1949], 4)]}


def place_recall(r: dict, t: str):
    truth = set(r["truth"])
    return sum(1 for x in truth if x in r[t]["hints"]) / min(10, len(truth)) if truth else None


def file_recall(r: dict, t: str):
    truth = {x.split("::", 1)[0] for x in r["truth"]}
    if not truth:
        return None
    files = list(dict.fromkeys(h.split("::", 1)[0] for h in r[t]["hints"]))[:10]
    return sum(1 for x in truth if x in files) / min(10, len(truth))


def main() -> None:
    rows = [json.loads(x) for x in (HERE / "results" / "testA.jsonl").read_text(encoding="utf-8").splitlines() if x]
    out: dict = {"note": "POST HOC: computed after the results were seen; context only, never a verdict."}
    out["graphify_minus_search_defined"] = boot_diff(rows, place_recall, "graphify", "search_defined")
    out["strata"] = {s: {o: boot_diff([r for r in rows if r["stratum"] == s], place_recall, "graphify", o)
                         for o in ("search", "search_defined", "pyright", "cochange", "most_changed", "random")}
                     for s in sorted({r["stratum"] for r in rows})}
    out["file_level_mean"] = {}
    for t in TOOLS:
        per = collections.defaultdict(list)
        for r in rows:
            v = file_recall(r, t)
            if v is not None:
                per[r["commit"]].append(v)
        out["file_level_mean"][t] = round(sum(sum(v) / len(v) for v in per.values()) / len(per), 4)
    out["false_hints_per_true"] = {}
    for t in TOOLS:
        true = sum(1 for r in rows for h in r[t]["hints"] if h in set(r["truth"]))
        false = sum(1 for r in rows for h in r[t]["hints"] if h not in set(r["truth"]))
        out["false_hints_per_true"][t] = round(false / max(1, true), 2)
    out["rows_with_no_hint"] = {t: sum(1 for r in rows if not r[t]["hints"]) for t in TOOLS}
    out["rows"] = len(rows)
    # the A/B recount
    ab = {}
    for f in sorted((HERE / "results" / "ab").glob("*.jsonl")):
        task, arm, n = f.stem.split("-")
        total = cleaned = 0
        calls = 0
        for x in f.read_text(encoding="utf-8").splitlines():
            if not x.startswith("{"):
                continue
            e = json.loads(x)
            msg = e.get("message") if isinstance(e.get("message"), dict) else {}
            for c in msg.get("content") or [] if isinstance(msg.get("content"), list) else []:
                if c.get("type") == "tool_result":
                    body = c.get("content")
                    body = body if isinstance(body, str) else json.dumps(body)
                    total += len(body)
                    keep = [ln for ln in body.split("\n")
                            if not re.search(r"graphify-out[/\\]|\.claude[/\\]+skills[/\\]+graphify", ln)]
                    cleaned += len("\n".join(keep))
                elif c.get("type") == "tool_use" and c.get("name") == "Bash":
                    cmd = c.get("input", {}).get("command", "")
                    calls += bool(re.search(r"(^|[;&|]\s*)graphify(\.exe)?\s+(query|affected|explain|path|section)", cmd))
        ab.setdefault(arm, {"read": 0, "read_without_graphify_files": 0, "graphify_calls": 0})
        ab[arm]["read"] += total
        ab[arm]["read_without_graphify_files"] += cleaned
        ab[arm]["graphify_calls"] += calls
        ab.setdefault("by_task", {}).setdefault(task, {}).setdefault(arm, []).append(total)
    a, b = ab["A"], ab["B"]
    out["ab"] = {"A": a, "B": b,
                 "more_read_B": round(b["read"] / a["read"] - 1, 4),
                 "more_read_B_without_graphify_files": round(b["read_without_graphify_files"] / a["read_without_graphify_files"] - 1, 4),
                 "more_read_B_without_task_M48": round(sum(sum(v["B"]) for k, v in ab["by_task"].items() if k != "M48")
                                                      / sum(sum(v["A"]) for k, v in ab["by_task"].items() if k != "M48") - 1, 4),
                 "ranges_overlap": {k: max(v["B"]) >= min(v["A"]) and max(v["A"]) >= min(v["B"]) for k, v in ab["by_task"].items()}}
    (HERE / "results" / "posthoc.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "strata"}, indent=1))
    for s, d in out["strata"].items():
        print(s, {o: (v.get("diff"), v.get("ci")) for o, v in d.items()})


if __name__ == "__main__":
    main()
