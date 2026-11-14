"""Tamheed interview page (plans 227, 227b, 227c): a slate of questions as one local page,
and a reader for the answers files that the page saves.

This module is the slate's grammar: what a slate may hold, and why one is refused. The rows
that a page quotes are in `slate_rows`, the reader is in `slate_answers`, the markup is in
`slate_page` and `slate_round`. Their names are also offered here.

The page carries the questions. The session carries the word: an answers file is a record of
what was clicked on a page, never the operator's approval (operator-interview, step 7).

Security doctrine, as for the review page, with one difference: this page runs ONE script.
- Every text of the slate and of a quoted row passes `esc()` at render.
- The script is the static file `slate.js`, the same for every slate. The page names it by
  hash in a content policy, so no other script runs: not an inline handler, not a script
  that a row's text tries to add.
- The script reads ids from data attributes, sets values and classes, and copies markup only
  from a template that the server rendered. The page holds no data block.
- The page loads nothing and sends nothing (`default-src 'none'`).

Determinism: the same slate over the same rows gives the same bytes. The page has no clock.
"""
from __future__ import annotations

import json
import re

ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,31}")      # used with fullmatch
OTHER, UNKNOWN, EVIDENCE = "other", "unknown", "evidence"
RESERVED = {OTHER: "the free answer", UNKNOWN: "the answer that nobody knows",
            EVIDENCE: "the answer that needs evidence"}
LANGUAGES = ("en", "ar")
OPENS = ("reading", "session")        # R112: how a page opens
OWNERS = ("room", "operator")
BASES = ("evidence", "ruling", "practice")
DEFAULT_KINDS = ("pain", "concern", "expectation", "requirement")
DEFAULT_CLOSURE = ("conclusions", "open_questions", "approvals", "commitments")
CAPS = {"title": 200, "intro": 8000, "question": 2000, "detail": 8000, "label": 500,
        "reason": 2000, "name": 200, "answer": 4000, "gap": 2000, "block": 200}
MAX_ROUNDS, MAX_QUESTIONS, MAX_OPTIONS, MAX_CITES = 50, 500, 12, 30
MAX_PARTICIPANTS, MAX_LABELLED, MAX_DECIDED, MAX_TERMS = 60, 12, 200, 200
MAX_FILE_BYTES = 2_000_000            # a spec file and an answers file, each
MAX_RECORD_BYTES = 20_000_000         # the slate record, at export and at read
MAX_PAGE_CHARS = 20_000_000           # the quoted text of a page, every citation counted
MAX_ANSWER_TEXT = 8000                # a note, a free answer, a point, a closure field
MAX_POINTS = 200                      # the points of one round
ANSWERS_FORMAT, RECORD_FORMAT, VERSION = "tamheed-slate-answers", "tamheed-slate", 2

_SLATE_KEYS = {"name", "title", "intro", "language", "opens", "participants", "point_kinds",
               "closure_fields", "terms", "rounds"}
_ROUND_KEYS = {"id", "title", "intro", "cites", "ready", "questions", "blocks", "decided"}
_BLOCK_KEYS = {"title", "questions"}
_DECIDED_KEYS = {"id", "title", "answer", "cites"}
_QUESTION_KEYS = {"id", "question", "detail", "cites", "allow_other", "allow_unsure",
                  "options", "recommended", "reason", "basis", "owner", "lead", "consulted",
                  "approval", "known", "decided", "depends_on", "gap", "settles", "block"}
_OPTION_KEYS = {"id", "label", "detail"}
_PARTICIPANT_KEYS = {"id", "name", "attends"}
_LABELLED_KEYS = {"id", "label"}


class Refused(ValueError):
    """Why a slate is refused. `check_slate` turns it into its second answer."""


# --------------------------------------------------------------------------- small checks

def encodable(value: str) -> bool:
    """False for text that UTF-8 cannot hold (a lone surrogate): it cannot be written."""
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def short(value) -> str:
    """A value of a file, as an error may echo it: 60 characters at most, never whole."""
    plain = isinstance(value, (str, int, float, bool, type(None)))
    text = repr(value) if plain else type(value).__name__
    return text if len(text) <= 60 else text[:57] + "..."


def _keys(owner: str, obj, allowed: set) -> None:
    if not isinstance(obj, dict):
        raise Refused(f"{owner} is an object")
    if extra := sorted(str(k) for k in set(obj) - allowed):
        raise Refused(f"{owner} has unknown key(s) {extra}. It takes"
                      f" {', '.join(sorted(allowed))}")


