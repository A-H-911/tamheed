"""Plan 179: the vocabulary census. Read-only. Counts, per surface, every inflected use of the
words in the upstream synonym groups and in Tamheed's candidate groups, outside code spans and
fenced code, and reports NAME POSITIONS separately: hits inside code spans, in headings, and in
identifiers the engine owns (tables, columns, tools, relations, readiness rules, stage titles).
A name cannot change in a MINOR, so the interview sees them before it rejects a word.

Usage: python plans/evidence/scripts-ste/vocab_census.py > plans/evidence/scripts-ste/vocab_census.md
"""
from __future__ import annotations

import ast
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "plugins" / "tamheed"
sys.path.insert(0, str(BUNDLE / "server"))

GROUPS = {
    # upstream SYNONYM_GROUPS
    "check/verify/confirm/validate": ("check", "verify", "confirm", "validate"),
    "delete/remove/erase (+retire)": ("delete", "remove", "erase", "retire"),
    "start/launch/begin/initiate": ("start", "launch", "begin", "initiate"),
    "stop/halt/terminate": ("stop", "halt", "terminate"),
    "show/display": ("show", "display"),
    "use/utilize/employ": ("use", "utilize", "employ"),
    "fix/repair/correct": ("fix", "repair", "correct"),
    "send/transmit": ("send", "transmit"),
    "get/retrieve/fetch/obtain (+read)": ("get", "retrieve", "fetch", "obtain", "read"),
    "change/modify/alter": ("change", "modify", "alter"),
    # Tamheed candidates
    "write/record/journal/log": ("write", "record", "journal", "log"),
    "refuse/reject/decline": ("refuse", "reject", "decline"),
    "supersede/replace/override": ("supersede", "replace", "override"),
    "carry/forward/propagate": ("carry", "forward", "propagate"),
    "emit/generate/produce": ("emit", "generate", "produce"),
    "name/cite/reference": ("name", "cite", "reference"),
}

SURFACES = {
    "skills": sorted(BUNDLE.glob("skills/*/SKILL.md")),
    "references": sorted(BUNDLE.glob("references/*.md")),
    "templates": sorted(BUNDLE.glob("templates/*.md")),
    "stock README": [BUNDLE / "prompts" / "README.md"],
    "docs+root": sorted((REPO / "docs").glob("*.md")) + [REPO / p for p in
                 ("README.md", "SECURITY.md", "CLAUDE.md", "CONTRIBUTING.md")],
}
PY_SURFACES = {"server literals": sorted(BUNDLE.glob("server/*.py")) + [BUNDLE / "db" / "store.py"]}

FENCE = re.compile(r"^(```|~~~)")
CODE_SPAN = re.compile(r"`[^`\n]*`")


def word_re(base: str) -> re.Pattern:
    if base.endswith("y"):
        stem = base[:-1] + "(?:y|ies|ied|ying)"
    else:
        stem = base + "(?:s|es|ed|d|ing)?"
    return re.compile(r"\b" + stem + r"\b", re.I)


def md_prose_and_names(path: Path):
    """Yield (kind, text): kind in prose | code | heading."""
    fence = False
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if FENCE.match(s):
            fence = not fence
            continue
        if fence or s.startswith(">"):
            continue
        for m in CODE_SPAN.finditer(line):
            yield "code", m.group(0)
        bare = CODE_SPAN.sub(" ", line)
        yield ("heading" if s.startswith("#") else "prose"), bare


def py_literals(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    doc_nodes = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr):
                value = getattr(body[0], "value", None)
                if isinstance(value, ast.Constant):
                    doc_nodes.add(id(value))
    for node in ast.walk(tree):
        if id(node) in doc_nodes:
            continue
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            text = node.value
        elif isinstance(node, ast.JoinedStr):
            text = "".join(v.value for v in node.values if isinstance(v, ast.Constant))
        else:
            continue
        if len(text.split()) < 6:
            continue
        for m in CODE_SPAN.finditer(text):
            yield "code", m.group(0)
        yield "prose", CODE_SPAN.sub(" ", text)


