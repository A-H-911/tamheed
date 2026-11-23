"""Plan 254: the frozen analysis of test A (freeze F3). Reads results/testA.jsonl, writes results/testA.summary.json.

    python -I analyze_254.py

Per seed: recall = true hints / min(10, |truth|) (primary truth: places that exist at the parent). Per
commit: the mean over its seeds. Statistic: the mean over commits. 2,000 bootstrap draws of CLUSTERS
(the plan number, else the commit) with random.Random(254), the same draws for every tool; percentiles
2.5 and 97.5. Verdict: Graphify minus each of the 3 rivals and 2 floors must have an interval above 0.
"""
import collections
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = ["graphify", "search", "search_defined", "pyright", "cochange", "random", "most_changed"]
OTHERS = ["search", "pyright", "cochange", "random", "most_changed"]
GATE = ("docs/guide/content.py", "README.md", "plugins/tamheed/README.md", "plugins/tamheed/server/README.md",
        ".claude-plugin/marketplace.json", "plugins/tamheed/.claude-plugin/plugin.json")


def recall(row: dict, tool: str, truth_key: str = "truth", drop_gate: bool = False):
    truth = set(row[truth_key])
    hints = row[tool]["hints"]
    if drop_gate:
        truth = {t for t in truth if t.split("::", 1)[0] not in GATE}
        hints = [h for h in hints if h.split("::", 1)[0] not in GATE]
    if not truth:
        return None
    return sum(1 for t in truth if t in hints) / min(10, len(truth))


def per_commit(rows: list, tool: str, **kw) -> dict:
    by = collections.defaultdict(list)
    for r in rows:
        v = recall(r, tool, **kw)
        if v is not None:
            by[r["commit"]].append(v)
    return {c: sum(v) / len(v) for c, v in by.items() if v}


def analyse(rows: list, label: str, **kw) -> dict:
    tables = {t: per_commit(rows, t, **kw) for t in TOOLS}
    commits = sorted(set.intersection(*(set(v) for v in tables.values()))) if tables else []
    if not commits:
        return {"label": label, "commits": 0}
    cluster = {r["commit"]: r["plan"] for r in rows}
    groups = collections.defaultdict(list)
    for c in commits:
        groups[cluster[c]].append(c)
    keys = sorted(groups)
    mean = {t: sum(tables[t][c] for c in commits) / len(commits) for t in TOOLS}
    rng = random.Random(254)
    diffs = {o: [] for o in OTHERS}
    boot = {t: [] for t in TOOLS}
    for _ in range(2000):
        draw = [c for k in (rng.choice(keys) for _ in keys) for c in groups[k]]
        m = {t: sum(tables[t][c] for c in draw) / len(draw) for t in TOOLS}
        for t in TOOLS:
            boot[t].append(m[t])
        for o in OTHERS:
            diffs[o].append(m["graphify"] - m[o])

    def ci(xs):
        xs = sorted(xs)
        return [round(xs[int(0.025 * len(xs))], 4), round(xs[int(0.975 * len(xs)) - 1], 4)]
    out = {"label": label, "commits": len(commits), "clusters": len(keys),
           "seeds": sum(1 for r in rows if r["commit"] in set(commits)),
           "mean_recall": {t: round(mean[t], 4) for t in TOOLS}, "ci": {t: ci(boot[t]) for t in TOOLS},
           "graphify_minus": {o: {"diff": round(mean["graphify"] - mean[o], 4), "ci": ci(diffs[o])} for o in OTHERS}}
    above = [o for o in OTHERS if out["graphify_minus"][o]["ci"][0] > 0]
    point = [o for o in OTHERS if out["graphify_minus"][o]["diff"] > 0]
    out["verdict"] = ("clear win" if len(above) == len(OTHERS) else
                      "not shown" if len(point) == len(OTHERS) else
                      "no: below " + ", ".join(o for o in OTHERS if o not in point))
    return out


def main() -> None:
    rows = [json.loads(x) for x in (HERE / "results" / "testA.jsonl").read_text(encoding="utf-8").splitlines() if x]
    res = {"primary": analyse(rows, "primary")}
    for s in sorted({r["stratum"] for r in rows}):
        res[f"stratum {s}"] = analyse([r for r in rows if r["stratum"] == s], f"stratum {s}")
    for lo, hi in ((1, 3), (4, 10), (11, 10 ** 6)):
        res[f"truth {lo}-{hi}"] = analyse([r for r in rows if lo <= len(r["truth"]) <= hi], f"truth size {lo}-{hi}")
    size = collections.Counter(r["commit"] for r in rows)
    files = {r["commit"]: len({r["seed"]} | {t.split("::", 1)[0] for t in r["truth_full"]}) for r in rows}
    res["S1 commits with 2-4 files"] = analyse([r for r in rows if files[r["commit"]] <= 4], "S1")
    res["S2 without gate-enforced files"] = analyse(rows, "S2", drop_gate=True)
    res["full truth"] = analyse(rows, "full truth", truth_key="truth_full")
    res["health"] = {"rows": len(rows), "commits": len(size), "map_ok": sum(r["map_ok"] for r in rows),
                     "graphify_exits": dict(collections.Counter(str(e) for r in rows for e in r["graphify_exits"])),
                     "pyright_timeouts": sum(r["pyright_timeouts"] for r in rows),
                     "empty_hints": {t: sum(1 for r in rows if not r[t]["hints"]) for t in TOOLS}}
    (HERE / "results" / "testA.summary.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    p = res["primary"]
    print(json.dumps({k: p.get(k) for k in ("commits", "clusters", "seeds", "mean_recall", "graphify_minus", "verdict")}, indent=1))
    for k, v in res.items():
        if k not in ("primary", "health") and v.get("commits"):
            print(f"{k:34s} n={v['commits']:3d}  graphify {v['mean_recall']['graphify']:.3f}  search {v['mean_recall']['search']:.3f}"
                  f"  pyright {v['mean_recall']['pyright']:.3f}  cochange {v['mean_recall']['cochange']:.3f}"
                  f"  most_changed {v['mean_recall']['most_changed']:.3f}  random {v['mean_recall']['random']:.3f}  -> {v['verdict']}")
    print("health", res["health"])


if __name__ == "__main__":
    main()
