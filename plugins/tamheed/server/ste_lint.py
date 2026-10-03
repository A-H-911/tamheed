"""Plain-English (ASD-STE100) structural linter for Tamheed prose.

A port of ``scripts/ste-lint.py`` from danyuchn/asd-ste100-skill, MIT License,
Copyright (c) 2026 Dustin Yuchen Teng. The rule regexes for semicolons, phrasal verbs,
marketing adjectives, nominalizations, passive voice and compound tenses, the Markdown
table handling and the dangling-conjunction check come from that file. The full license
text is in ``plugins/tamheed/THIRD-PARTY-NOTICES.md``. Tamheed added the paragraph join,
the frontmatter and Python-literal extractors, the vocabulary tables, the Arabic rules and
the allow marker (plan 180).

What this module checks is the STRUCTURAL half of the standard: the half that needs no
dictionary. It never flags a hedge (may, might, could): confidence is content, and a rewrite
that drops a hedge changes the claim. Passive voice and compound tenses are advisory.

Usage::

    python ste_lint.py [--mode strict|flavored] [--lang en|ar] [--vocab FILE] [--json] FILE...

Exit 1 when a hard finding exists. ``--mode flavored`` makes the vocabulary rule advisory.
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

HARD = "hard"
ADVISORY = "advisory"
MAX_WORDS = 25
LENGTH_EXEMPT_KINDS = frozenset({"heading", "table-header"})
ABBREVIATIONS = ("e.g.", "i.e.", "etc.", "vs.", "cf.")
MIN_LITERAL_WORDS = 6
ALLOW_REASON_MIN = 8

# ---------------------------------------------------------------- the ported rules
# (id, level, regex, message). Semicolon and vocabulary are handled apart from this list
# because they take the language and the vocabulary file into account.
RULES = [
    ("phrasal-verb", HARD,
     re.compile(r"\b(spin(?:ning|s)? up|spun up|reach(?:ing|es|ed)? out|div(?:e|es|ing|ed) into"
                r"|dove into|kick(?:ing|s|ed)? off|circl(?:e|es|ing|ed) back|touch(?:ing|es|ed)? base)\b",
                re.I),
     "Soft phrasal verb. Use the single plain verb (start, contact, read, begin)."),
    ("marketing-adjective", HARD,
     re.compile(r"\b(seamless(?:ly)?|robust(?:ly)?|cutting-edge|effortless(?:ly)?|blazing[- ]fast"
                r"|world-class|state-of-the-art|game-chang(?:ing|er))\b", re.I),
     "Marketing adjective. Delete it, or replace it with the measurement that earns the claim."),
    ("nominalization", HARD,
     re.compile(r"\b(perform|performs|performed|conduct|conducts|conducted|carry out|carries out"
                r"|carried out)\s+(?:a|an|the)\s+\w+(?:tion|sion|ment|ance|ence|ysis)\b", re.I),
     "Action frozen into a noun. Use the verb (analyze, not perform an analysis of)."),
    ("passive-voice", ADVISORY,
     re.compile(r"\b(is|are|was|were|been|being)\s+(\w+ed|given|taken|made|done|found|seen|known"
                r"|shown|written|built|sent|set|run|read|kept|held|left|put)\b"
                r"(?!\s+(?:to|for|by)\s+\w+ing)", re.I),
     "Possible passive voice. Name the actor and use an active verb, unless the actor is unknown."),
    ("present-perfect", ADVISORY,
     # a modal + perfect infinitive ("may have failed") is a protected hedge, never flagged
     re.compile(r"(?<!\bmay )(?<!\bmight )(?<!\bcould )(?<!\bshould )(?<!\bwould )(?<!\bmust )"
                r"\b(has|have|had)\s+(?:been\s+)?\w+(?:ed|en)\b", re.I),
     "Compound tense. Use the simple past or present unless current relevance is the point."),
]
SEMICOLON = re.compile(r"[;\u061b]")  # ; and the Arabic semicolon
SENTENCE_END = re.compile(r"(?<=[.!?\u061f])\s+")  # . ! ? and the Arabic question mark
CONJUNCTION_END = re.compile(r"\b(?:and|or)\s*$", re.I)
ALLOW = re.compile(r"ste:allow\s+(?P<rule>[a-z-]+)(?::\s*(?P<reason>.*?))?\s*$")

# ---------------------------------------------------------------- Markdown shapes
_FENCE = re.compile(r"^\s{0,3}(```|~~~)")
_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$")
_LIST = re.compile(r"^(?P<indent>\s*)(?P<marker>[-*+]|\d+[.)])\s+(?P<body>.*)$")
_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)*\|?\s*$")
_HR = re.compile(r"^\s{0,3}(?:-{3,}|\*{3,}|_{3,})\s*$")
_COMMENT_ONE_LINE = re.compile(r"^\s*<!--(?P<body>.*?)-->\s*$")
_CODE_SPAN = re.compile(r"`[^`\n]*`")
_LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
_HTML_CELL = re.compile(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", re.S | re.I)
_TAG = re.compile(r"<[^>]+>")

# ---------------------------------------------------------------- Python literal shapes
_REGEX_META = re.compile(r"\\[bswdBSWD]|\(\?|\[\^")
_SQL_START = re.compile(r"^\s*(?:SELECT|INSERT|UPDATE|DELETE|PRAGMA|CREATE|WITH|ALTER|DROP)\b", re.I)
_MARKUP = re.compile(
    r"</|<(?:div|span|p|a|td|th|tr|table|thead|tbody|tfoot|caption|col|colgroup|ul|ol|li|dl|dt|dd"
    r"|h[1-6]|section|article|aside|figure|figcaption|svg|g|path|text|tspan|rect|line|polyline"
    r"|polygon|circle|ellipse|marker|defs|use|symbol|clipPath|linearGradient|stop|foreignObject"
    r"|meta|link|style|script|noscript|title|details|summary|nav|header|footer|main|button|label"
    r"|input|select|option|textarea|form|img|br|hr|code|pre|em|strong|small|sup|sub|b|i|u|s"
    r"|html|head|body|blockquote|iframe|canvas)\b|\b(?:style|class|href)=", re.I)
_LETTERS3 = re.compile(r"[A-Za-z]{3}")


def _block(line: int, kind: str, text: str, allow=None, bad_allow=None) -> dict:
    return {"line": line, "kind": kind, "text": text,
            "allow": set(allow or ()), "bad_allow": list(bad_allow or ())}


def _inline(text: str) -> str:
    """Code spans become the one token CODE, links become their text, emphasis marks go."""
    text = _CODE_SPAN.sub(" CODE ", text)
    text = _LINK.sub(r"\1", text)
    text = text.replace("**", "").replace("__", "")
    text = re.sub(r"(?<!\w)\*|\*(?!\w)", "", text)
    return " ".join(text.split())


def _parse_allow(body: str):
    """Return (rule, ok) for an allow marker body, or None when the comment is not one."""
    m = ALLOW.search(body)
    if not m:
        return None
    reason = (m.group("reason") or "").strip()
    return m.group("rule"), len(reason) >= ALLOW_REASON_MIN


# ---------------------------------------------------------------- vocabulary
def _tables(text: str) -> list[tuple[list[str], list[list[str]]]]:
    """Every Markdown table in a file as (header cells, body rows)."""
    out = []
    lines = text.replace("\r\n", "\n").split("\n")
    i = 1
    while i < len(lines):
        if "|" in lines[i - 1] and _TABLE_SEP.match(lines[i]):
            header = _cells(lines[i - 1])
            rows = []
            j = i + 1
            while j < len(lines) and "|" in lines[j] and not _TABLE_SEP.match(lines[j]):
                rows.append(_cells(lines[j]))
                j += 1
            out.append((header, rows))
            i = j
        i += 1
    return out


def _cells(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def load_vocabulary(path) -> dict:
    """Parse references/vocabulary.md into approved verbs, rejected words, terms and names.

    The three tables carry fixed headers. A missing header is an error: the gate would
    otherwise pass with an empty vocabulary.
    """
    text = Path(path).read_text(encoding="utf-8")
    wanted = {
        ("action", "approved verb", "rejected synonyms"): "actions",
        ("term", "one meaning", "never means"): "terms",
        ("name", "where it is a name"): "names",
    }
    found: dict[str, list[list[str]]] = {}
    for header, rows in _tables(text):
        key = wanted.get(tuple(h.lower() for h in header))
        if key:
            found[key] = rows
    missing = sorted(set(wanted.values()) - set(found))
    if missing:
        raise ValueError(f"vocabulary file {path} lacks the table(s): {', '.join(missing)}")
    approved: dict[str, str] = {}
    rejected: dict[str, str] = {}
    for action, verb, synonyms in found["actions"]:
        approved[action] = verb.strip("`")
        for word in re.findall(r"`([^`]+)`", synonyms):
            rejected.setdefault(word.strip().lower(), verb.strip("`"))
    terms = {row[0].strip("`"): row[1] for row in found["terms"] if row and row[0]}
    names = {row[0].strip("`"): row[1] for row in found["names"] if row and row[0]}
    return {"approved": approved, "rejected": rejected, "terms": terms, "names": names}


def _word_re(base: str) -> re.Pattern:
    """Inflections of a word, including the -y forms upstream lacked (modify -> modifies)."""
    if base.endswith("y"):
        stem = re.escape(base[:-1]) + "(?:y|ies|ied|ying)"
    else:
        stem = re.escape(base) + "(?:s|es|ed|d|ing)?"
    return re.compile(r"\b" + stem + r"\b", re.I)


# ---------------------------------------------------------------- Markdown extraction
def _frontmatter_description(fm: list[str], first_line: int):
    """The `description:` value of a skill's frontmatter, folded lines joined."""
    for i, line in enumerate(fm):
        m = re.match(r"^description:\s*(.*)$", line)
        if not m:
            continue
        value = m.group(1).strip()
        parts = []
        if value and value not in (">-", ">", "|", "|-"):
            parts.append(value.strip("\"'"))
        j = i + 1
        while j < len(fm) and (fm[j].startswith((" ", "\t")) or not fm[j].strip()):
            if fm[j].strip():
                parts.append(fm[j].strip())
            j += 1
        return first_line + i, " ".join(parts)
    return None


