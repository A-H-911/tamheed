"""Mutation check for plan 227c: each safeguard is taken out in turn, and a test must fail."""
import io
import json
import re
import sys
import unittest

sys.path.insert(0, "tests")
import test_slate as old  # noqa: E402
import test_slate_rounds as new  # noqa: E402

srv, slates = old.srv, old.slates
import slate_answers  # noqa: E402
import slate_page  # noqa: E402
import slate_round  # noqa: E402
import slate_rows  # noqa: E402

CASES = [old.SlateTest, new.GrammarTest, new.ReaderTest, new.PageTest]


def run(label: str) -> int:
    failed = []
    for case in CASES:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(case)
        result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
        failed += sorted(x[0]._testMethodName for x in result.failures + result.errors)
    print(f"{label}: {len(failed)} test(s) fail" + ("" if failed else "   <-- NOT CAUGHT"))
    return len(failed)


def swap(module, name: str, value, label: str) -> bool:
    keep = getattr(module, name)
    setattr(module, name, value)
    try:
        return run(label) > 0
    finally:
        setattr(module, name, keep)


assert run("as built") == 0, "the suites must pass before a mutation means anything"
plain = lambda v: "" if v is None else str(v)  # noqa: E731
caught = [
    swap(slate_round, "esc", plain, "escaping off in a round's markup"),
    swap(slate_page, "esc", plain, "escaping off in the page's shell"),
    swap(slate_rows, "UNQUOTED_COLUMNS", frozenset({"id"}), "last_referenced quoted"),
    swap(slates, "parse_strict", json.loads, "loose JSON"),
    swap(srv, "_INJECT_RE", re.compile(r"(?!x)x"), "no screening"),
    swap(slate_answers, "MAX_DROPPED", 10 ** 9, "no cap on dropped answers"),
    swap(slate_answers, "_empty_answer", lambda a: False, "an empty answer is a candidate"),
    swap(slate_answers, "legal_selections", lambda q: {"A", "B", "Z", "other", "unknown", "evidence",
                                                         "yes", "no"}, "any selection is legal"),
    swap(slate_rows, "derived_error", lambda *a: None, "the record's derived part is not checked"),
    swap(slate_answers, "question_digests",
         lambda record: {q["id"]: "same" for q in slates.questions_of(record["slate"])},
         "every question has one digest"),
    swap(slate_answers, "short", lambda v: repr(v), "a refusal echoes a value whole"),
    swap(slate_rows, "ID_IN_TEXT", re.compile(r"(?!x)x"), "no id is found in a text"),
]
print(f"{sum(caught)} of {len(caught)} mutations are caught")
sys.exit(0 if all(caught) else 1)
