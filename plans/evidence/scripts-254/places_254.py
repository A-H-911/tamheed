"""Plan 254: 'places' and the cheap rivals for the replay (freeze F2, F3). Standard library only.

A place is a file, or, in a file over 800 lines AT THAT COMMIT, the innermost function, class, multi-line
module-level assignment, key of a module-level dict literal, or Markdown heading around a line.
Revised after the early critic (X5-X8, X11-X13, X15, X22). Self-check: `python -I places_254.py --check <repo>`.
"""
import ast
import builtins
import collections
import functools
import json
import keyword
import os
import random
import re
import sqlite3
import subprocess
import unittest
from pathlib import Path

BIG = 800
SINCE = "2026-07-01"
GATE_ENFORCED = ("docs/guide/content.py", "README.md", "plugins/tamheed/README.md", "plugins/tamheed/server/README.md",
                 ".claude-plugin/marketplace.json", "plugins/tamheed/.claude-plugin/plugin.json")
GIT = ["git", "-c", "core.quotePath=false", "-c", "diff.noprefix=false", "-c", "diff.mnemonicPrefix=false",
       "-c", "core.autocrlf=false"]
DIFF = ["diff", "--no-ext-diff", "--src-prefix=a/", "--dst-prefix=b/", "-U0", "--no-color", "--no-renames"]


def kept(path: str) -> bool:
    """Generated and record files never count as a place (frozen; X14 adds the standup goldens)."""
    return not (path.startswith(("plans/", "docs/guide/figures/", "generated-samples/", "evals/sample-results/",
                                 "tests/standup_golden/"))
                or path in ("CHANGELOG.md", "index.html"))


