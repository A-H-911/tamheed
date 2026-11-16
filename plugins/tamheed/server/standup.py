"""The standup engine (plan 233, ADR-0003): state, deltas, checkpoint replay, the window, facts.

Pure over a sqlite3 connection: no server globals, the clock and the offset are passed in. The
server's `standup_report` tool (plan 235) does the writes; this module only computes.

The state of a package is one value per entity row, ``status|fingerprint``. A report row keeps
the changes of its window (a delta). A checkpoint row keeps the full state. The state at any
report is a replay from the latest checkpoint, and every link is checked against its digest.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re

DELTA_VERSION = 1
CHECKPOINT_EVERY = 30          # the first report, then every 30th recorded daily report (SR44)
LIST_CAP = 30                  # items frozen per list (SR41); the first report is uncapped
TITLE_CAP = 100
DUE_DAYS = 7
STATE_SKIP = frozenset({"progress_entries", "audit_verdicts", "standup_reports",
                        "trace_edges", "omissions"})
SELF_ACTOR = "system:standup-report"
_PE_RE = "PE-[0-9]*"
_OFFSET_RE = re.compile(r"^([+-])(0\d|1[0-4]):(00|15|30|45)$")
_DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
_HANDOFF_HEAD = re.compile(
    r"^\s*(?:\d+\.\s*)?(?:#+\s*)?\*{0,2}(Resume at|In flight|Awaiting the operator|"
    r"Verified facts|Do not carry)\b[.:]?\*{0,2}[.:]?\s*", re.IGNORECASE)


# ----------------------------------------------------------------------------- the state

def status_of(table: str, row: dict) -> str:
    """The status part of a row's state value."""
    if table == "risks":
        return f"{row.get('risk_state') or ''}|{row.get('lifecycle_status') or ''}"
    if table == "execution_gates":
        return str(row.get("outcome") or "")
    return str(row.get("lifecycle_status") or "")


def fingerprint(row: dict) -> str:
    """12 hex of sha256 over the row's non-null columns, without `last_referenced`.

    A column a release adds is null until written, so it moves no fingerprint."""
    body = {k: v for k, v in row.items() if v is not None and k != "last_referenced"}
    raw = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def state(conn, tables) -> tuple[dict, dict]:
    """(state, columns) of the package: {table: {id: value}} and {table: [column, ...]}."""
    st: dict[str, dict] = {}
    cols: dict[str, list] = {}
    for table in sorted(set(tables) - STATE_SKIP):
        names = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]
        if "id" not in names:
            continue
        cols[table] = names
        rows = conn.execute(f"SELECT {', '.join(names)} FROM {table}").fetchall()
        for raw in rows:
            row = dict(zip(names, raw))
            st.setdefault(table, {})[str(row["id"])] = (
                f"{status_of(table, row)}|{fingerprint(row)}")
    return st, cols


