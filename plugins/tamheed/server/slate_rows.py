"""What a slate takes from the store (plans 227 and 227c): the rows that its page quotes, and
what the export derives from them. Import `slate` first: this module reads its constants.

Derived at export, and kept in the record beside the slate:
- `names`: the title of each participant that is a row (R108).
- `terms`: the glossary rows that a question's text uses (R110). The match runs here, on the
  server, so no matching script runs in the browser.
- `named`: the rows that a text names by id and that the question does not already show (R113).
"""
from __future__ import annotations

import hashlib
import json
import re

from slate import MAX_TERMS, Refused, cited_ids, questions_of, shown_ids
from tamheed_server import ENTITY_TABLES

# `last_referenced` is stamped by work_bind: a bind is no change to what a row says
UNQUOTED_COLUMNS = frozenset({"id", "last_referenced"})
TITLE_COLUMNS = ("title", "heading", "term", "name")
# an id as the store writes one, standing alone in a text
ID_IN_TEXT = re.compile(r"(?<![A-Za-z0-9_-])[A-Z]{2,5}-\d{1,6}(?![A-Za-z0-9_-])")
MAX_NAMED = 30                        # the ids that one text may name on the page


def _canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def quote_rows(conn, ids: list[str]) -> tuple[dict, list[str]]:
    """({id: {type, columns, digest}}, the ids that name no row). A quote is the row as the
    store holds it: every column that has a value, in column order, except the id itself
    and `last_referenced`. `custom_attributes` is in, so a register entry shows its fields.
    The digest is of that same set, so it moves only when what the row says moves."""
    quotes, missing = {}, []
    for rid in ids:
        found = conn.execute("SELECT entity_type FROM entity_index WHERE id = ?",
                             (rid,)).fetchone()
        table = ENTITY_TABLES.get(found[0]) if found else None
        if table is None:
            missing.append(rid)
            continue
        names = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]
        row = conn.execute(f"SELECT {', '.join(names)} FROM {table} WHERE id = ?",
                           (rid,)).fetchone()
        columns = [[name, value] for name, value in zip(names, row)
                   if name not in UNQUOTED_COLUMNS and value not in (None, "")]
        quote = {"type": found[0], "columns": columns}
        quotes[rid] = quote | {"digest": _sha(_canonical(quote))}
    return quotes, missing


def title_of(quote: dict) -> str:
    columns = dict(quote["columns"])
    return next((str(columns[c]) for c in TITLE_COLUMNS if columns.get(c)), "")


def _texts(question: dict) -> list[str]:
    """Every text of a question that a reader sees."""
    return ([question["question"], question["detail"], question["reason"], question["gap"]]
            + [text for o in question["options"] for text in (o["label"], o["detail"])])


def _term_pattern(quote: dict):
    """The words of one glossary row: its term, and `variants` in its attributes when that
    is a list of text. A word may take a final s. It stands alone, in any letter case."""
    columns = dict(quote["columns"])
    words = [columns.get("term") or ""]
    try:
        attributes = json.loads(columns.get("custom_attributes") or "{}")
    except (ValueError, RecursionError):
        attributes = {}
    variants = attributes.get("variants") if isinstance(attributes, dict) else None
    if isinstance(variants, list):
        words += [v for v in variants if isinstance(v, str)]
    words = [w.strip() for w in words if isinstance(w, str) and w.strip()]
    if not words:
        return None
    return re.compile(r"(?<!\w)(?:" + "|".join(re.escape(w) for w in words) + r")s?(?!\w)",
                      re.IGNORECASE)


def _terms(conn, slate: dict) -> tuple[dict, dict]:
    """({question id: [glossary ids]}, the quotes of the glossary rows that matched)."""
    if slate["terms"] is None:
        ids = [r[0] for r in conn.execute("SELECT id FROM glossary_terms ORDER BY id")]
        if len(ids) > MAX_TERMS:               # the match is bounded, like a named list
            raise Refused(f"the package holds {len(ids)} glossary rows (the cap of one page"
                          f" is {MAX_TERMS}). Name the rows to match under `terms`")
    else:
        ids = slate["terms"]
    quotes, missing = quote_rows(conn, ids)
    if missing:
        raise Refused("the slate cites id(s) that name no row: " + ", ".join(missing[:10]))
    if other := [rid for rid, quote in quotes.items() if quote["type"] != "glossary-term"]:
        raise Refused(f"the slate's `terms` names {other[0]!r}, which is no glossary row")
    patterns = {rid: _term_pattern(quote) for rid, quote in quotes.items()}
    matched: dict = {}
    for question in questions_of(slate):
        text = "\n".join(_texts(question))
        if hit := [rid for rid, pattern in patterns.items() if pattern and pattern.search(text)]:
            matched[question["id"]] = hit
    used = {rid for hit in matched.values() for rid in hit}
    return matched, {rid: quote for rid, quote in quotes.items() if rid in used}


def _named(conn, slate: dict) -> dict:
    """{question or decided-topic id: [row ids]}: the ids that a text names and that exist,
    less the rows that the item already shows by a key."""
    out: dict = {}
    items = [(q["id"], _texts(q), shown_ids(q)) for q in questions_of(slate)]
    items += [(t["id"], [t["title"], t["answer"]], t["cites"])
              for rnd in slate["rounds"] for t in rnd["decided"]]
    known: dict = {}
    for ident, texts, shown in items:
        found = []
        for token in dict.fromkeys(ID_IN_TEXT.findall("\n".join(texts))):
            if token in shown:
                continue
            if token not in known:
                known[token] = conn.execute("SELECT 1 FROM entity_index WHERE id = ?",
                                            (token,)).fetchone() is not None
            if known[token]:
                found.append(token)
        if found:
            out[ident] = found[:MAX_NAMED]
    return out