def _text(owner: str, obj: dict, key: str, required: bool = False) -> str:
    value = obj.get(key)
    if value is None or value == "":
        if required:
            raise Refused(f"{owner} needs `{key}`")
        return ""
    if not isinstance(value, str) or not encodable(value):
        raise Refused(f"{owner}: `{key}` is text")
    if len(value) > CAPS[key]:
        raise Refused(f"{owner}: `{key}` holds {len(value)} characters (the cap is"
                      f" {CAPS[key]})")
    return value


def _ident(owner: str, value) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise Refused(f"{owner} needs an `id` of 1 to 32 letters, digits, dots, dashes or"
                      f" underscores (got {short(value)})")
    return value


def _flag(owner: str, obj: dict, key: str, default: bool) -> bool:
    value = obj.get(key, default)
    if not isinstance(value, bool):
        raise Refused(f"{owner}: `{key}` is true or false")
    return value


def _choice(owner: str, obj: dict, key: str, allowed: tuple, default):
    value = obj.get(key)
    if value is None:
        return default
    if value not in allowed:
        raise Refused(f"{owner}: `{key}` is one of: {', '.join(allowed)} (got {short(value)})")
    return value


def _ids(owner: str, obj: dict, key: str, what: str = "row ids") -> list:
    """A list of ids under `key`: in order, each once, capped."""
    items = [] if obj.get(key) is None else obj[key]
    if not isinstance(items, list) \
            or not all(isinstance(i, str) and i and encodable(i) for i in items):
        raise Refused(f"{owner}: `{key}` is a list of {what}")
    if len(items) > MAX_CITES:
        raise Refused(f"{owner}: `{key}` holds {len(items)} ids (the cap is {MAX_CITES})")
    return list(dict.fromkeys(items))


# --------------------------------------------------------------------------- the parts

def _participants(slate: dict) -> list:
    """R108: each participant is the id of a row, or {id, name, attends}. A name left empty
    is read from the row at export. `attends` false names a person who leads or is
    consulted and has no attendance line."""
    items = [] if slate.get("participants") is None else slate["participants"]
    if not isinstance(items, list) or len(items) > MAX_PARTICIPANTS:
        raise Refused(f"the slate's `participants` is a list of {MAX_PARTICIPANTS} at most")
    out, seen = [], set()
    for n, item in enumerate(items):
        owner = f"participant {n + 1}"
        item = {"id": item} if isinstance(item, str) else item
        _keys(owner, item, _PARTICIPANT_KEYS)
        pid = _ident(owner, item.get("id"))
        if pid in seen:
            raise Refused(f"the participant id {pid!r} is used twice")
        seen.add(pid)
        out.append({"id": pid, "name": _text(f"participant {pid}", item, "name"),
                    "attends": _flag(f"participant {pid}", item, "attends", True)})
    return out


def _labelled(slate: dict, key: str, defaults: tuple) -> list:
    """R106: the kinds of a round's points, or the fields of its closure. The defaults carry
    no label: the page has words for them in its own language."""
    if slate.get(key) is None:
        return [{"id": ident, "label": ""} for ident in defaults]
    items = slate[key]
    if not isinstance(items, list) or not items or len(items) > MAX_LABELLED:
        raise Refused(f"the slate's `{key}` is a list of one or more {{id, label}}, and of"
                      f" {MAX_LABELLED} at most")
    out, seen = [], set()
    for n, item in enumerate(items):
        owner = f"`{key}`, item {n + 1}"
        _keys(owner, item, _LABELLED_KEYS)
        ident = _ident(owner, item.get("id"))
        if ident in seen:
            raise Refused(f"the id {ident!r} is used twice in `{key}`")
        seen.add(ident)
        out.append({"id": ident, "label": _text(owner, item, "label", ident not in defaults)})
    return out


def _options(owner: str, q: dict) -> list:
    options = q.get("options")
    if not isinstance(options, list) or len(options) < 2:
        raise Refused(f"{owner} needs two or more options")
    if len(options) > MAX_OPTIONS:
        raise Refused(f"{owner} has {len(options)} options (the cap is {MAX_OPTIONS})")
    out, seen = [], set()
    for n, option in enumerate(options):
        where = f"{owner}, option {n + 1}"
        _keys(where, option, _OPTION_KEYS)
        oid = _ident(where, option.get("id"))
        if oid in RESERVED:
            raise Refused(f"{where}: the id {oid!r} is reserved for {RESERVED[oid]}")
        if oid in seen:
            raise Refused(f"{where}: the id {oid!r} is used twice in this question")
        seen.add(oid)
        out.append({"id": oid, "label": _text(where, option, "label", True),
                    "detail": _text(where, option, "detail")})
    return out


