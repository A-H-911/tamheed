"""The pin ledger for a rewrite wave (plans 184-188). Read-only.

Every quoted string of four or more words in the test suites, the eval spec, check.py's lints
and the eval workflow that occurs verbatim in a file the wave rewrites. A pinned phrase is kept
word for word, or the pin is re-aimed in the same commit. The census's recollection is not the
ledger: this output is.

Usage: python plans/evidence/scripts-ste/pins.py <file-or-glob> ... > plans/evidence/scripts-ste/pins-<plan>.md
"""
from __future__ import annotations

import ast
import glob
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MIN_WORDS = 3  # a three-word pin ("stock last changed") slipped past 4 in wave 1


def py_strings(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node.lineno, node.value
        elif isinstance(node, ast.JoinedStr):
            for v in node.values:
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    yield node.lineno, v.value


def json_strings(path: Path):
    def walk(x, line=0):
        if isinstance(x, str):
            yield line, x
        elif isinstance(x, dict):
            for v in x.values():
                yield from walk(v)
        elif isinstance(x, list):
            for v in x:
                yield from walk(v)
    yield from walk(json.loads(path.read_text(encoding="utf-8")))


def yaml_strings(path: Path):
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for m in re.finditer(r"""(["'])(.{12,}?)\1""", line):
            yield i, m.group(2)


def pins() -> list[tuple[str, int, str]]:
    out = []
    for p in sorted((REPO / "tests").glob("*.py")):
        out += [(p.relative_to(REPO).as_posix(), ln, s) for ln, s in py_strings(p)]
    out += [("evals/evals.json", ln, s) for ln, s in json_strings(REPO / "evals" / "evals.json")]
    out += [("check.py", ln, s) for ln, s in py_strings(REPO / "check.py")]
    wf = REPO / ".github" / "workflows" / "eval.yaml"
    if wf.exists():
        out += [(".github/workflows/eval.yaml", ln, s) for ln, s in yaml_strings(wf)]
    return [(f, ln, s.strip()) for f, ln, s in out if len(s.split()) >= MIN_WORDS]


def main(argv: list[str]) -> None:
    targets = []
    for a in argv:
        targets += [Path(p) for p in glob.glob(a, recursive=True)] or [Path(a)]
    texts = {t.as_posix(): t.read_text(encoding="utf-8") for t in targets if t.is_file()}
    ledger = pins()
    print(f"# Pin ledger: {len(ledger)} candidate phrases against {len(texts)} files\n")
    print("| pinned in | line | phrase | occurs in |")
    print("|---|---|---|---|")
    n = 0
    seen = set()
    for src, ln, s in ledger:
        hits = [t for t, body in texts.items() if s in body]
        if hits and (s, tuple(hits)) not in seen:
            seen.add((s, tuple(hits)))
            n += 1
            print(f"| `{src}` | {ln} | `{s[:90].replace('|', chr(92) + '|')}` | {', '.join(f'`{h}`' for h in hits)} |")
    print(f"\n{n} pinned phrases occur in the wave's files.")


if __name__ == "__main__":
    main(sys.argv[1:])
