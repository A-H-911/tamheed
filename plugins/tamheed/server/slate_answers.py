"""The reader of an interview page's answers (plans 227 and 227c). Import `slate` first.

The page saves one file for the whole page, and one file per round (R105). The reader takes
every file of a slate, checks each against the slate's record, and joins them. It reads and
judges. It decides nothing, and it writes nothing.

What it never does: pick between two files that disagree, take an approval from a file, or
accept a key that the slate did not declare.
"""
from __future__ import annotations

import re

from slate import (ANSWERS_FORMAT, EVIDENCE, ID_RE, MAX_ANSWER_TEXT, MAX_POINTS, OTHER,
                   UNKNOWN, VERSION, encodable, short)
from slate_rows import name_of, question_digests, shown_ids

EXPORTED_AT_RE = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d{1,9})?Z", re.ASCII)
MAX_DROPPED = 50                      # the entries of `dropped` that one read lists
OPERATOR = "operator"                 # the value of `answered_by` and `by` for the operator
STATES = ("present", "covered")
FIXED_LABELS = {UNKNOWN: "Unknown", EVIDENCE: "Requires evidence"}


class Unfit(ValueError):
    """Why one answers file does not fit its slate."""


def _text(owner: str, obj: dict, key: str) -> str:
    value = obj.get(key, "")
    if value is None:
        return ""
    if not isinstance(value, str) or not encodable(value):
        raise Unfit(f"{owner}: `{key}` is text")
    if len(value) > MAX_ANSWER_TEXT:
        raise Unfit(f"{owner}: `{key}` holds {len(value)} characters (the cap is"
                    f" {MAX_ANSWER_TEXT})")
    return value


def legal_selections(question: dict) -> set:
    """The values that an answer to this question may select."""
    legal = {o["id"] for o in question["options"]}
    if question["allow_other"]:
        legal.add(OTHER)
    if question["allow_unsure"]:
        legal |= {UNKNOWN, EVIDENCE}
    return legal


def _person(owner: str, obj: dict, key: str, people: set) -> str:
    value = obj.get(key) or ""
    if not isinstance(value, str) or (value and value != OPERATOR and value not in people):
        raise Unfit(f"{owner}: `{key}` names {short(value)}, who is no participant of the slate")
    return value


def _check_answer(question: dict, got: dict, people: set) -> dict:
    owner = f"question {question['id']}"
    selected = got.get("selected")
    legal = legal_selections(question)
    if selected is not None and (not isinstance(selected, str) or selected not in legal):
        raise Unfit(f"{owner}: the file selects {short(selected)}, which is none of its options"
                    f" ({', '.join(sorted(legal))})")
    digest = got.get("question_digest")
    return {"selected": selected, "other": _text(owner, got, "other"),
            "note": _text(owner, got, "note"),
            "answered_by": _person(owner, got, "answered_by", people),
            "question_digest": digest if isinstance(digest, str) else None}


def _check_round(rnd: dict, got: dict, slate: dict) -> dict:
    """One round's part of a file, with nothing that the slate did not declare."""
    owner = f"round {rnd['id']}"
    people = {p["id"] for p in slate["participants"]}
    attending = {p["id"] for p in slate["participants"] if p["attends"]}
    kinds = {k["id"] for k in slate["point_kinds"]}
    fields = {f["id"] for f in slate["closure_fields"]}
    out = {key: _text(owner, got, key) for key in ("guests", "reopen", "closed_by")}
    out["closed"] = got.get("closed") is True
    attendance = got.get("attendance") or {}
    if not isinstance(attendance, dict):
        raise Unfit(f"{owner}: `attendance` is an object")
    out["attendance"] = {}
    for pid, item in attendance.items():
        if pid not in attending:
            raise Unfit(f"{owner}: `attendance` names {short(pid)}, who does not attend")
        state = item.get("state") if isinstance(item, dict) else None
        if not isinstance(state, str) or state not in STATES:
            raise Unfit(f"{owner}, attendance of {pid}: `state` is one of: {', '.join(STATES)}")
        out["attendance"][pid] = {"state": item["state"],
                                  "covered_by": _text(owner, item, "covered_by")}
    closure = got.get("closure") or {}
    if not isinstance(closure, dict):
        raise Unfit(f"{owner}: `closure` is an object")
    if extra := sorted(str(k) for k in set(closure) - fields):
        raise Unfit(f"{owner}: the slate did not declare the closure field {short(extra[0])}")
    out["closure"] = {key: _text(owner, closure, key) for key in closure}
    points = got.get("points") or []
    if not isinstance(points, list) or not all(isinstance(p, dict) for p in points):
        raise Unfit(f"{owner}: `points` is a list of objects")
    if len(points) > MAX_POINTS:
        raise Unfit(f"{owner} holds {len(points)} points (the cap is {MAX_POINTS})")
    out["points"] = []
    for n, point in enumerate(points):
        where = f"{owner}, point {n + 1}"
        if not isinstance(point.get("kind"), str) or point["kind"] not in kinds:
            raise Unfit(f"{where}: the slate did not declare the point kind"
                        f" {short(point.get('kind'))}")
        out["points"].append({"kind": point["kind"], "by": _person(where, point, "by", people),
                              "text": _text(where, point, "text")})
    return out


