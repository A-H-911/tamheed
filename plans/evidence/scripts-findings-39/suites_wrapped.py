"""M58 (findings_39, W105): which item keys do the repo's own suites SEND to progress_update
and audit_record? A search of call sites by pattern reads inline arguments only - a list built
in a variable and passed by name is invisible to it. This runs every suite under tests/ with
both tools wrapped and records the keys that actually arrive.

Run from the repository root, with the hook's trace variable unset:
    env -u TAMHEED_HOOK_LOG PYTHONIOENCODING=utf-8 python plans/evidence/scripts-findings-39/suites_wrapped.py

Nothing in the repository is written: the suites use their own temporary folders. The key sets
below are the tools' own constants once plan 161 has landed, and a literal copy before it.
"""
import collections
import contextlib
import glob
import importlib
import io
import os
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
for sub in ("plugins/tamheed/server", "plugins/tamheed/db", "tests"):
    sys.path.insert(0, str(REPO / sub))
os.chdir(REPO)
import tamheed_server as srv  # noqa: E402

TAKES = {
    "progress_update": set(getattr(srv, "_PROGRESS_KEYS", (
        "entry", "event_type", "subject_id", "actor", "corrects", "phase_id", "slice_id"))),
    "audit_record": set(getattr(srv, "_VERDICT_KEYS", (
        "ac_id", "verdict", "evidence", "verified_by", "verification_method",
        "against_commit"))),
}
sent = {name: collections.Counter() for name in TAKES}
calls, odd = collections.Counter(), collections.Counter()


def wrap(name):
    real = getattr(srv, name)

    def inner(items, *args, **kwargs):
        calls[name] += 1
        if not isinstance(items, list):
            odd[(name, "the argument is " + type(items).__name__)] += 1
        for item in items if isinstance(items, list) else []:
            if not isinstance(item, dict):
                odd[(name, "an item is " + type(item).__name__)] += 1
                continue
            for key in item:                # never Counter.update(item): it adds the VALUES
                sent[name][str(key)] += 1
            for key in set(item) - TAKES[name]:
                odd[(name, "key " + str(key))] += 1
        return real(items, *args, **kwargs)

    inner.__doc__ = real.__doc__
    setattr(srv, name, inner)


for tool in TAKES:
    wrap(tool)
modules = sorted(Path(p).stem for p in glob.glob(str(REPO / "tests" / "test_*.py")))
ran = failed = 0
for mod in modules:
    suite = unittest.defaultTestLoader.loadTestsFromModule(importlib.import_module(mod))
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    ran += result.testsRun
    failed += len(result.failures) + len(result.errors)
    print(f"  {mod:30} ran {result.testsRun:4}  failures+errors"
          f" {len(result.failures) + len(result.errors)}")
print(f"suites {len(modules)}; tests run {ran}; failures+errors {failed}")
print("calls seen:", dict(calls))
for tool in sent:
    print(f"  {tool} keys sent: {dict(sent[tool])}")
print("sent outside the tool's keys, or no object at all (each is a DELIBERATE refusal test"
      " once plan 161 has landed):", dict(odd) or "none")