def digest(st: dict) -> str:
    raw = json.dumps(st, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def diff(base: dict, base_cols: dict, live: dict, live_cols: dict) -> dict:
    """The delta that turns (base, base_cols) into (live, live_cols)."""
    sets, drops = {}, {}
    for table in sorted(set(base) | set(live)):
        b, lv = base.get(table, {}), live.get(table, {})
        changed = {i: v for i, v in lv.items() if b.get(i) != v}
        gone = sorted(i for i in b if i not in lv)
        if changed:
            sets[table] = changed
        if gone:
            drops[table] = gone
    columns = {t: c for t, c in live_cols.items() if base_cols.get(t) != c}
    return {"v": DELTA_VERSION, "columns": columns, "set": sets, "drop": drops}


def full(live: dict, live_cols: dict) -> dict:
    """A checkpoint: the whole state, applied over nothing."""
    return {"v": DELTA_VERSION, "checkpoint": True, "columns": dict(live_cols),
            "set": {t: dict(m) for t, m in live.items()}, "drop": {}}


def apply(base: dict, base_cols: dict, delta: dict) -> tuple[dict, dict]:
    """Apply a delta. A checkpoint replaces everything. Returns new copies."""
    if delta.get("v") != DELTA_VERSION:
        raise ValueError(f"delta format v{delta.get('v')} is unknown to this engine")
    if delta.get("checkpoint"):
        st, cols = {}, {}
    else:
        st = {t: dict(m) for t, m in base.items()}
        cols = dict(base_cols)
    cols.update(delta.get("columns", {}))
    for table, values in delta.get("set", {}).items():
        st.setdefault(table, {}).update(values)
    for table, gone in delta.get("drop", {}).items():
        for i in gone:
            st.get(table, {}).pop(i, None)
    return {t: m for t, m in st.items() if m}, cols


# ----------------------------------------------------------------------------- the chain

def chain(conn, upto: int | None = None) -> list[dict]:
    """Recorded daily reports from the latest checkpoint at or before place `upto`, by `seq`."""
    sql = ("SELECT id, checkpoint, seq, state_delta, state_digest FROM standup_reports"
           " WHERE kind = 'default' AND lifecycle_status = 'Approved'")
    params: list = []
    if upto is not None:
        sql += " AND seq <= ?"
        params.append(upto)
    rows = [dict(zip(("id", "checkpoint", "seq", "delta", "digest"), r))
            for r in conn.execute(sql + " ORDER BY seq", params)]
    starts = [k for k, r in enumerate(rows) if r["checkpoint"]]
    return rows[starts[-1]:] if starts else []


def replay(links: list[dict]) -> tuple[dict, dict, str | None]:
    """(state, columns, first bad id). Each link is checked against its own digest."""
    st: dict = {}
    cols: dict = {}
    for link in links:
        try:
            st, cols = apply(st, cols, json.loads(link["delta"]))
        except (ValueError, TypeError):
            return st, cols, link["id"]
        if digest(st) != link["digest"]:
            return st, cols, link["id"]
    return st, cols, None


def is_checkpoint_due(seq: int, broken: bool) -> bool:
    """The first report, every 30th daily report, and the report after a broken link."""
    return seq == 1 or broken or seq % CHECKPOINT_EVERY == 0


# ----------------------------------------------------------------------------- moves

def classify(base: dict, base_cols: dict, live: dict, live_cols: dict) -> dict:
    """What changed: moved (status), edited (same status, other content), new, dropped.

    A table the base never tracked is `first_counted`: counted, never listed as new. A
    table whose column list changed has its edits paused for this one report."""
    out = {"moved": [], "edited": [], "new": [], "dropped": [],
           "first_counted": sorted(t for t in live_cols if t not in base_cols),
           "paused": sorted(t for t in live_cols
                            if t in base_cols and base_cols[t] != live_cols[t])}
    for table in sorted(live):
        if table in out["first_counted"]:
            continue
        b = base.get(table, {})
        for i, value in live[table].items():
            now_status, _, now_fp = value.rpartition("|")
            if i not in b:
                out["new"].append((table, i, now_status))
                continue
            was_status, _, was_fp = b[i].rpartition("|")
            if was_status != now_status:
                out["moved"].append((table, i, was_status, now_status))
            elif was_fp != now_fp and table not in out["paused"]:
                out["edited"].append((table, i))
    for table in sorted(base):
        out["dropped"].extend((table, i) for i in base[table] if i not in live.get(table, {}))
    return out


# ----------------------------------------------------------------------------- the window

def pe_max(conn) -> int:
    return conn.execute("SELECT COALESCE(MAX(CAST(SUBSTR(id, 4) AS INTEGER)), 0) FROM"
                        " progress_entries WHERE id GLOB ?", (_PE_RE,)).fetchone()[0]


def av_max(conn) -> int:
    return conn.execute("SELECT COALESCE(MAX(CAST(SUBSTR(id, 4) AS INTEGER)), 0) FROM"
                        " audit_verdicts WHERE id GLOB 'AV-[0-9]*'").fetchone()[0]


def parse_offset(text: str) -> _dt.timedelta | None:
    """'+03:00' -> timedelta. None when the text is not ±HH:MM in -12:00..+14:00."""
    m = _OFFSET_RE.match(str(text or ""))
    if not m:
        return None
    minutes = int(m.group(2)) * 60 + int(m.group(3))
    if (m.group(1) == "-" and minutes > 12 * 60) or minutes > 14 * 60:
        return None
    return _dt.timedelta(minutes=-minutes if m.group(1) == "-" else minutes)


def normal_offset(text: str) -> str:
    return "+00:00" if text == "-00:00" else text


def local(utc_text: str, offset: str) -> _dt.datetime:
    """A stored UTC time in the row's own offset. strptime: Python 3.10 refuses a 'Z'."""
    when = _dt.datetime.strptime(utc_text, "%Y-%m-%dT%H:%M:%SZ")
    return when + (parse_offset(offset) or _dt.timedelta())


def shown(utc_text: str, offset: str) -> str:
    """'Mon 16 Nov 2026, 09:05 (UTC+03:00)', with fixed English names (no locale)."""
    t = local(utc_text, offset)
    return (f"{_DAYS[t.weekday()]} {t.day} {_MONTHS[t.month - 1]} {t.year},"
            f" {t.hour:02d}:{t.minute:02d} (UTC{offset})")


def daily_reports(conn) -> list[dict]:
    keys = ("id", "seq", "pe_to", "av_to", "ended_at", "utc_offset", "base_report")
    return [dict(zip(keys, r)) for r in conn.execute(
        f"SELECT {', '.join(keys)} FROM standup_reports WHERE kind = 'default'"
        " AND lifecycle_status = 'Approved' ORDER BY seq")]


def at_place(conn, report_id: str | None) -> dict | None:
    """The recorded daily report at the place of `report_id` in the chain. A correction takes
    the place of the report it corrects, so a base id stays valid after its correction."""
    if not report_id:
        return None
    seq = conn.execute("SELECT seq FROM standup_reports WHERE id = ?", (report_id,)).fetchone()
    if not seq or seq[0] is None:
        return None
    return next((r for r in daily_reports(conn) if r["seq"] == seq[0]), None)


def snap(conn, day: str) -> tuple[dict | None, str | None]:
    """The last recorded daily report whose local end date is on or before `day`."""
    try:
        target = _dt.date.fromisoformat(day)
    except ValueError:
        return None, "start is a date (YYYY-MM-DD) or a recorded report id (RPT-NNN)"
    best = None
    for row in daily_reports(conn):
        if local(row["ended_at"], row["utc_offset"]).date() <= target:
            best = row
    return best, None


# ----------------------------------------------------------------------------- the journal

def window_entries(conn, pe_from: int, pe_to: int) -> list[dict]:
    keys = ("id", "event_type", "entry", "subject_id", "actor", "custom_attributes")
    return [dict(zip(keys, r)) for r in conn.execute(
        f"SELECT {', '.join(keys)} FROM progress_entries WHERE id GLOB ? AND"
        " CAST(SUBSTR(id, 4) AS INTEGER) BETWEEN ? AND ? AND COALESCE(actor, '') <> ?"
        " ORDER BY CAST(SUBSTR(id, 4) AS INTEGER), id",
        (_PE_RE, pe_from, pe_to, SELF_ACTOR))]


def window_verdicts(conn, av_from: int, av_to: int) -> list[dict]:
    """The latest verdict per acceptance check inside the window."""
    rows = conn.execute(
        "SELECT id, ac_id, verdict FROM audit_verdicts WHERE id GLOB 'AV-[0-9]*' AND"
        " CAST(SUBSTR(id, 4) AS INTEGER) BETWEEN ? AND ?"
        " ORDER BY CAST(SUBSTR(id, 4) AS INTEGER)", (av_from, av_to)).fetchall()
    latest: dict[str, dict] = {}
    for vid, ac, verdict in rows:
        latest[str(ac)] = {"id": vid, "ac_id": ac, "verdict": verdict}
    return list(latest.values())


def handoff_sections(conn) -> dict[str, list[str]]:
    """The latest handoff entry, split by its five headings (missing ones are absent)."""
    row = conn.execute(
        "SELECT entry FROM progress_entries WHERE event_type = 'handoff' AND id GLOB ?"
        " ORDER BY CAST(SUBSTR(id, 4) AS INTEGER) DESC LIMIT 1", (_PE_RE,)).fetchone()
    out: dict[str, list[str]] = {}
    current = None
    for line in str(row[0] if row else "").splitlines():
        head = _HANDOFF_HEAD.match(line)
        if head:
            current = head.group(1).lower()
            rest = line[head.end():].strip()
            out[current] = [rest] if rest else []
        elif current and line.strip():
            out[current].append(line.strip())
    return out


def first_sentence(text: str, words: int = 25) -> str:
    one = re.split(r"(?<=[.!?])\s", " ".join(str(text or "").split()), maxsplit=1)[0]
    parts = one.split()
    return " ".join(parts[:words]) + (" …" if len(parts) > words else "")


# ----------------------------------------------------------------------------- orchestration

def select_base(conn, start: str | None) -> tuple[dict | None, str, str | None, str | None]:
    """(base row or None for birth, kind, snapped-from note, error).

    No start: the latest recorded daily report. A report id: that recorded daily report. A
    date: the last recorded daily report on or before it. Kind is `default` only when the
    base is the latest daily report."""
    daily = daily_reports(conn)
    latest = daily[-1] if daily else None
    if start is None:
        return latest, "default", None, None
    start = str(start).strip()
    if re.fullmatch(r"RPT-\d+", start):
        row = at_place(conn, start)
        if row is None:
            state_of = conn.execute("SELECT kind, lifecycle_status FROM standup_reports"
                                    " WHERE id = ?", (start,)).fetchone()
            why = ("not a row" if state_of is None else
                   f"{'an override' if state_of[0] == 'override' else state_of[1].lower()}")
            return None, "", None, (f"{start} cannot start a window: it is {why}. Start from"
                                    " a recorded daily report")
        base, note = row, None
    else:
        base, err = snap(conn, start)
        if err:
            return None, "", None, err
        note = start
    same = (base or {}).get("id") == (latest or {}).get("id")
    return base, ("default" if same else "override"), note, None


def compute(conn, tables, base: dict | None, kind: str) -> dict:
    """The draft's window, state, delta and classification. Raises nothing: an `error`
    key names a journal that runs backwards."""
    links = chain(conn, upto=base["seq"]) if base else []
    base_state, base_cols, broken = replay(links) if base else ({}, {}, None)
    if base and not links:
        broken = base["id"]             # a chain with no checkpoint cannot be replayed
    live, live_cols = state(conn, tables)
    pe_to, av_to = pe_max(conn), av_max(conn)
    if base and pe_to < base["pe_to"]:
        return {"error": (f"the journal ends at PE-{pe_to}, before {base['id']}'s end"
                          f" PE-{base['pe_to']}. data/ moved backwards. Reconcile it, then"
                          " draft again")}
    seq = ((base or {}).get("seq") or 0) + 1 if kind == "default" else None
    checkpoint = seq is not None and is_checkpoint_due(seq, broken is not None)
    # A broken link leaves no trusted base: the delta is then the full state, for an
    # override too. verify() applies a full delta over nothing, so both sides agree.
    delta = (full(live, live_cols) if checkpoint or broken else
             diff(base_state, base_cols, live, live_cols))
    check, _cols = apply(base_state, base_cols, delta)
    if digest(check) != digest(live):  # pragma: no cover - diff and apply are inverses
        raise AssertionError("the delta does not rebuild the live state")
    cls = (classify({}, {}, {}, {}) if broken else
           classify(base_state, base_cols, live, live_cols))
    return {"pe_from": (base["pe_to"] + 1) if base else 1, "pe_to": pe_to,
            "av_from": (base["av_to"] + 1) if base else 1, "av_to": av_to,
            "seq": seq, "live": live, "live_cols": live_cols, "checkpoint": checkpoint,
            "delta": delta, "digest": digest(live), "cls": cls, "broken": broken,
            "first": base is None}


def verify(conn, row: dict) -> tuple[bool, str | None]:
    """At record: the replay to the row's base plus the row's delta gives its digest.

    A full delta (a checkpoint, or a draft over a broken link) needs no base."""
    try:
        delta = json.loads(row["state_delta"])
        whole = bool(delta.get("checkpoint"))
    except (ValueError, TypeError, AttributeError) as exc:
        return False, f"the draft's delta does not read: {exc}"
    base_state, base_cols = {}, {}
    if row.get("base_report") and not whole:
        base = at_place(conn, row["base_report"])
        if base is None:
            return False, f"{row['base_report']} is no longer a recorded daily report"
        base_state, base_cols, broken = replay(chain(conn, upto=base["seq"]))
        if broken:
            return False, f"the stored reports no longer replay at {broken}"
    try:
        st, _cols = apply(base_state, base_cols, delta)
    except (ValueError, TypeError) as exc:
        return False, f"the draft's delta does not read: {exc}"
    if digest(st) != row["state_digest"]:
        return False, "the stored reports no longer replay to the state this draft saw"
    return True, None