def check_file(record: dict, name: str, round_id: str | None, answers) -> dict:
    """One answers file against the record: {"file", "round", "rounds", "answers", "dropped",
    "exported_at", "slate_digest"}. Raises Unfit. `round_id` is the round that the file's
    name stands for, or None for the file of the whole page."""
    slate = record["slate"]
    if not isinstance(answers, dict):
        raise Unfit("the file is not a JSON object")
    head = (answers.get("format"), answers.get("version"), answers.get("slate"))
    if head != (ANSWERS_FORMAT, VERSION, slate["name"]):
        raise Unfit("the file's head reads (" + ", ".join(short(h) for h in head)
                    + f"). This slate's answers file starts with"
                      f" {(ANSWERS_FORMAT, VERSION, slate['name'])!r}")
    if round_id is None and answers.get("round") is not None:
        raise Unfit(f"it is one round's file (the round {short(answers.get('round'))}). Its"
                    f" name is {slate['name']}.<round id>.answers.json")
    if round_id is not None and answers.get("round") != round_id:
        raise Unfit(f"it names the round {short(answers.get('round'))}, and its file name"
                    f" stands for the round {round_id!r}")
    rounds = {r["id"]: r for r in slate["rounds"] if r["ready"]
              and (round_id is None or r["id"] == round_id)}
    questions = {q["id"]: q for r in rounds.values() for q in r["questions"]}
    people = {p["id"] for p in slate["participants"]}
    out = {"file": name, "round": round_id, "rounds": {}, "answers": {}, "dropped": []}
    for kind, key, into in (("answers", "question", out["answers"]),
                            ("rounds", "id", out["rounds"])):
        items = answers.get(kind)
        if not isinstance(items, list) or not all(isinstance(i, dict) for i in items):
            raise Unfit(f"the file's `{kind}` is a list of objects")
        seen = set()
        for item in items:
            ident = item.get(key)
            if not isinstance(ident, str) or ident in seen:
                raise Unfit(f"the file names the {kind[:-1]} {short(ident)} twice, or without"
                            " an id")
            seen.add(ident)
            if kind == "answers" and ident in questions:
                into[ident] = _check_answer(questions[ident], item, people)
            elif kind == "rounds" and ident in rounds:
                into[ident] = _check_round(rounds[ident], item, slate)
            else:                              # R111: the slate no longer has it
                # an id that the slate could never hold is echoed as a short, quoted text
                shown = ident if ID_RE.fullmatch(ident) else short(ident)
                out["dropped"].append({"file": name,
                                       key if kind == "answers" else "round": shown})
    stamp = answers.get("exported_at")           # a time in one fixed form, or nothing
    out["exported_at"] = (stamp if isinstance(stamp, str) and EXPORTED_AT_RE.fullmatch(stamp)
                          else None)
    out["slate_digest"] = answers.get("slate_digest")
    return out


def _empty_answer(answer: dict) -> bool:
    return answer["selected"] is None and not (answer["other"].strip() or answer["note"].strip()
                                               or answer["answered_by"])


def _empty_round(data: dict) -> bool:
    return not (data["attendance"] or data["points"] or data["closed"]
                or any(v.strip() for v in data["closure"].values())
                or any(data[k].strip() for k in ("guests", "reopen", "closed_by")))


def _split(covering: list, part: str, ident: str, empty) -> tuple[list, list]:
    """(the files' values that hold something, the files that leave this one empty)."""
    held = [(f["file"], f[part][ident]) for f in covering if ident in f[part]]
    return ([c for c in held if not empty(c[1])], [name for name, v in held if empty(v)])


def _one(candidates: list, same_keys: tuple | None):
    """(the one value that the files agree on or None, the files that disagree)."""
    if not candidates:
        return None, []
    first = candidates[0][1]
    for name, value in candidates[1:]:
        left, right = ((first, value) if same_keys is None else
                       ({k: first[k] for k in same_keys}, {k: value[k] for k in same_keys}))
        if left != right:
            return None, [name for name, _ in candidates]
    return first, []


def _missing(rnd: dict, data: dict, record: dict) -> list:
    """R106: what a round still misses: a person, a named cover, a closure field."""
    out = []
    for person in record["slate"]["participants"]:
        if not person["attends"]:
            continue
        got, name = data["attendance"].get(person["id"]), name_of(record, person["id"])
        if got is None:
            out.append(f"attendance: {name} is not recorded")
        elif got["state"] == "covered" and not got["covered_by"].strip():
            out.append(f"attendance: {name} is covered, and nobody is named")
    out.extend(f"closure: {f['id']} is empty" for f in record["slate"]["closure_fields"]
               if not data["closure"].get(f["id"], "").strip())
    return out