def git(repo, *args: str) -> str:
    return subprocess.run([*GIT, "-C", str(repo), *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


@functools.lru_cache(maxsize=8192)
def sha(repo: str, rev: str) -> str:
    return git(repo, "rev-parse", rev).strip()


@functools.lru_cache(maxsize=8192)
def blob(repo: str, commit: str, path: str) -> str:
    return git(repo, "show", f"{commit}:{path}")


def _dict_key_spans(target: str, value) -> list:
    out = []
    if isinstance(value, ast.Dict):
        for k, v in zip(value.keys, value.values):
            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                out.append((k.lineno, v.end_lineno or v.lineno, f"{target}[{k.value}]"))
    return out


@functools.lru_cache(maxsize=8192)
def spans(repo: str, commit: str, path: str) -> tuple:
    """(start, end, name) of every sub-place, only for files over BIG lines at this commit."""
    text = blob(repo, commit, path)
    if text.count("\n") <= BIG:
        return ()
    out = []
    if path.endswith(".py"):
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return ()

        def walk(node, prefix):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    name = f"{prefix}{child.name}"
                    out.append((child.lineno, child.end_lineno or child.lineno, name))
                    walk(child, name + ".")
        walk(tree, "")
        for node in tree.body:  # X13: module-level multi-line assignments and their dict keys
            target = None
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                target = node.targets[0].id
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
                target = node.target.id
            if target and (node.end_lineno or node.lineno) > node.lineno:
                out.append((node.lineno, node.end_lineno, target))
                out += _dict_key_spans(target, node.value)
    elif path.endswith(".md"):
        heads = [(i + 1, len(m.group(1)), m.group(2).strip()) for i, line in enumerate(text.split("\n"))
                 if (m := re.match(r"^(#{1,3})\s+(.*)", line))]
        total = text.count("\n") + 1
        for k, (line, level, title) in enumerate(heads):
            end = next((h[0] - 1 for h in heads[k + 1:] if h[1] <= level), total)
            out.append((line, end, title))
    return tuple(sorted(out))


def place(repo: str, commit: str, path: str, line: int) -> str:
    """The innermost span around `line` at `commit`, or the file itself."""
    best = None
    for start, end, name in spans(repo, commit, path):
        if start <= line <= end and (best is None or start > best[0] or (start == best[0] and end <= best[1])):
            best = (start, end, name)
    return f"{path}::{best[2]}" if best else path


def parse_diff(text: str) -> list:
    """(old path, new path, old start, old len, new start, new len) per hunk. A state machine: '---' and
    '+++' are headers only between 'diff --git' and the first '@@' (X7)."""
    hunks, in_header, old, new = [], False, None, None
    for line in text.split("\n"):
        if line.startswith("diff --git "):
            in_header, old, new = True, None, None
        elif in_header and line.startswith("--- "):
            old = line[6:] if line.startswith("--- a/") else None
        elif in_header and line.startswith("+++ "):
            new = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("@@"):
            in_header = False
            m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
            if m:
                hunks.append((old, new, int(m[1]), int(m[2] if m[2] is not None else 1),
                              int(m[3]), int(m[4] if m[4] is not None else 1)))
    return hunks


def changed(repo, commit: str) -> dict:
    """{kept path: set of places} touched by one commit against its first parent. Old-side lines map at the
    parent, new-side lines at the commit; a deleted file keeps its old path (X15)."""
    parent = sha(str(repo), f"{commit}^")
    out: dict = collections.defaultdict(set)
    for old, new, os_, ol, ns, nl in parse_diff(git(repo, *DIFF, parent, commit)):
        if ol and old and kept(old):
            out[old] |= {place(str(repo), parent, old, n) for n in range(os_, os_ + ol)}
        if nl and new and kept(new):
            out[new] |= {place(str(repo), commit, new, n) for n in range(ns, ns + nl)}
        if not ol and not nl and (new or old) and kept(new or old):
            out[new or old].add(new or old)
    return {p: s for p, s in out.items() if s}


def commits(repo, head: str) -> list:
    """Ancestry order, oldest first (X6): every non-merge commit since SINCE up to head."""
    return git(repo, "log", "--reverse", "--topo-order", "--no-merges", f"--since={SINCE}", "--format=%H", head).split()


def history(repo, head: str) -> list:
    return [(c, changed(repo, c)) for c in commits(repo, head)]


@functools.lru_cache(maxsize=1024)
def ancestors(repo: str, rev: str) -> frozenset:
    return frozenset(git(repo, "rev-list", rev).split())


class CoChange:
    """Places that changed together with the seed's places in ANCESTORS of the parent only (X5, X6)."""

    def __init__(self, repo, hist: list):
        self.repo, self.hist = str(repo), hist

    def rank(self, parent: str, seed_places: set, exclude, k: int = 60) -> list:
        anc = ancestors(self.repo, parent)
        score: dict = collections.defaultdict(float)
        for c, touched in self.hist:
            if c not in anc:
                continue
            allp = set().union(*touched.values()) if touched else set()
            if allp & seed_places:
                for p in allp - seed_places:
                    score[p] += 1.0 / max(1, len(allp))
        return [p for p in sorted(score, key=lambda p: (-score[p], p)) if not exclude(p)][:k]


def most_changed(repo, hist: list, parent: str, exclude, k: int = 60) -> list:
    anc = ancestors(str(repo), parent)
    score: collections.Counter = collections.Counter()
    for c, touched in hist:
        if c in anc:
            for ps in touched.values():
                score.update(ps)
    return [p for p, _ in sorted(score.items(), key=lambda kv: (-kv[1], kv[0])) if not exclude(p)][:k]


@functools.lru_cache(maxsize=512)
def all_places(repo: str, commit: str) -> tuple:
    out = []
    for path in git(repo, "ls-tree", "-r", "--name-only", commit).split("\n"):
        if path and kept(path):
            out += [f"{path}::{n}" for _, _, n in spans(repo, commit, path)] + [path]
    return tuple(out)


def random_places(repo, parent: str, exclude, seed: int, k: int = 10) -> list:
    pool = [p for p in all_places(str(repo), parent) if not exclude(p)]
    return random.Random(seed).sample(pool, min(k, len(pool)))


NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]{3,}")
COMMON = (set(dir(builtins)) | set(dir(str)) | set(dir(dict)) | set(dir(list)) | set(dir(set)) | set(dir(Path))
          | set(dir(unittest.TestCase)) | set(dir(sqlite3.Connection)) | set(dir(sqlite3.Cursor)) | set(dir(re))
          | set(dir(re.Match)) | set(dir(re.Pattern)) | set(dir(json)) | set(dir(os.path)) | set(dir(os))
          | set(keyword.kwlist) | {"self", "cls", "subTest", "addCleanup", "setUp", "tearDown"})


def changed_lines(repo, commit: str, path: str) -> tuple:
    parent = sha(str(repo), f"{commit}^")
    old, new = set(), set()
    for _o, _n, os_, ol, ns, nl in parse_diff(git(repo, *DIFF, parent, commit, "--", path)):
        old |= set(range(os_, os_ + ol))
        new |= set(range(ns, ns + nl))
    return old, new


def _py_names(text: str, lines: set) -> list:
    """Names of code on the given lines, from the syntax tree: strings never count (X11 adds AnnAssign)."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    out = []
    for node in ast.walk(tree):
        if getattr(node, "lineno", None) not in lines:
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.append(node.name)
        elif isinstance(node, ast.Call):
            f = node.func
            out.append(f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else "")
        elif isinstance(node, ast.Assign):
            out += [t.id for t in node.targets if isinstance(t, ast.Name) and t.id.isupper()]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id.isupper():
            out.append(node.target.id)
    return [n for n in out if n]


def _stem(token: str) -> str:
    base = token.rsplit("/", 1)[-1]
    if base.rsplit(".", 1)[-1] in ("py", "md", "sql", "js", "json", "css", "mjs"):
        return base.rsplit(".", 1)[0]
    return base.split(".")[-1]


def defined_once(text: str, name: str) -> bool:
    pat = r"^[ \t]*(?:async\s+)?(?:def|class)\s+" + re.escape(name) + r"\b|^" + re.escape(name) + r"\s*(?::[^=\n]*)?="
    return len(re.findall(pat, text, re.M)) == 1


def seed_names(repo, commit: str, path: str, places: set, defined_only_at: str = "") -> list:
    """The frozen seed-to-query rule (X12, X22). Span names first, ordered by how many changed lines fall in
    them; then, for Python, names defined, called or assigned (upper case) on changed lines, from the syntax
    tree; for Markdown, code spans (file names by their stem); for .js/.sql, identifiers on changed lines.
    With defined_only_at, only names defined exactly once in the seed file at that commit are kept, BEFORE the
    cap of 12 (X12, X20)."""
    old, new = changed_lines(repo, commit, path)
    parent = sha(str(repo), f"{commit}^")
    weight: collections.Counter = collections.Counter()
    for n in old:
        weight[place(str(repo), parent, path, n)] += 1
    for n in new:
        weight[place(str(repo), commit, path, n)] += 1
    names = []
    for p in sorted(places, key=lambda p: (-weight[p], p)):
        if "::" in p:
            sub = p.split("::", 1)[1]
            m = re.match(r"([A-Za-z_]\w*)\[(.*)\]$", sub)
            if m:
                names += [m[1]] + ([m[2]] if NAME.fullmatch(m[2]) else [])
            else:
                names.append(sub.split(".")[-1])
    if path.endswith(".py"):
        names += _py_names(blob(str(repo), parent, path), old) + _py_names(blob(str(repo), commit, path), new)
    else:
        diff = git(repo, *DIFF, parent, commit, "--", path)
        for ln in diff.split("\n"):
            if ln[:1] not in "+-" or ln.startswith(("+++ ", "--- ")):
                continue
            if path.endswith(".md"):
                names += [_stem(s) for s in re.findall(r"`([A-Za-z_][\w./-]{3,})(?:\(\))?`", ln)]
            elif path.endswith((".js", ".mjs", ".sql")):
                names += NAME.findall(ln)
    seen, out = set(), []
    text = blob(str(repo), defined_only_at, path) if defined_only_at else ""
    for n in names:
        if not NAME.fullmatch(n) or n in COMMON or n in seen:
            continue
        if defined_only_at and not defined_once(text, n):
            continue
        seen.add(n)
        out.append(n)
    return out[:12]


def search(repo, commit: str, names: list, exclude, k: int = 60) -> list:
    """Plain search: places holding a whole-word match of the seed names, most distinct names first (X8)."""
    if not names:
        return []
    rev = sha(str(repo), commit)
    pattern = "(" + "|".join(re.escape(n) for n in names) + ")"
    out = git(repo, "grep", "-n", "-I", "-E", "-w", pattern, rev, "--")
    score: collections.Counter = collections.Counter()
    hit_names: dict = collections.defaultdict(set)
    for line in out.split("\n"):
        m = re.match(re.escape(rev) + r":([^:]+):(\d+):(.*)", line)
        if not m or not kept(m[1]):
            continue
        p = place(str(repo), rev, m[1], int(m[2]))
        if exclude(p):
            continue
        score[p] += 1
        hit_names[p] |= {n for n in names if re.search(r"(?<![\w])" + re.escape(n) + r"(?![\w])", m[3])}
    return sorted(score, key=lambda p: (-len(hit_names[p]), -score[p], p))[:k]


def self_check(repo: str) -> None:
    hunks = parse_diff("diff --git a/x.sql b/x.sql\n--- a/x.sql\n+++ b/x.sql\n@@ -1,2 +1,2 @@\n--- c\n+++ d\n"
                       "diff --git a/y.md b/y.md\n--- a/y.md\n+++ /dev/null\n@@ -1 +0,0 @@\n-gone\n")
    assert hunks == [("x.sql", "x.sql", 1, 2, 1, 2), ("y.md", None, 1, 1, 0, 0)], hunks
    head = sha(repo, "451ff94")
    assert len(search(repo, head, ["gate_run"], lambda p: False)) > 0, "search finds gate_run"
    sp = {n for _, _, n in spans(repo, head, "plugins/tamheed/server/tamheed_server.py")}
    assert "TOOLS" in sp and "TOOLS[package_open]" in sp and "RELATION_RULES" in sp, "module-level spans"
    assert any(n.startswith("TEXT[") for _, _, n in spans(repo, head, "docs/guide/content.py")), "TEXT keys"
    assert "AA_BB" in _py_names("AA_BB: dict = {}\n", {1}), "AnnAssign"
    assert defined_once("def f_one(x):\n    pass\n", "f_one") and not defined_once("def f_one():\ndef f_one():\n", "f_one")
    assert _stem("tamheed_server.py") == "tamheed_server" and _stem("pkg.mod.func") == "func"
    print("places_254 self-check passed")


if __name__ == "__main__":
    import sys
    if sys.argv[1] == "--check":
        self_check(sys.argv[2])
    else:
        r, c = sys.argv[1], sys.argv[2]
        for p, s in changed(r, c).items():
            print(p, sorted(s)[:6], seed_names(r, c, p, s))
