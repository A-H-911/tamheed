"""Plan 254, step 5.1: the ledger, the reading bundles and the parse of the machine-written dumps.

    python -I setup_254.py <study folder> <repo of tamheed>

Reads <study>/src (the clone at 3671f31). Writes <study>/bundles/<reader>/<nnn>.txt and, beside this
script, ledger.csv (every path -> content -> reader -> bundles) and dumps.json. Nothing from the clone
is imported or run.
"""
import collections
import csv
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAX_TOKENS = 19000      # the Read tool refuses over 25,000 tokens; the estimate below is rough
MAX_LINES = 1900
WRAP = 1800
IMAGES = {"png", "jpg", "jpeg", "gif", "ico", "webp", "pdf"}
SAFETY = {
    "S1": ["install.py", "hooks.py", "security.py", "paths.py", "querylog.py", "rcfile.py", "manifest.py",
           "__main__.py", "__init__.py", "manifest_ingest.py", "ids.py", "prs.py", "global_graph.py",
           "reflect.py", "benchmark.py", "cargo_introspect.py"],
    "S2": ["cli.py", "llm.py", "semantic_cleanup.py", "file_slice.py", "transcribe.py"],
    "S3": ["detect.py", "cache.py", "watch.py", "serve.py", "ingest.py",
           "google_workspace.py", "mcp_ingest.py", "pg_introspect.py", "scip_ingest.py"],
}
CORE_EXTRACTORS = {"engine", "resolution", "models", "base", "__init__", "sql", "markdown", "json_config",
                   "yaml_config", "bash", "powershell", "MIGRATION"}
OTHER_LANG = ("pascal", "dfm", "ruby", "swift", "kotlin", "csharp", "cpp_", "go_dispatch")
KEY_DOCS = {"README.md", "ARCHITECTURE.md", "BENCHMARKS.md", "AGENTS.md", "GEMINI.md",
            "docs/how-it-works.md", "docs/node-summaries-rfc.md"}


def tokens(text: str) -> int:
    ascii_n = sum(1 for c in text if ord(c) < 128)
    return int(ascii_n / 2.4 + (len(text) - ascii_n) / 0.9) + text.count("\n") * 3


def lane(path: str) -> str:
    ext, stem, name = path.rsplit(".", 1)[-1].lower(), path.rsplit("/", 1)[-1].rsplit(".", 1)[0], path.rsplit("/", 1)[-1]
    if ext in IMAGES:
        return "image"
    if path in ("uv.lock", "worked/rsl-siege-manager/graph.html", "worked/rsl-siege-manager/manifest.json") \
            or path.endswith("/graph.json"):
        return "dump"
    if path.startswith("graphify/") and path.count("/") == 1:
        for reader, names in SAFETY.items():
            if name in names:
                return reader
    if path.startswith(("graphify/pi/", "graphify/always_on/")) or path in ("SECURITY.md", "pyproject.toml"):
        return "S1"
    if path.startswith("graphify/extractors/"):
        return "D" if stem in CORE_EXTRACTORS else "B"
    if path.startswith("graphify/"):
        return "B" if path.endswith(".py") and any(x in stem for x in OTHER_LANG) else "D"
    if path.startswith("tools/") or path in KEY_DOCS:
        return "D"
    if path.startswith("tests/") or path == "CHANGELOG.md":
        return "B"
    return "L"


