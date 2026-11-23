"""Plan 254: the pyright rival, driving its language server over stdio. Standard library only.

Revised after the early critic (X10, X21): a frozen pyrightconfig.json gives pyright the import roots the
tests add at run time; workspace/configuration requests get one {} per item; URIs are decoded properly;
each file is opened once; a timeout is recorded, never fatal.

    python -I lsp_254.py <tree> <file> <name>      prints the places that reference <name> defined in <file>
    python -I lsp_254.py --check <tree>             the self-check (a test must reference package_create)
"""
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path

CONFIG = {"extraPaths": ["plugins/tamheed/server", "plugins/tamheed/db", "docs/guide", "tests"],
          "exclude": ["plans", "generated-samples", "evals/sample-results", "**/node_modules", "**/__pycache__"]}


def to_relative(uri: str, root: Path) -> str | None:
    """A file URI as a path relative to root, or None when it lies outside. Pyright on Windows sends
    'file:///c%3A/...' (lower-case drive, escaped colon); the comparison is case-insensitive there."""
    path = urllib.parse.unquote(urllib.parse.urlparse(uri).path)
    if re.match(r"^/[A-Za-z]:", path):
        path = path[1:]
    try:
        rel = os.path.relpath(os.path.normcase(os.path.abspath(path)), os.path.normcase(str(root)))
    except ValueError:  # another drive
        return None
    return None if rel.startswith("..") or os.path.isabs(rel) else rel.replace(os.sep, "/")


class Pyright:
    def __init__(self, root: Path):
        self.root = root.resolve()
        (self.root / "pyrightconfig.json").write_text(json.dumps(CONFIG), encoding="utf-8")
        exe = shutil.which("pyright-langserver.cmd") or shutil.which("pyright-langserver")
        self.p = subprocess.Popen([exe, "--stdio"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, cwd=str(self.root))
        self.n, self.replies, self.lock, self.opened, self.timeouts = 0, {}, threading.Lock(), set(), 0
        threading.Thread(target=self._read, daemon=True).start()
        uri = self.root.as_uri()
        self.call("initialize", {"processId": None, "rootUri": uri, "workspaceFolders": [{"uri": uri, "name": "w"}],
                                 "capabilities": {"workspace": {"configuration": True},
                                                  "textDocument": {"references": {}}}}, timeout=180)
        self.notify("initialized", {})

    def _read(self) -> None:
        f = self.p.stdout
        while True:
            head = b""
            while not head.endswith(b"\r\n\r\n"):
                ch = f.read(1)
                if not ch:
                    return
                head += ch
            size = int(re.search(rb"Content-Length: (\d+)", head)[1])
            msg = json.loads(f.read(size))
            if "id" in msg and "method" not in msg:
                with self.lock:
                    self.replies[msg["id"]] = msg
            elif "id" in msg:
                result = [{} for _ in msg.get("params", {}).get("items", [])] if msg["method"] == "workspace/configuration" else None
                self._send({"jsonrpc": "2.0", "id": msg["id"], "result": result})

    def _send(self, obj: dict) -> None:
        body = json.dumps(obj).encode("utf-8")
        self.p.stdin.write(b"Content-Length: %d\r\n\r\n" % len(body) + body)
        self.p.stdin.flush()

    def notify(self, method: str, params: dict) -> None:
        self._send({"jsonrpc": "2.0", "method": method, "params": params})

    def call(self, method: str, params: dict, timeout: float = 180):
        self.n += 1
        i = self.n
        self._send({"jsonrpc": "2.0", "id": i, "method": method, "params": params})
        end = time.time() + timeout
        while time.time() < end:
            with self.lock:
                if i in self.replies:
                    return self.replies.pop(i).get("result")
            time.sleep(0.02)
        raise TimeoutError(method)

    def warm(self, probe_file: str = "plugins/tamheed/server/tamheed_server.py", probe: str = "package_create",
             limit: float = 180) -> int:
        """Wait until pyright has indexed the workspace: right after start-up it answers from the open file
        only (1 reference where 71 exist, measured). Polls a probe until two answers 3 s apart are equal."""
        if not (self.root / probe_file).exists():
            time.sleep(30)
            return -1
        last, end = -1, time.time() + limit
        while time.time() < end:
            n = len(self.references(probe_file, probe) or [])
            if n == last and n > 1:
                return n
            last = n
            time.sleep(3)
        return last

    def references(self, rel: str, name: str) -> list | None:
        """(path, line) of every reference to the single definition of `name` in `rel`. None on a timeout."""
        path = self.root / rel
        text = path.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^[ \t]*(?:async\s+)?(?:def|class)\s+(" + re.escape(name) + r")\b|^(" + re.escape(name)
                      + r")\s*(?::[^=\n]*)?=", text, re.M)
        if not m:
            return []
        start = m.start(1) if m.group(1) else m.start(2)
        line = text.count("\n", 0, start)
        col = start - (text.rfind("\n", 0, start) + 1)
        uri = path.as_uri()
        if uri not in self.opened:
            self.notify("textDocument/didOpen", {"textDocument": {"uri": uri, "languageId": "python", "version": 1, "text": text}})
            self.opened.add(uri)
        try:
            res = self.call("textDocument/references", {"textDocument": {"uri": uri},
                                                        "position": {"line": line, "character": col},
                                                        "context": {"includeDeclaration": False}}) or []
        except TimeoutError:
            self.timeouts += 1
            return None
        out = []
        for r in res:
            rel = to_relative(r["uri"], self.root)
            if rel is not None:
                out.append((rel, r["range"]["start"]["line"] + 1))
        return out

    def close(self) -> None:
        try:
            self.call("shutdown", {}, timeout=10)
            self.notify("exit", {})
        except Exception:
            pass
        self.p.kill()


if __name__ == "__main__":
    if sys.argv[1] == "--check":
        r0 = Path(sys.argv[2]).resolve()
        drive, rest = str(r0)[0].lower(), str(r0)[2:].replace("\\", "/")
        assert to_relative(f"file:///{drive}%3A{rest}/a/b.py", r0) == "a/b.py", "lower-case escaped drive URI"
        assert to_relative("file:///Z%3A/elsewhere/x.py", r0) is None, "outside the tree"
        s = Pyright(Path(sys.argv[2]))
        t0 = time.time()
        print("warm-up probe answer:", s.warm(), "references after", round(time.time() - t0, 1), "s")
        refs = s.references("plugins/tamheed/server/tamheed_server.py", "package_create") or []
        s.close()
        files = sorted({p for p, _ in refs})
        print(len(refs), "references in", len(files), "files:", files[:8])
        assert any(p.startswith("tests/") for p in files), "pyright sees no test reference to package_create"
        print("lsp_254 self-check passed")
    else:
        t0 = time.time()
        s = Pyright(Path(sys.argv[1]))
        refs = s.references(sys.argv[2], sys.argv[3]) or []
        print(len(refs), "references in", round(time.time() - t0, 1), "s")
        for r in sorted(set(refs))[:15]:
            print(" ", r)
        s.close()