def extract_markdown_prose(text: str, *, filename: str = "<text>") -> list[dict]:
    """Prose blocks of a Markdown file, paragraphs joined, with the exemptions applied.

    Dropped: fenced code, blockquote lines, HTML comments (after an allow marker is read),
    frontmatter keys other than `description`, horizontal rules. Kept as blocks: the
    description, headings, table header cells, table body cells (Markdown and HTML tables),
    list items with their continuation lines, paragraphs.
    """
    lines = text.replace("\r\n", "\n").split("\n")
    blocks: list[dict] = []
    allow_at: dict[int, tuple] = {}  # line index -> (rule, ok)
    i = 0
    if lines and lines[0].strip() == "---":
        j = 1
        while j < len(lines) and lines[j].strip() != "---":
            j += 1
        desc = _frontmatter_description(lines[1:j], 2)
        if desc:
            blocks.append(_block(desc[0], "description", _inline(desc[1])))
        i = j + 1

    para: list[tuple[int, str]] = []
    item: list[tuple[int, str]] = []

    def pending_allow(start: int):
        k = start - 1
        while k >= 0 and not lines[k].strip():
            k -= 1
        marker = allow_at.get(k)
        if not marker:
            return set(), []
        rule, ok = marker
        return ({rule} if ok else set()), ([] if ok else [k + 1])

    def flush():
        nonlocal para, item
        for buf, kind in ((item, "item"), (para, "paragraph")):
            if buf:
                start = buf[0][0]
                allow, bad = pending_allow(start)
                blocks.append(_block(start + 1, kind, _inline(" ".join(t for _, t in buf)),
                                     allow, bad))
        para, item = [], []

    in_fence = False
    while i < len(lines):
        raw = lines[i]
        s = raw.strip()
        if _FENCE.match(raw):
            flush()
            in_fence = not in_fence
            i += 1
            continue
        if in_fence:
            i += 1
            continue
        if not s or _HR.match(raw):
            flush()
            i += 1
            continue
        if s.startswith(">"):
            flush()
            i += 1
            continue
        m = _COMMENT_ONE_LINE.match(raw)
        if m:
            flush()
            parsed = _parse_allow(m.group("body"))
            if parsed:
                allow_at[i] = parsed
            i += 1
            continue
        if s.startswith("<!--"):
            flush()
            while i < len(lines) and "-->" not in lines[i]:
                i += 1
            i += 1
            continue
        if s.lower().startswith("<table"):
            flush()
            start = i
            html = []
            while i < len(lines):
                html.append(lines[i])
                if "</table>" in lines[i].lower():
                    break
                i += 1
            i += 1
            for cell in _HTML_CELL.findall("\n".join(html)):
                cell_text = _inline(_TAG.sub(" ", cell))
                if cell_text:
                    blocks.append(_block(start + 1, "table-cell", cell_text))
            continue
        if "|" in s and i + 1 < len(lines) and _TABLE_SEP.match(lines[i + 1]):
            flush()
            allow, bad = pending_allow(i)
            for cell in _cells(raw):
                if cell:
                    blocks.append(_block(i + 1, "table-header", _inline(cell), allow, bad))
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip() \
                    and not _TABLE_SEP.match(lines[i]):
                for cell in _cells(lines[i]):
                    if cell:
                        blocks.append(_block(i + 1, "table-cell", _inline(cell), allow, bad))
                i += 1
            continue
        h = _HEADING.match(raw)
        if h:
            flush()
            allow, bad = pending_allow(i)
            blocks.append(_block(i + 1, "heading", _inline(h.group(1)), allow, bad))
            i += 1
            continue
        li = _LIST.match(raw)
        if li:
            flush()
            item = [(i, li.group("body"))]
            i += 1
            continue
        if item and raw[:1].isspace():
            item.append((i, s))
            i += 1
            continue
        if item:
            flush()
        para.append((i, s))
        i += 1
    flush()
    return blocks