def main(study: Path) -> None:
    src = study / "src"
    by_sha: dict[str, list[tuple[str, int]]] = collections.defaultdict(list)
    for line in subprocess.run(["git", "-C", str(src), "ls-tree", "-r", "-l", "HEAD"], capture_output=True,
                               text=True, encoding="utf-8", check=True).stdout.splitlines():
        meta, path = line.split("\t", 1)
        _, _, sha, size = meta.split()
        by_sha[sha].append((path, int(size)))
    # the copy that is read: never the skillgen 'expected' twin when another path has the same bytes
    rep = {sha: sorted(v, key=lambda t: (t[0].startswith("tools/skillgen/expected"), t[0]))[0] for sha, v in by_sha.items()}
    lanes: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    for sha, (path, _) in rep.items():
        lanes[lane(path)].append((path, sha))
    bundles: dict[str, list[tuple[str, int]]] = collections.defaultdict(list)   # lane -> [(text, tokens)]
    where: dict[str, list[str]] = collections.defaultdict(list)                  # sha -> bundle labels

    def flush(key: str, parts: list[str], shas: list[str]) -> None:
        if parts:
            text = "".join(parts)
            label = f"{key}:{len(bundles[key]) + 1:03d}"
            bundles[key].append((text, tokens(text)))
            for s in dict.fromkeys(shas):
                where[s].append(label)

    for key in sorted(lanes):
        if key in ("image", "dump"):
            continue
        parts, shas, used, lines_used = [], [], 0, 0
        for path, sha in sorted(lanes[key]):
            text = (src / path).read_bytes().decode("utf-8", "replace").replace("\r\n", "\n").replace("\r", "\n")
            rows = []
            for ln in text.split("\n"):
                while len(ln) > WRAP:
                    rows.append(ln[:WRAP] + " ↵")
                    ln = ln[WRAP:]
                rows.append(ln)
            i = 0
            while i < len(rows) or i == 0:
                head = f"##### FILE {path} | sha {sha[:12]} | from row {i + 1} of {len(rows)} #####\n"
                room_t, room_l = MAX_TOKENS - used - 60, MAX_LINES - lines_used - 2
                if (room_t < 1500 or room_l < 40) and parts:
                    flush(key, parts, shas)
                    parts, shas, used, lines_used = [], [], 0, 0
                    continue
                take, t = 0, 0
                while i + take < len(rows) and take < room_l:
                    cost = tokens(rows[i + take] + "\n")
                    if t + cost > room_t and take:
                        break
                    t += cost
                    take += 1
                parts.append(head + "\n".join(rows[i:i + take]) + "\n")
                shas.append(sha)
                used += t + 60
                lines_used += take + 1
                i += take
                if i >= len(rows):
                    break
        flush(key, parts, shas)

    # split the lanes into readers, keeping bundle order
    plan = {"S1": ["S1"], "S2": ["S2"], "S3": ["S3"], "D": [f"D{n}" for n in range(4, 9)],
            "B": [f"B{n:02d}" for n in range(1, 13)], "L": ["L1", "L2", "L3"]}
    label_to_reader: dict[str, tuple[str, int]] = {}
    summary = []
    for key, readers in plan.items():
        items = bundles.get(key, [])
        total = sum(t for _, t in items)
        acc, r, seq = 0, 0, 0
        for n, (text, t) in enumerate(items, 1):
            if r < len(readers) - 1 and acc + t / 2 > total * (r + 1) / len(readers):
                r, seq = r + 1, 0
            seq += 1
            acc += t
            out = study / "bundles" / readers[r]
            out.mkdir(parents=True, exist_ok=True)
            (out / f"{seq:03d}.txt").write_text(text, encoding="utf-8", newline="\n")
            label_to_reader[f"{key}:{n:03d}"] = (readers[r], seq)
        for reader in readers:
            sel = [items[int(k.split(":")[1]) - 1] for k, v in label_to_reader.items() if v[0] == reader]
            summary.append((reader, len(sel), sum(t for _, t in sel), sum(len(x) for x, _ in sel)))

    with (HERE / "ledger.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["path", "sha", "bytes", "read_as", "lane", "reader", "bundles"])
        for sha, paths in sorted(by_sha.items(), key=lambda kv: kv[1][0][0]):
            read_as = rep[sha][0]
            key = lane(read_as)
            labels = where.get(sha, [])
            readers = sorted({label_to_reader[x][0] for x in labels})
            refs = " ".join(f"{label_to_reader[x][0]}/{label_to_reader[x][1]:03d}" for x in labels)
            for path, size in paths:
                w.writerow([path, sha, size, "" if path == read_as else read_as, key,
                            "L4" if key == "image" else "script" if key == "dump" else " ".join(readers), refs])

    print("paths", sum(len(v) for v in by_sha.values()), "contents", len(by_sha),
          "lanes", {k: len(v) for k, v in lanes.items()})
    for row in summary:
        print("%-4s bundles %3d  est tokens %7d  chars %8d" % row)
    dumps(src, [p for p, _ in lanes["dump"]])


def dumps(src: Path, paths: list[str]) -> None:
    """Every byte of the machine-written files goes through a parser; the result is their structure."""
    report = {}
    for path in sorted(paths):
        raw = (src / path).read_bytes()
        info: dict = {"bytes": len(raw)}
        if path == "uv.lock":
            lock = tomllib.loads(raw.decode("utf-8"))
            pk = lock["package"]
            info.update(packages=len(pk), sources=dict(collections.Counter(next(iter(p.get("source", {"?": 0}))) for p in pk)),
                        registries=sorted({p["source"]["registry"] for p in pk if "registry" in p.get("source", {})}),
                        without_hash=[p["name"] for p in pk if "registry" in p.get("source", {})
                                      and not all("hash" in w for w in p.get("wheels", []) + ([p["sdist"]] if "sdist" in p else []))][:10],
                        sdist_only=[p["name"] for p in pk if "registry" in p.get("source", {}) and not p.get("wheels")][:20])
        elif path.endswith(".json"):
            d = json.loads(raw.decode("utf-8"))
            info["top"] = {k: (len(v) if hasattr(v, "__len__") and not isinstance(v, str) else v) for k, v in list(d.items())[:12]} \
                if isinstance(d, dict) else f"list of {len(d)}"
            if isinstance(d, dict) and "nodes" in d:
                edges = d.get("links") or d.get("edges") or []
                info.update(nodes=len(d["nodes"]), edges=len(edges),
                            node_keys=sorted({k for n in d["nodes"] for k in n}),
                            edge_keys=sorted({k for e in edges for k in e}),
                            relations=dict(collections.Counter(e.get("relation") for e in edges).most_common(12)),
                            confidence=dict(collections.Counter(e.get("confidence") for e in edges)),
                            absolute_paths=sum(1 for n in d["nodes"] if re.match(r"([A-Za-z]:\\|/(home|Users)/)", str(n.get("source_file", "")))))
        else:
            text = raw.decode("utf-8", "replace")
            info.update(external=sorted(set(re.findall(r"(?:src|href)=[\"'](https?://[^\"']+)", text)))[:10],
                        scripts=text.count("<script"), fetch_calls=len(re.findall(r"\bfetch\(|XMLHttpRequest|WebSocket\(", text)))
        report[path] = info
    (HERE / "dumps.json").write_text(json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=1, sort_keys=True)[:3500])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main(Path(sys.argv[1]).resolve())
