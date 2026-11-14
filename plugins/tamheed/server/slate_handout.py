"""Two hand-outs for the people of a workshop (plan 227c, R113). Import `slate` first.

Both are plain Markdown, made from the slate's record. They hold the room's questions only:
no option, no recommendation, no question of the operator, no decided topic, no quoted row.
The long sheet gives each question's text. The short sheet gives one line per question, and
a line per round for a topic that a reader wants to add.
"""
from __future__ import annotations

from slate_words import WORDS


def _line(text: str) -> str:
    """One line of a sheet: a text of the slate with its line ends folded."""
    return " ".join(str(text).split())


def _rounds(record: dict):
    """(number, round, the room's questions) for each ready round that has one."""
    for number, rnd in enumerate(record["slate"]["rounds"], 1):
        questions = [q for q in rnd["questions"] if q["owner"] == "room"]
        if rnd["ready"] and questions:
            yield number, rnd, questions


def orientation(record: dict) -> str:
    slate = record["slate"]
    words = WORDS[slate["language"]]
    lines = [f"# {_line(slate['title'])}", "", words["h_intro"], ""]
    for number, rnd, questions in _rounds(record):
        lines += [f"## {words['round']} {number} · {_line(rnd['title'])}", ""]
        for q in questions:
            lines.append(f"- **{q['id']} · {_line(q['question'])}**")
            if q["detail"]:
                lines.append(f"  {_line(q['detail'])}")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def short_sheet(record: dict) -> str:
    slate = record["slate"]
    words = WORDS[slate["language"]]
    lines = [f"# {_line(slate['title'])}", "", words["h_short_intro"], ""]
    for number, rnd, questions in _rounds(record):
        lines += [f"## {words['round']} {number} · {_line(rnd['title'])}", ""]
        lines += [f"- {q['id']} · {_line(q['question'])}" for q in questions]
        lines += [f"- {words['h_add']} ____________________", ""]
    return "\n".join(lines).rstrip("\n") + "\n"
