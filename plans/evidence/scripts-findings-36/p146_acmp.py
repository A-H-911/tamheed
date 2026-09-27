"""Plan 146 validation: the repo's exporter over a read-only copy of the field package marks
exactly the lesson ids the field's own note lists. The copy is `git archive` of ACMP's HEAD.

usage: python p146_acmp.py <copy-root>      (copy-root holds tamheed-package/)
"""
import os
import re
import sys
from pathlib import Path

assert "TAMHEED_HOOK_LOG" not in os.environ, "unset TAMHEED_HOOK_LOG in the command"
REPO = Path(r"C:\Users\ahammo\Repos\tamheed")
sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "server"))
import tamheed_server as srv  # noqa: E402

root = Path(sys.argv[1]).resolve()
srv.PACKAGE_ROOT = root
opened = srv.package_open("tamheed-package")
assert opened["ok"], opened
try:
    info = srv.server_info()
    print("server", info["version"], info["migrations_head"], info["schema_version"])
    out = srv.export_html(str(root / "review-146.html"))
    assert out["ok"], out
    page = (root / "review-146.html").read_text(encoding="utf-8")
    fold = page.split('id="lessons-approved"', 1)[1].split("</details>", 1)[0]
    cells = dict(re.findall(r'<tr id="(LL-\d+)"><td>LL-\d+</td><td>[^<]*</td><td>[^<]*</td>'
                            r'<td>([^<]*)</td>', fold))
    marked = sorted(i for i, c in cells.items() if c == "rendered")
    note = (root / "tamheed-package" / "CLAUDE.md").read_text(encoding="utf-8")
    listed = sorted(re.findall(r"^- \*\*(LL-\d+)\*\*", note, re.M))
    print("approved rows in the fold:", len(cells), "values:", sorted(set(cells.values())))
    print("marked :", marked)
    print("in note:", listed)
    assert marked == listed, "the page and the field's note disagree"
    title = re.search(r"<summary>(Approved[^<]*)</summary>", fold_head := page.split(
        'id="lessons-approved"', 1)[1][:400])
    print("fold title:", title.group(1) if title else fold_head[:200])
    # calibration: a one-row corruption of the expectation is caught
    assert marked != listed[:-1], "calibration failed"
    print("HELD: marked set == the note's roster; calibration fires")
finally:
    srv.package_close()