def join_files(record: dict, digest: str, files: list, changed: dict,
               only: str | None = None) -> dict:
    """A checked transcript of every file of one slate. `files` are the answers of
    `check_file`. `changed` maps a quoted row id to what happened to it since the page was
    made. `only` limits the transcript to one round."""
    slate, digests = record["slate"], question_digests(record)
    derived = record["derived"]
    dropped = [d for f in files for d in f["dropped"]]
    out = {"rounds": [], "answers": [], "unanswered": [], "conflicts": [], "put_again": [],
           "question_changed": [], "approval_needed": [], "rounds_without_file": [],
           "one_file_only": [], "dropped": dropped[:MAX_DROPPED],
           "dropped_more": max(0, len(dropped) - MAX_DROPPED),
           "files": [{"file": f["file"], "round": f["round"], "exported_at": f["exported_at"],
                      "same_export": f["slate_digest"] == digest} for f in files]}
    for rnd in slate["rounds"]:
        if not rnd["ready"] or (only is not None and rnd["id"] != only):
            continue
        covering = [f for f in files if f["round"] in (None, rnd["id"])]
        candidates, blank = _split(covering, "rounds", rnd["id"], _empty_round)
        data, clash = _one(candidates, None)
        if clash:
            out["conflicts"].append({"round": rnd["id"], "files": clash})
        if candidates and blank:
            out["one_file_only"].append({"round": rnd["id"], "empty_in": blank,
                                         "answered_in": [name for name, _ in candidates]})
        info = {"id": rnd["id"], "title": rnd["title"], "files": [f["file"] for f in covering]}
        if not covering:
            out["rounds_without_file"].append(rnd["id"])
        if data is None:
            info |= {"complete": False, "missing": ["no file holds this round's attendance"
                                                    " and closure"] if not clash else
                     ["two files disagree on this round"]}
        else:
            info |= {"guests": data["guests"], "reopen": data["reopen"],
                     "closed": data["closed"], "closed_by": data["closed_by"],
                     "closure": data["closure"],
                     "attendance": [{"id": pid, "name": name_of(record, pid), **got}
                                    for pid, got in data["attendance"].items()],
                     "points": [{**p, "by_name": name_of(record, p["by"]) if p["by"] else ""}
                                for p in data["points"] if p["text"].strip()]}
            info["missing"] = _missing(rnd, data, record)
            info["complete"] = not info["missing"]
        out["rounds"].append(info)
        for question in rnd["questions"]:
            qid = question["id"]
            candidates, blank = _split(covering, "answers", qid, _empty_answer)
            got, clash = _one(candidates, ("selected", "other", "note", "answered_by"))
            if clash:
                out["conflicts"].append({"question": qid, "files": clash})
            if candidates and blank:
                out["one_file_only"].append({"question": qid, "empty_in": blank,
                                             "answered_in": [name for name, _ in candidates]})
            # files that agree on an answer and name two versions of its question: changed
            versions = {value["question_digest"] for _, value in candidates}
            got = got or {"selected": None, "other": "", "note": "", "answered_by": "",
                          "question_digest": None}
            labels = {o["id"]: o["label"] for o in question["options"]} | FIXED_LABELS
            selected, other = got["selected"], got["other"]
            answered = selected is not None and not (selected == OTHER and not other.strip())
            shown = (rnd["cites"] + shown_ids(question) + derived["terms"].get(qid, [])
                     + derived["named"].get(qid, []))
            moved = [rid for rid in dict.fromkeys(shown) if rid in changed]
            stale = answered and (got["question_digest"] != digests[qid] or len(versions) > 1)
            out["answers"].append({
                "question": qid, "round": rnd["id"], "text": question["question"],
                "owner": question["owner"], "selected": selected,
                "selected_label": (None if selected is None else other if selected == OTHER
                                   else labels[selected]),
                "recommended": question["recommended"],
                "equals_recommendation": (selected == question["recommended"]
                                          if answered and question["recommended"] is not None
                                          else None),
                # the free text is returned whatever is selected: text that was typed and
                # left unselected is still on the page, and it is screened
                "other": other, "note": got["note"], "answered_by": got["answered_by"],
                "answered_by_name": (name_of(record, got["answered_by"])
                                     if got["answered_by"] not in ("", OPERATOR)
                                     else got["answered_by"]),
                "settles": question["settles"], "approval": question["approval"],
                "cites": question["cites"], "changed_rows": moved, "question_changed": stale})
            if not answered:
                out["unanswered"].append(qid)
            if stale:
                out["question_changed"].append(qid)
            if answered and (stale or moved):
                out["put_again"].append(qid)
            if answered and question["approval"]:
                out["approval_needed"].append(qid)
    return out


def screened_texts(transcript: dict):
    """(where, field, text) for every free text of a transcript."""
    for rnd in transcript["rounds"]:
        where = f"round {rnd['id']}"
        for key in ("guests", "reopen", "closed_by"):
            yield where, key, rnd.get(key, "")
        for key, text in rnd.get("closure", {}).items():
            yield where, f"closure.{key}", text
        for person in rnd.get("attendance", []):
            yield where, "attendance", person["covered_by"]
        for point in rnd.get("points", []):
            yield where, "points", point["text"]
    for answer in transcript["answers"]:
        for key in ("other", "note"):
            yield f"question {answer['question']}", key, answer[key]
