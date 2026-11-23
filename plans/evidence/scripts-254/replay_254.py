"""Plan 254, tests A and B (freeze F3, F4). One Graphify map per parent commit, built from nothing.

    python -I replay_254.py <study> A <'all' | 'sample60' | N (the last N)> [--no-pyright]
    python -I replay_254.py <study> B
    python -I replay_254.py <study> gate          the 20-query gate on the census map (X19)

Every tool's raw hints go through ONE pipeline (X4): path made relative to the tree, posix; place at the
parent; non-kept places dropped; test A drops every place in the seed's own file, test B only place A;
first occurrence kept; cut to 10. Several answers are merged round-robin in seed-name order, the file
form last (X20). Each build gets a fresh tree, home and output folder, deleted afterwards (X18).
Rows: results/testA.jsonl, results/testB.jsonl.
"""
import io
import json
import random
import re
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path, PurePosixPath, PureWindowsPath

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import places_254 as P  # noqa: E402
from lsp_254 import Pyright  # noqa: E402

IGNORE = ("plans/\nindex.html\nCHANGELOG.md\ndocs/guide/figures/\ngenerated-samples/\nevals/sample-results/\n"
          "tests/standup_golden/\npyrightconfig.json\n")
K = 10
GATE_FILES = ["plugins/tamheed/server/tamheed_server.py", "plugins/tamheed/db/store.py", "plugins/tamheed/server/export_html.py",
              "plugins/tamheed/server/standup.py", "plugins/tamheed/server/slate.py", "plugins/tamheed/server/adopt.py",
              "plugins/tamheed/server/resume_hook.py", "plugins/tamheed/server/ste_lint.py", "check.py", "docs/guide/build.py"]
GATE_SYMBOLS = ["_wire_project", "gate_run", "_edge_rule_violations", "package_create", "package_open", "entity_upsert",
                "audit_record", "handoff_emit", "readiness_check", "_scan_markers"]


def run(study: Path, step: str, timeout: int, cmd: list, out: Path, home: Path) -> dict:
    subprocess.run([sys.executable, "-I", str(HERE / "run_254.py"), str(study), step, str(timeout), "--out", str(out),
                    "--home", str(home), "--", *cmd], capture_output=True, text=True, encoding="utf-8")
    rec = json.loads((study / "out" / f"{step}.json").read_text(encoding="utf-8"))
    rec["stdout"] = (study / "out" / f"{step}.stdout.txt").read_text(encoding="utf-8")
    return rec


def rel_path(path: str, tree: Path) -> str:
    """A node's source_file as a tree-relative posix path; absolute, backslashed or drive-cased forms alike."""
    s = str(path).replace("\\", "/")
    t = str(tree.resolve()).replace("\\", "/")
    if s.lower().startswith(t.lower() + "/"):
        return s[len(t) + 1:]
    if PureWindowsPath(str(path)).is_absolute() or PurePosixPath(s).is_absolute():
        return "<outside>" + s
    return s[2:] if s.startswith("./") else s


def build(study: Path, repo: Path, rev: str, tag: str) -> dict:
    work = study / "replay" / tag
    shutil.rmtree(work, ignore_errors=True)
    tree, out, home = work / "tree", work / "out", work / "home"
    tree.mkdir(parents=True)
    blob = subprocess.run([*P.GIT, "-C", str(repo), "archive", rev], capture_output=True, check=True).stdout
    tarfile.open(fileobj=io.BytesIO(blob)).extractall(tree, filter="data")
    (tree / ".graphifyignore").write_text(IGNORE, encoding="utf-8")
    rec = run(study, f"build-{tag}", 900, [str(study / "venv" / "Scripts" / "graphify.exe"), "update", str(tree)], out, home)
    rec.update(tree=tree, out=out, home=home, work=work)
    graph = out / "graph.json"
    rec["map_ok"] = graph.exists() and not (tree / "graphify-out").exists()
    if rec["map_ok"]:
        listed = set(P.git(repo, "ls-tree", "-r", "--name-only", rev).split("\n"))
        nodes = json.loads(graph.read_text(encoding="utf-8")).get("nodes", [])
        files = [n.get("source_file") for n in nodes if n.get("source_file")]
        rel = [rel_path(f, tree) for f in files]
        rec["nodes"] = len(nodes)
        rec["source_files_listed"] = round(sum(1 for r in rel if r in listed) / max(1, len(rel)), 4)
        rec["source_file_sample"] = files[:3]
    return rec


def affected(study: Path, rec: dict, query: str, repo: Path, rev: str, tag: str) -> tuple:
    r = run(study, f"aff-{tag}", 180, [str(study / "venv" / "Scripts" / "graphify.exe"), "affected", query, "--graph",
                                         str(rec["out"] / "graph.json")], rec["out"], rec["home"])
    return parse_affected(r["stdout"], rec["tree"], repo, rev), r["exit"]


