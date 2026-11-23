"""Plan 254, step 5.3: what the census map of 451ff94 holds, checked against Python's own syntax tree.

    python -I census_254.py <study>        reads <study>/census/{out,tree}; writes results/census.json
"""
import ast
import collections
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
study = Path(sys.argv[1]).resolve()
tree, out = study / "census" / "tree", study / "census" / "out"
g = json.loads((out / "graph.json").read_text(encoding="utf-8"))
nodes, edges = g["nodes"], g.get("links") or g.get("edges") or []
byid = {n["id"]: n for n in nodes}
res: dict = {"bytes": (out / "graph.json").stat().st_size, "nodes": len(nodes), "edges": len(edges),
             "node_types": dict(collections.Counter(n.get("file_type") for n in nodes)),
             "relations": dict(collections.Counter(e.get("relation") for e in edges).most_common()),
             "confidence": dict(collections.Counter(e.get("confidence") for e in edges)),
             "files_with_nodes": len({n.get("source_file") for n in nodes}),
             "md_files_with_nodes": len({n.get("source_file") for n in nodes if str(n.get("source_file", "")).endswith(".md")}),
             "report_bytes": (out / "GRAPH_REPORT.md").stat().st_size, "html_bytes": (out / "graph.html").stat().st_size}

# Python functions and classes, by the syntax tree, against the map's nodes
py = [p for p in tree.rglob("*.py") if "plans" not in p.parts]
defs, calls_ast = set(), collections.Counter()
for p in py:
    rel = p.relative_to(tree).as_posix()
    try:
        t = ast.parse(p.read_text(encoding="utf-8"))
    except SyntaxError:
        continue
    for node in ast.walk(t):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defs.add((rel, node.name, node.lineno))
        elif isinstance(node, ast.Call):
            calls_ast[rel] += 1
node_at = {(n.get("source_file"), str(n.get("source_location", "")).lstrip("L")) for n in nodes}
found = sum(1 for rel, name, line in defs if (rel, str(line)) in node_at)
res["python_defs_by_ast"] = len(defs)
res["python_defs_found_as_nodes"] = found
res["python_defs_share"] = round(found / max(1, len(defs)), 4)
res["call_edges"] = sum(1 for e in edges if e.get("relation") in ("calls", "indirect_call"))
res["calls_by_ast"] = sum(calls_ast.values())

# 100 random call edges: does the target's name appear on the source's line, or in the source's body?
rng = random.Random(254)
call_edges = [e for e in edges if e.get("relation") == "calls"]
sample = rng.sample(call_edges, min(100, len(call_edges)))
ok, why = 0, collections.Counter()
for e in sample:
    src, tgt = byid.get(e.get("source") or e.get("_src")), byid.get(e.get("target") or e.get("_tgt"))
    if not src or not tgt:
        why["endpoint missing"] += 1
        continue
    name = str(tgt.get("label", "")).rstrip("()").split(".")[-1]
    f = tree / str(e.get("source_file") or src.get("source_file"))
    line = int(str(e.get("source_location") or "L0").lstrip("L") or 0)
    text = f.read_text(encoding="utf-8", errors="replace").split("\n") if f.is_file() else []
    if line and 0 < line <= len(text) and name and name in text[line - 1]:
        ok += 1
    else:
        why["name not on the cited line"] += 1
res["call_edge_sample"] = {"checked": len(sample), "name_on_cited_line": ok, "other": dict(why),
                           "by_confidence": dict(collections.Counter(e.get("confidence") for e in sample))}
(HERE / "results").mkdir(exist_ok=True)
(HERE / "results" / "census.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
print(json.dumps(res, indent=1))