# ---------------------------------------------------------------- Python extraction
def _docstring_ids(tree: ast.AST) -> set[int]:
    ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr):
                value = getattr(body[0], "value", None)
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    ids.add(id(value))
    return ids


def _code_shaped(text: str) -> bool:
    if not text.strip() or len(text.split()) < MIN_LITERAL_WORDS:
        return True
    if " " not in text.strip():
        return True
    if _REGEX_META.search(text) or _SQL_START.match(text) or _MARKUP.search(text):
        return True
    tokens = [t for t in text.split() if any(ch.isalnum() for ch in t)]  # `|` is layout
    lettered = sum(1 for t in tokens if _LETTERS3.search(t))
    return lettered * 2 < len(tokens)


def extract_python_literals(source: str, *, filename: str = "<source>") -> list[dict]:
    """Runtime string literals of a Python source, docstrings and code shapes skipped.

    An f-string's constant parts are joined with the token X in each slot. A string is
    code-shaped when it is short, has no space, carries regex metacharacters, starts with an
    SQL verb, is markup (a known HTML/SVG tag name or an attribute, never a bare angle
    bracket: `<package>` is prose) or is digit-heavy (path data). The allow marker is a
    `# ste:allow <rule>: <reason>` comment on the line above the literal.
    """
    source = source.replace("\r\n", "\n")
    tree = ast.parse(source)
    lines = source.split("\n")
    skip = _docstring_ids(tree)
    for node in ast.walk(tree):  # an f-string's constant parts are read with the f-string
        if isinstance(node, ast.JoinedStr):
            skip.update(id(v) for v in node.values if isinstance(v, ast.Constant))
    blocks: list[dict] = []
    for node in ast.walk(tree):
        if id(node) in skip:
            continue
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            text = node.value
        elif isinstance(node, ast.JoinedStr):
            text = "".join(v.value if isinstance(v, ast.Constant) and isinstance(v.value, str)
                           else " X " for v in node.values)
        else:
            continue
        if _code_shaped(text):
            continue
        allow: set = set()
        bad: list = []
        above = lines[node.lineno - 2] if node.lineno >= 2 else ""
        if "# ste:allow" in above:
            parsed = _parse_allow(above.split("#", 1)[1])
            if parsed:
                rule, ok = parsed
                if ok:
                    allow.add(rule)
                else:
                    bad.append(node.lineno - 1)
        if "\n" in text.strip():
            # A multi-line literal is Markdown (the operating note, a stale-warning block):
            # its headings, table rows and paragraphs are read as such, each at the
            # literal's line, so a table row is never one long sentence.
            for sub in extract_markdown_prose(text, filename=filename):
                blocks.append(_block(node.lineno, sub["kind"], sub["text"], allow, bad))
            continue
        blocks.append(_block(node.lineno, "literal", _inline(text), allow, bad))
    return blocks


