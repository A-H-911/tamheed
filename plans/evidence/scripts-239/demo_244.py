"""Plan 244 (FB-018): demo pages of other shapes for the browser check, derived from the demo
of plan 227c without a copy of it. One hook is put before its export.

    python demo_244.py <repo> <out root> one|noroom

`one` keeps the first round only: the check runs its one-round checks and prints SKIP for the
rest. `noroom` makes every question the operator's: the page has no question of the room, so
the check refuses it before it changes anything.
"""
import sys
from pathlib import Path

repo, out, mode = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
src = (repo / "plans/evidence/scripts-227/demo_227c.py").read_text(encoding="utf-8")
HOOKS = {
    "one": ('slate["rounds"] = [slate["rounds"][0]]\n'
            'slate["name"] = "workshop-one"\n'),
    # a round holds its questions in blocks, or directly
    "noroom": ('for _r in slate["rounds"]:\n'
               '    _qs = _r.get("questions", []) + [q for b in _r.get("blocks", [])\n'
               '                                     for q in b["questions"]]\n'
               '    for _q in _qs:\n'
               '        _q["owner"] = "operator"\n'
               '        _q.setdefault("approval", True)\n'
               'slate["name"] = "workshop-noroom"\n'),
}
anchor = "result = srv.slate_export(slate)"
assert src.count(anchor) == 1
src = src.replace(anchor, HOOKS[mode] + anchor)
sys.argv = [sys.argv[0], str(repo), out]
exec(compile(src, "demo_227c.py", "exec"))