def parse_affected(text: str, tree: Path, repo: Path, rev: str) -> list:
    """'- <label> [<relation>] <file>:L<n>' or '- <label> [<relation>] <file>' (a file node: line 1).
    A label may itself hold '[...]', so the LAST bracket group before the location is the relation (v2.2)."""
    hits = []
    for line in text.splitlines():
        m = re.match(r"- .*\[[\w-]+\]\s+([^\[\]]+?)(?::L?(\d+))?\s*$", line)
        if m and m[1] != "-":
            path = rel_path(m[1], tree)
            if not path.startswith("<outside>"):
                hits.append(P.place(str(repo), rev, path, int(m[2] or 1)))
    return hits


def pyright_lists(lsp, seed: str, names: list, repo: Path, rev: str) -> tuple:
    lists, fails = [], 0
    for n in names:
        refs = lsp.references(seed, n)
        if refs is None:
            fails += 1
            lists.append([])
            continue
        count: dict = {}
        first: dict = {}
        for path, line in refs:
            if P.kept(path):
                p = P.place(str(repo), rev, path, line)
                count[p] = count.get(p, 0) + 1
                first.setdefault(p, (path, line))
        lists.append(sorted(count, key=lambda p: (-count[p], first[p][0], first[p][1])))
    return lists, fails


def round_robin(lists: list) -> list:
    out, i = [], 0
    while any(i < len(x) for x in lists):
        for x in lists:
            if i < len(x):
                out.append(x[i])
        i += 1
    return out


def pipeline(raw: list, drop) -> list:
    out = []
    for p in raw:
        if not P.kept(p.split("::", 1)[0]) or drop(p) or p in out:
            continue
        out.append(p)
        if len(out) == K:
            break
    return out


def stratum(seed: str, defined: list) -> str:
    if seed.startswith("tests/") and seed.endswith(".py"):
        return "tests"
    if seed.endswith(".py"):
        return "py-defined" if defined else "py-none"
    return "md" if seed.endswith(".md") else "other"


def score(top: list, truth: set, big_bare: frozenset = frozenset()) -> dict:
    found = sum(1 for t in truth if t in top or (t in big_bare and any(h.split("::", 1)[0] == t for h in top)))
    return {"hints": top, "found": found, "recall": round(found / min(K, len(truth)), 4) if truth else None}


def test_a(study: Path, which: str, use_pyright: bool) -> None:
    repo = study / "hist"
    hist = P.history(repo, "451ff94")
    idx = {c: i for i, (c, _) in enumerate(hist)}
    eligible = [c for c, t in hist if 2 <= len(t) <= 20]
    if which == "sample60":
        chosen = sorted(random.Random(254).sample(eligible, min(60, len(eligible))), key=lambda c: idx[c])
    else:
        chosen = eligible if which == "all" else eligible[-int(which):]
    co = P.CoChange(repo, hist)
    (HERE / "results").mkdir(exist_ok=True)
    sink = (HERE / "results" / "testA.jsonl").open("a", encoding="utf-8")
    for c in chosen:
        i, rev, touched, tag = idx[c], P.sha(str(repo), f"{c}^"), hist[idx[c]][1], c[:8]
        t0 = time.time()
        rec = build(study, repo, rev, tag)
        lsp = Pyright(rec["tree"]) if use_pyright else None
        warm = lsp.warm() if lsp else None
        parent_places = set(P.all_places(str(repo), rev))
        subject = P.git(repo, "show", "-s", "--format=%s", c).strip()
        m = re.search(r"plan (\d+)", subject)
        plan = m[1] if m else c[:10]
        for seed, seed_places in touched.items():
            truth_full = set().union(*(v for k, v in touched.items() if k != seed))
            truth = truth_full & parent_places
            if not truth_full:
                continue
            names = P.seed_names(repo, c, seed, seed_places)
            defined = P.seed_names(repo, c, seed, seed_places, defined_only_at=rev) if seed.endswith(".py") else []

            def drop(p, s=seed):
                return p.split("::", 1)[0] == s
            g_lists, g_exits = [], []
            if rec["map_ok"]:
                for q in [f"{seed}::{n}" for n in defined] + [seed]:
                    hits, ex = affected(study, rec, q, repo, rev, tag)
                    g_lists.append(hits)
                    g_exits.append(ex)
            p_lists, p_fail = pyright_lists(lsp, seed, defined, repo, rev) if lsp else ([], 0)
            tools = {
                "search": P.search(repo, rev, names, drop),
                "search_defined": P.search(repo, rev, defined, drop),
                "pyright": round_robin(p_lists),
                "cochange": co.rank(rev, seed_places, drop),
                "graphify": round_robin(g_lists),
                "random": P.random_places(repo, rev, drop, 254 + i),
                "most_changed": P.most_changed(repo, hist, rev, drop),
            }
            row = {"commit": c[:10], "plan": plan, "seed": seed, "stratum": stratum(seed, defined), "names": names,
                   "defined": defined, "truth": sorted(truth), "truth_full": sorted(truth_full),
                   "build_seconds": rec["seconds"], "map_ok": rec["map_ok"], "graphify_exits": g_exits,
                   "pyright_timeouts": p_fail, "pyright_warm": warm}
            for k, raw in tools.items():
                top = pipeline(raw, drop)
                row[k] = score(top, truth) | {"recall_full": score(top, truth_full)["recall"]}
            sink.write(json.dumps(row) + "\n")
            sink.flush()
        if lsp:
            lsp.close()
        print(tag, "seeds", len(touched), "build", rec["seconds"], "s exit", rec["exit"], "map", rec["map_ok"],
              "nodes", rec.get("nodes"), "listed", rec.get("source_files_listed"), "| total", round(time.time() - t0, 1), "s", flush=True)
        if rec["map_ok"] and rec.get("source_files_listed", 1) < 0.95:
            sys.exit(f"STOP: only {rec['source_files_listed']} of node source files are at the parent ({tag})")
        shutil.rmtree(rec["work"], ignore_errors=True)