# ---------------------------------------------------------------- sentences and rules
def split_sentences(text: str) -> list[str]:
    """Split on . ! ? and the Arabic question mark followed by whitespace. An abbreviation
    in ABBREVIATIONS never ends a sentence, and a dot inside a token never splits."""
    protected = text
    for abbr in ABBREVIATIONS:
        protected = re.sub(re.escape(abbr), abbr.replace(".", "\u0000"), protected, flags=re.I)
    return [p.replace("\u0000", ".") for p in SENTENCE_END.split(protected) if p.strip()]


def _name_heavy(sentence: str) -> bool:
    """A sentence made of names: code spans or quoted phrases are at least half its tokens."""
    tokens = sentence.split()
    if not tokens:
        return False
    quoted = sum(len(m.group(0).split()) for m in re.finditer(r'"[^"]*"', sentence))
    code = sum(1 for t in tokens if t.strip(".,:;()[]") == "CODE")
    return (quoted + code) * 2 >= len(tokens)


def _finding(filename: str, line: int, rule: str, level: str, match: str, message: str) -> dict:
    return {"file": filename, "line": line, "rule": rule, "level": level,
            "match": match, "message": message}


def lint_blocks(blocks: list[dict], *, mode: str = "strict", lang: str = "en", vocab=None,
                filename: str = "<text>", skip_rules=()) -> list[dict]:
    """Apply the rules to extracted blocks. `lang="ar"` runs the semicolon and length rules
    only. `mode="flavored"` makes the vocabulary rule advisory."""
    skip = set(skip_rules)
    findings: list[dict] = []
    rejected = []
    names = []
    if vocab:
        rejected = [(w, v, _word_re(w)) for w, v in vocab["rejected"].items()]
        names = sorted(vocab["names"], key=len, reverse=True)
    for b in blocks:
        text, line, allow = b["text"], b["line"], b.get("allow", set())
        for bad_line in b.get("bad_allow", ()):
            findings.append(_finding(filename, bad_line, "allow-without-reason", HARD, "ste:allow",
                                     "An allow marker needs a reason: `ste:allow <rule>: <reason>`."))

        def add(rule, level, match, message, at=line):
            if rule not in skip and rule not in allow:
                findings.append(_finding(filename, at, rule, level, match, message))

        for m in SEMICOLON.finditer(text):
            add("semicolon", HARD, m.group(0),
                "STE bans the semicolon (Rule 8.1). Write two sentences.")
        if b["kind"] not in LENGTH_EXEMPT_KINDS:
            for sentence in split_sentences(text):
                n = len(sentence.split())
                if n > MAX_WORDS and not _name_heavy(sentence):
                    add("long-sentence", HARD, f"{n} words",
                        f"Sentence has {n} words (cap {MAX_WORDS}). Split it.")
        if lang == "ar":
            continue
        for rule_id, level, pattern, msg in RULES:
            for m in pattern.finditer(text):
                add(rule_id, level, m.group(0), msg)
        if b["kind"] == "item" and CONJUNCTION_END.search(text):
            add("dangling-conjunction", HARD, text.split()[-1],
                "List item ends with a coordinating conjunction. Complete the item.")
        if rejected:
            masked = text
            for name in names:
                masked = masked.replace(name, " NAME ")
            level = HARD if mode == "strict" else ADVISORY
            for word, approved, rx in rejected:
                for m in rx.finditer(masked):
                    add("vocabulary", level, m.group(0),
                        f"`{word}` is rejected in vocabulary.md. Use `{approved}`.")
    findings.sort(key=lambda f: (f["line"], f["rule"]))
    return findings