def derive(conn, slate: dict) -> tuple[dict | None, dict, str | None]:
    """(what the export derives, the quotes of every row that the page shows, None), or
    (None, {}, why the slate is refused). Nothing is written."""
    quotes, missing = quote_rows(conn, cited_ids(slate))
    if missing:
        return None, {}, ("the slate cites id(s) that name no row: " + ", ".join(missing[:10])
                          + (f" (+{len(missing) - 10} more)" if len(missing) > 10 else ""))
    try:
        terms, term_quotes = _terms(conn, slate)
    except Refused as exc:
        return None, {}, str(exc)
    quotes.update(term_quotes)
    names = {}
    for person in slate["participants"]:
        if person["name"]:
            continue
        found, _ = quote_rows(conn, [person["id"]])
        name = title_of(found[person["id"]]) if found else ""
        if not name:
            return None, {}, (f"participant {person['id']!r} has no `name` and names no row"
                              " that has a title. Give it a `name`, or use a row's id")
        names[person["id"]] = name
        quotes.update(found)
    named = _named(conn, slate)
    more, _ = quote_rows(conn, [rid for ids in named.values() for rid in ids
                                if rid not in quotes])
    quotes.update(more)
    return {"names": names, "terms": terms, "named": named}, quotes, None


def derived_ids(derived: dict) -> set:
    """Every row id that the derived part of a record names."""
    return (set(derived["names"]) | {rid for ids in derived["terms"].values() for rid in ids}
            | {rid for ids in derived["named"].values() for rid in ids})


def derived_error(slate: dict, derived, rows: dict) -> str | None:
    """Why the derived part of a record on disk is not one that the export wrote, or None."""
    if not isinstance(derived, dict) or set(derived) != {"names", "terms", "named"}:
        return "its derived part is missing or has other keys"
    if not all(isinstance(derived[k], dict) for k in derived):
        return "its derived part is not three objects"
    if not all(isinstance(v, str) and v for v in derived["names"].values()):
        return "a derived name is not text"
    for key in ("terms", "named"):
        for ids in derived[key].values():
            if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
                return f"a derived list of `{key}` is not a list of ids"
    unnamed = {p["id"] for p in slate["participants"] if not p["name"]}
    if set(derived["names"]) != unnamed:
        return "its derived names are not those of the slate's participants"
    if set(rows) != set(cited_ids(slate)) | derived_ids(derived):
        return "it does not quote exactly the rows that its slate shows"
    for quote in rows.values():              # a quote as `quote_rows` writes one
        columns, digest = quote.get("columns"), quote.get("digest")
        if not isinstance(quote.get("type"), str) or not isinstance(columns, list) \
                or not all(isinstance(c, list) and len(c) == 2 and isinstance(c[0], str)
                           for c in columns) \
                or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            return "a quoted row is not as this tool writes one"
    return None


def name_of(record: dict, pid: str) -> str:
    """The name of a participant as the page shows it."""
    for person in record["slate"]["participants"]:
        if person["id"] == pid:
            return person["name"] or record["derived"]["names"].get(pid, pid)
    return pid


def quoted_size(record: dict) -> int:
    """The characters of quoted text that the page will hold. A row is printed once per
    citation, so one large row cited by many questions makes a very large page."""
    quotes, derived = record["rows"], record["derived"]
    size = {rid: sum(len(str(name)) + len(str(value)) for name, value in quote["columns"])
            for rid, quote in quotes.items()}
    total = 0
    for rnd in record["slate"]["rounds"]:
        ids = rnd["cites"] + [c for t in rnd["decided"] for c in t["cites"]]
        for question in rnd["questions"]:
            ids = ids + shown_ids(question) + derived["terms"].get(question["id"], [])
        total += sum(size[rid] for rid in ids)
    return total


def build_record(slate: dict, quotes: dict, derived: dict) -> dict:
    from slate import RECORD_FORMAT, VERSION
    return {"format": RECORD_FORMAT, "version": VERSION, "slate": slate, "derived": derived,
            "rows": quotes}


def record_text(record: dict) -> str:
    """The slate file's bytes: sorted keys, one space of indent, a final newline."""
    return json.dumps(record, ensure_ascii=False, sort_keys=True, indent=1) + "\n"


def record_digest(record: dict) -> str:
    """The slate's name for one exact content. Computed from the content at every use, and
    never read from a stored field: a field can be edited, and this cannot."""
    return _sha(_canonical({k: record.get(k)
                            for k in ("format", "version", "slate", "derived", "rows")}))


def question_digests(record: dict) -> dict:
    """{question id: digest}. R111: a question's digest covers its own keys, its round's
    cited rows, every row that it shows, and the names of the people that it names. An
    answer keeps the digest of the question that it answered."""
    rows, derived = record["rows"], record["derived"]
    out = {}
    for rnd in record["slate"]["rounds"]:
        for question in rnd["questions"]:
            qid = question["id"]
            ids = (rnd["cites"] + shown_ids(question) + derived["terms"].get(qid, [])
                   + derived["named"].get(qid, []))
            people = ([question["lead"]] if question["lead"] else []) + question["consulted"]
            out[qid] = _sha(_canonical({
                "question": question,
                "rows": {rid: rows[rid]["digest"] for rid in dict.fromkeys(ids)},
                "names": {pid: name_of(record, pid) for pid in people}}))
    return out