def engine_names() -> dict[str, list[str]]:
    """Identifiers the engine owns, grouped by kind."""
    out: dict[str, list[str]] = defaultdict(list)
    ddl = (BUNDLE / "db" / "schema.sql").read_text(encoding="utf-8")
    out["table"] = re.findall(r"CREATE TABLE (\w+)", ddl)
    out["column"] = sorted(set(re.findall(r"^\s{2}(\w+)\s+(?:TEXT|INTEGER|REAL)", ddl, re.M)))
    import tamheed_server as srv  # noqa: PLC0415
    out["tool"] = list(srv.TOOLS)
    out["relation"] = sorted(srv.RELATION_RULES)
    ev = re.search(r"event_type\s+TEXT.*?\)\)", ddl, re.S)
    out["event_type"] = re.findall(r"'([a-z-]+)'", ev.group(0)) if ev else []
    wf = (BUNDLE / "references" / "workflow.md").read_text(encoding="utf-8")
    out["stage title"] = re.findall(r"^### \d+\. (.+)$", wf, re.M)
    src = (BUNDLE / "server" / "tamheed_server.py").read_text(encoding="utf-8")
    out["readiness rule"] = sorted(set(re.findall(r'rule\("([a-z-]+)"', src)))
    out["gate"] = sorted(set(re.findall(r"\bG-[A-Z-]+\b", src)))
    out["skill"] = sorted(p.parent.name for p in BUNDLE.glob("skills/*/SKILL.md"))
    return out


def main() -> None:
    counts: dict[str, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
    code_hits: dict[str, Counter] = defaultdict(Counter)
    heading_hits: dict[str, Counter] = defaultdict(Counter)
    samples: dict[str, list[str]] = defaultdict(list)
    regs = {w: word_re(w) for g in GROUPS.values() for w in g}

    def take(surface: str, items):
        for kind, text in items:
            for w, rx in regs.items():
                for m in rx.finditer(text):
                    if kind == "code":
                        code_hits[w][m.group(0)] += 1
                    elif kind == "heading":
                        heading_hits[w][text.strip()[:60]] += 1
                    else:
                        counts[w][surface][m.group(0).lower()] += 1
                        if len(samples[w]) < 4 and surface in ("skills", "server literals"):
                            i = max(0, m.start() - 50)
                            samples[w].append(text[i:m.end() + 50].replace("\n", " ").strip())

    for surface, paths in SURFACES.items():
        for p in paths:
            take(surface, md_prose_and_names(p))
    for surface, paths in PY_SURFACES.items():
        for p in paths:
            take(surface, py_literals(p))

    names = engine_names()
    cols = list(SURFACES) + list(PY_SURFACES)
    print("# Vocabulary census (plan 179, read-only)\n")
    print("Counts are inflected uses in prose outside code spans, fenced code and blockquotes. "
          "`in code` counts the word inside backticks (a name, never rewritten). `names` lists "
          "engine identifiers that contain the word (a name cannot change in a MINOR).\n")
    for group, words in GROUPS.items():
        print(f"## {group}\n")
        print("| word | " + " | ".join(cols) + " | total | in code | headings |")
        print("|---|" + "---|" * (len(cols) + 3))
        for w in words:
            row = [sum(counts[w][s].values()) for s in cols]
            print(f"| {w} | " + " | ".join(str(x) for x in row) + f" | {sum(row)} | "
                  f"{sum(code_hits[w].values())} | {sum(heading_hits[w].values())} |")
        for w in words:
            rx = word_re(w)
            hits = [f"{kind}: {n}" for kind, ns in names.items() for n in ns
                    if rx.search(n.replace("_", " ").replace("-", " "))]
            if hits:
                more = " ..." if len(hits) > 14 else ""
                print(f"- names containing **{w}**: " + ", ".join(hits[:14]) + more)
        for w in words:
            if samples[w]:
                print(f"- samples **{w}**: " + " / ".join(f"...{s}..." for s in samples[w][:3]))
        print()


if __name__ == "__main__":
    main()
