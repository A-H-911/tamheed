"""Plan 254: a static scan of the package for anything that runs, sends, deletes or writes.

    python -I scan_254.py <study folder>

Reads source as text only. Import aliases are resolved (`import subprocess as _sp`), so `_sp.run`
counts as `subprocess.run`. It cannot see calls made through getattr or native code.
"""
import ast
import collections
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
src = Path(sys.argv[1]).resolve() / "src" / "graphify"
MODULES = {"process": ("subprocess", "pty", "os.system", "os.popen", "os.startfile", "os.execv", "os.execvp", "os.spawnv",
                       "multiprocessing", "concurrent.futures.ProcessPoolExecutor"),
           "network": ("socket", "urllib.request", "http.client", "http.server", "requests", "httpx", "aiohttp", "webbrowser",
                       "smtplib", "ftplib", "yt_dlp", "uvicorn", "starlette", "openai", "anthropic", "boto3", "neo4j", "falkordb", "psycopg"),
           "dynamic": ("eval", "exec", "compile", "__import__", "importlib.import_module", "pickle", "marshal", "ctypes", "runpy"),
           "delete": ("shutil.rmtree", "os.remove", "os.unlink", "os.rmdir")}
METHODS = {"delete": ("unlink", "rmdir", "rmtree"), "write": ("write_text", "write_bytes", "mkdir", "copy2", "copytree", "copyfile"),
           "move": ("rename",)}


def dotted(node):
    if isinstance(node, ast.Attribute):
        base = dotted(node.value)
        return f"{base}.{node.attr}" if base else f"?.{node.attr}"
    return node.id if isinstance(node, ast.Name) else ""


rows = []
for path in sorted(src.rglob("*.py")):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    rel = path.relative_to(src).as_posix()
    alias: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                alias[a.asname or a.name.split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            for a in node.names:
                alias[a.asname or a.name] = f"{node.module}.{a.name}"
    owner = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.walk(node):
                owner[id(child)] = node.name
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        raw = dotted(node.func)
        if not raw:
            continue
        head, _, rest = raw.partition(".")
        name = alias.get(head, head) + ("." + rest if rest else "")
        tail = name.split(".")[-1]
        kind = None
        for k, keys in MODULES.items():
            if any(name == m or name.startswith(m + ".") for m in keys):
                kind = k
                break
        if kind is None and (name == "open" or tail == "open" and name not in ("webbrowser.open",)):
            mode = [a.value for a in node.args[:2] if isinstance(a, ast.Constant) and isinstance(a.value, str) and 0 < len(a.value) <= 3 and set(a.value) <= set("rwabxt+")]
            mode += [kw.value.value for kw in node.keywords if kw.arg == "mode" and isinstance(kw.value, ast.Constant)]
            if mode and set(mode[0]) & set("wax+"):
                kind, name = "write", f"open({mode[0]})"
        if kind is None:
            for k, keys in METHODS.items():
                if tail in keys:
                    kind = k
                    break
        if kind is None and name in ("os.replace", "os.rename", "shutil.move"):
            kind = "move"
        if kind:
            rows.append((kind, rel, node.lineno, owner.get(id(node), ""), name))
with (HERE / "scan.csv").open("w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["kind", "file", "line", "function", "call"])
    w.writerows(rows)
print("files", len(list(src.rglob("*.py"))), dict(collections.Counter(r[0] for r in rows)))
for kind in ("process", "network", "dynamic"):
    print("==", kind)
    for r in rows:
        if r[0] == kind:
            print(f"  {r[1]}:{r[2]} {r[3]}() -> {r[4]}")