def _question(owner: str, q, block: str) -> dict:
    _keys(owner, q, _QUESTION_KEYS)
    out: dict = {"id": _ident(owner, q.get("id"))}
    owner = f"question {out['id']}"
    for key, required in (("question", True), ("detail", False), ("reason", False),
                          ("gap", False)):
        out[key] = _text(owner, q, key, required)
    out["block"] = _text(owner, q, "block") or block
    for key in ("cites", "known", "decided"):
        out[key] = _ids(owner, q, key)
    out["consulted"] = _ids(owner, q, "consulted", "participant ids")
    out["depends_on"] = _ids(owner, q, "depends_on", "question ids")
    for key, default in (("allow_other", True), ("allow_unsure", True), ("approval", False)):
        out[key] = _flag(owner, q, key, default)
    out["owner"] = _choice(owner, q, "owner", OWNERS, "room")
    out["basis"] = _choice(owner, q, "basis", BASES, None)
    for key in ("lead", "settles"):
        value = q.get(key)
        if value is not None and (not isinstance(value, str) or not value):
            raise Refused(f"{owner}: `{key}` is one id")
        out[key] = value
    out["options"] = _options(owner, q)
    recommended = q.get("recommended")
    if recommended is None:
        for key in ("reason", "basis"):
            if out[key]:
                raise Refused(f"{owner} gives a `{key}` and recommends no option")
    elif not isinstance(recommended, str) \
            or recommended not in {o["id"] for o in out["options"]}:
        raise Refused(f"{owner} recommends {short(recommended)}, which is none of its options")
    elif not out["reason"]:
        raise Refused(f"{owner} recommends an option and gives no `reason`. A recommendation"
                      " carries its deciding reason")
    out["recommended"] = recommended
    return out


def _round(n: int, rnd) -> dict:
    owner = f"round {n + 1}"
    _keys(owner, rnd, _ROUND_KEYS)
    item = {"id": _ident(owner, rnd.get("id"))}
    owner = f"round {item['id']}"
    for key, required in (("title", True), ("intro", False)):
        item[key] = _text(owner, rnd, key, required)
    item["cites"] = _ids(owner, rnd, "cites")
    item["ready"] = _flag(owner, rnd, "ready", True)
    if rnd.get("blocks") is not None and rnd.get("questions") is not None:
        raise Refused(f"{owner} gives `blocks` and `questions`. Give one")
    groups = [{"title": "", "questions": rnd.get("questions")}]
    if rnd.get("blocks") is not None:
        groups = rnd["blocks"]
        if not isinstance(groups, list):
            raise Refused(f"{owner}: `blocks` is a list of {{title, questions}}")
    item["questions"] = []
    for b, group in enumerate(groups):
        where = f"{owner}, block {b + 1}"
        _keys(where, group, _BLOCK_KEYS)
        questions = [] if group.get("questions") is None else group["questions"]
        if not isinstance(questions, list):
            raise Refused(f"{where}: `questions` is a list")
        title = _text(where, group, "title") if "title" in group else ""
        item["questions"].extend(_question(f"{owner}, question {m + 1}", q, title)
                                 for m, q in enumerate(questions))
    if item["ready"] and not item["questions"]:
        raise Refused(f"{owner} needs one or more `questions`")
    decided = [] if rnd.get("decided") is None else rnd["decided"]
    if not isinstance(decided, list) or len(decided) > MAX_DECIDED:
        raise Refused(f"{owner}: `decided` is a list of {MAX_DECIDED} at most")
    item["decided"] = []
    for d, topic in enumerate(decided):
        where = f"{owner}, decided topic {d + 1}"
        _keys(where, topic, _DECIDED_KEYS)
        tid = _ident(where, topic.get("id"))
        item["decided"].append({"id": tid, "title": _text(where, topic, "title", True),
                                "answer": _text(where, topic, "answer", True),
                                "cites": _ids(where, topic, "cites")})
    return item


def _cross_check(out: dict) -> None:
    """Ids that name each other: one name space for questions and decided topics, people
    that a question names, and what a question depends on."""
    people = {p["id"] for p in out["participants"]}
    seen: dict = {}
    for rnd in out["rounds"]:
        for kind, items in (("question ", rnd["questions"]), ("", rnd["decided"])):
            for item in items:
                if item["id"] in seen:
                    raise Refused(f"the {kind}id {item['id']!r} is used twice in the slate")
                seen[item["id"]] = True
    questions = [q for rnd in out["rounds"] for q in rnd["questions"]]
    if len(questions) > MAX_QUESTIONS:
        raise Refused(f"the slate has {len(questions)} questions (the cap is {MAX_QUESTIONS})")
    for q in questions:
        owner = f"question {q['id']}"
        for key, named in (("lead", [q["lead"]] if q["lead"] else []),
                           ("consulted", q["consulted"])):
            if missing := [p for p in named if p not in people]:
                raise Refused(f"{owner}: `{key}` names {missing[0]!r}, which is no participant"
                              " of the slate")
        for target in q["depends_on"]:
            if target == q["id"]:
                raise Refused(f"{owner} depends on itself")
            if target not in seen:
                raise Refused(f"{owner} depends on {target!r}, which is no question or decided"
                              " topic of the slate")