def word_count(blocks: list[dict]) -> int:
    return sum(len(b["text"].split()) for b in blocks)


def lint_text(text: str, *, mode: str = "strict", lang: str = "en", vocab=None,
              filename: str = "<text>", skip_rules=()) -> list[dict]:
    """Lint a Markdown text."""
    return lint_blocks(extract_markdown_prose(text, filename=filename), mode=mode, lang=lang,
                       vocab=vocab, filename=filename, skip_rules=skip_rules)


def lint_source(source: str, *, mode: str = "strict", lang: str = "en", vocab=None,
                filename: str = "<source>", skip_rules=()) -> list[dict]:
    """Lint the runtime string literals of a Python source."""
    return lint_blocks(extract_python_literals(source, filename=filename), mode=mode, lang=lang,
                       vocab=vocab, filename=filename, skip_rules=skip_rules)


def lint_path(path, *, mode: str = "strict", lang: str = "en", vocab=None,
              skip_rules=()) -> tuple[list[dict], int]:
    """Lint one file by its suffix. Returns (findings, words)."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    name = p.as_posix()
    if p.suffix == ".py":
        blocks = extract_python_literals(text, filename=name)
    else:
        blocks = extract_markdown_prose(text, filename=name)
    return (lint_blocks(blocks, mode=mode, lang=lang, vocab=vocab, filename=name,
                        skip_rules=skip_rules), word_count(blocks))


def hard(findings: list[dict]) -> list[dict]:
    return [f for f in findings if f["level"] == HARD]


def _default_vocab():
    candidate = Path(__file__).resolve().parent.parent / "references" / "vocabulary.md"
    return load_vocabulary(candidate) if candidate.is_file() else None


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    mode, lang, as_json, vocab_path, paths = "strict", "en", False, None, []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--mode":
            i += 1
            mode = argv[i]
        elif a == "--lang":
            i += 1
            lang = argv[i]
        elif a == "--vocab":
            i += 1
            vocab_path = argv[i]
        elif a == "--json":
            as_json = True
        elif not a.startswith("--"):
            paths.append(a)
        i += 1
    vocab = load_vocabulary(vocab_path) if vocab_path else _default_vocab()
    findings: list[dict] = []
    words = 0
    for p in paths:
        f, w = lint_path(p, mode=mode, lang=lang, vocab=vocab)
        findings.extend(f)
        words += w
    hard_n = len(hard(findings))
    if as_json:
        print(json.dumps({"findings": findings, "hard": hard_n,
                          "advisory": len(findings) - hard_n, "words": words}, indent=2))
    else:
        for f in findings:
            print(f"{f['file']}:{f['line']} {f['rule']} ({f['level']}): {f['message']} [{f['match']}]")
        print(f"{len(findings)} findings ({hard_n} hard, {len(findings) - hard_n} advisory), "
              f"{words} words. Hedges (may, might, could) are never flagged.")
    return 1 if hard_n else 0


if __name__ == "__main__":
    sys.exit(main())