def test_b(study: Path) -> None:
    repo = study / "hist"
    hist = P.history(repo, "451ff94")
    co = P.CoChange(repo, hist)
    (HERE / "results").mkdir(exist_ok=True)
    sink = (HERE / "results" / "testB.jsonl").open("w", encoding="utf-8")
    for case in json.loads((HERE / "testB_cases.json").read_text(encoding="utf-8")):
        if case["status"] != "testable":
            continue
        rev = P.sha(str(repo), case["build_at"])
        seed_place, seed = case["seed"], case["seed"].split("::", 1)[0]
        truth = set(case["truth"])
        big_bare = frozenset(t for t in truth if "::" not in t and P.spans(str(repo), rev, t))
        text = P.blob(str(repo), rev, seed)
        names = []
        if "::" in seed_place:  # X23: the name of place A plus names defined inside A, nothing from the fix
            span = next(((s, e) for s, e, n in P.spans(str(repo), rev, seed) if f"{seed}::{n}" == seed_place), None)
            names.append(seed_place.split("::", 1)[1].split(".")[-1])
            if span:
                inner = "\n".join(text.split("\n")[span[0] - 1: span[1]])
                names += re.findall(r"^\s*(?:async\s+)?def\s+(\w+)", inner, re.M)
        defined = [n for n in dict.fromkeys(names) if P.defined_once(text, n)]
        tag = "B" + case["fix"]
        rec = build(study, repo, rev, tag)
        lsp = Pyright(rec["tree"])
        lsp.warm()

        def drop(p, a=seed_place):
            return p == a
        g_lists = ([affected(study, rec, q, repo, rev, tag)[0] for q in [f"{seed}::{n}" for n in defined] + [seed]]
                   if rec["map_ok"] else [])
        tools = {"search": P.search(repo, rev, defined, drop), "pyright": round_robin(pyright_lists(lsp, seed, defined, repo, rev)[0]),
                 "cochange": co.rank(rev, {seed_place}, drop), "graphify": round_robin(g_lists),
                 "random": P.random_places(repo, rev, drop, 254), "most_changed": P.most_changed(repo, hist, rev, drop)}
        row = {"fix": case["fix"], "seed": seed_place, "names": defined, "truth": sorted(truth), "map_ok": rec["map_ok"]}
        for k, raw in tools.items():
            row[k] = score(pipeline(raw, drop), truth, big_bare)
        sink.write(json.dumps(row) + "\n")
        lsp.close()
        shutil.rmtree(rec["work"], ignore_errors=True)
        print("fix", case["fix"], {k: row[k]["found"] for k in tools}, "of", len(truth), flush=True)


def gate(study: Path) -> None:
    repo = study / "hist"
    rev = P.sha(str(repo), "451ff94")
    rec = build(study, repo, rev, "gate")
    print({k: rec.get(k) for k in ("seconds", "exit", "map_ok", "nodes", "source_files_listed", "source_file_sample")})
    queries = [f"plugins/tamheed/server/tamheed_server.py::{s}" for s in GATE_SYMBOLS] + GATE_FILES
    ok = 0
    for q in queries:
        hits, ex = affected(study, rec, q, repo, rev, "gate")
        ok += ex == 0
        print(f"  exit {ex} hints {len(hits):3d}  {q}")
    print(f"GATE: {ok} of {len(queries)} exit 0 (needs 18)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    st = Path(sys.argv[1]).resolve()
    mode = sys.argv[2]
    if mode == "A":
        test_a(st, sys.argv[3], "--no-pyright" not in sys.argv)
    elif mode == "B":
        test_b(st)
    else:
        gate(st)