def check_slate(slate) -> tuple[dict | None, str | None]:
    """(the slate with every default filled, None), or (None, why it is refused). The answer
    holds known keys only, in one fixed shape, so the record's bytes follow from it. The
    answer checks to itself."""
    try:
        _keys("the slate", slate, _SLATE_KEYS)
        out = {"name": slate.get("name"),
               "language": _choice("the slate", slate, "language", LANGUAGES, "en"),
               "opens": _choice("the slate", slate, "opens", OPENS, "reading")}
        for key, required in (("title", True), ("intro", False)):
            out[key] = _text("the slate", slate, key, required)
        out["participants"] = _participants(slate)
        out["point_kinds"] = _labelled(slate, "point_kinds", DEFAULT_KINDS)
        out["closure_fields"] = _labelled(slate, "closure_fields", DEFAULT_CLOSURE)
        terms = slate.get("terms")                  # R110: None is every glossary row
        if terms is not None and (not isinstance(terms, list) or len(terms) > MAX_TERMS
                                  or not all(isinstance(t, str) and t for t in terms)):
            raise Refused("the slate's `terms` is a list of glossary row ids, of"
                          f" {MAX_TERMS} at most. Leave it out to match every glossary row")
        out["terms"] = None if terms is None else list(dict.fromkeys(terms))
        rounds = slate.get("rounds")
        if not isinstance(rounds, list) or not rounds:
            raise Refused("the slate needs one or more `rounds`")
        if len(rounds) > MAX_ROUNDS:
            raise Refused(f"the slate has {len(rounds)} rounds (the cap is {MAX_ROUNDS})")
        out["rounds"], folded = [], {}
        for n, rnd in enumerate(rounds):
            item = _round(n, rnd)
            if item["id"] in {r["id"] for r in out["rounds"]}:
                raise Refused(f"the round id {item['id']!r} is used twice")
            # a round's answers file is named by the round's id, and Windows folds case
            if (other := folded.get(item["id"].lower())) is not None:
                raise Refused(f"the round ids {other!r} and {item['id']!r} differ only by case")
            folded[item["id"].lower()] = item["id"]
            out["rounds"].append(item)
        _cross_check(out)
    except Refused as exc:
        return None, str(exc)
    return out, None


def questions_of(slate: dict) -> list:
    """Every question of a checked slate, in order."""
    return [q for rnd in slate["rounds"] for q in rnd["questions"]]


def shown_ids(question: dict) -> list:
    """The rows that one question quotes by its own keys, each once."""
    ids = question["cites"] + question["known"] + question["decided"]
    return list(dict.fromkeys(ids + ([question["settles"]] if question["settles"] else [])))


def cited_ids(slate: dict) -> list[str]:
    """Every row id that the slate names by a key, each once, in the order of first use."""
    ids: dict = {}
    for rnd in slate["rounds"]:
        for cid in rnd["cites"] + [c for t in rnd["decided"] for c in t["cites"]]:
            ids[cid] = True
        for question in rnd["questions"]:
            for cid in shown_ids(question):
                ids[cid] = True
    return list(ids)


def parse_strict(text: str):
    """JSON with no key written twice and no non-finite number. Raises ValueError."""
    def unique(pairs: list) -> dict:
        out = dict(pairs)
        if len(out) != len(pairs):
            raise ValueError("a key is written twice")
        return out

    def constant(name: str):
        raise ValueError(f"{name} is not a JSON value")

    try:
        return json.loads(text, object_pairs_hook=unique, parse_constant=constant)
    except RecursionError:
        raise ValueError("the text nests too deep") from None


# The other modules of the page, offered under this one name. They import this module's
# constants, so they are imported last.
from slate_rows import (UNQUOTED_COLUMNS, build_record, derive, question_digests,  # noqa: E402,F401
                        quote_rows, quoted_size, record_digest, record_text)
from slate_answers import (EXPORTED_AT_RE, Unfit, check_file, join_files,  # noqa: E402,F401
                           screened_texts)
from slate_handout import orientation, short_sheet  # noqa: E402,F401
from slate_page import SCRIPT_PATH, STYLE_PATH, render, script_hash, script_text  # noqa: E402,F401
