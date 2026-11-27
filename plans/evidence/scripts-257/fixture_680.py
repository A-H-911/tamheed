"""Plan 257 (R153): write tests/slate_compat_680/ with the v6.8.0 tool, never by hand.

    python -I plans/evidence/scripts-257/fixture_680.py <repo root>

It takes the bundle of the tag v6.8.0 with `git archive`, imports THAT server, and builds the
package and the slate of tests/test_slate.py (its setUp rows and its `slate()` spec, copied
here because the test module imports the current server). It exports the slate, then writes an
answers file as the page writes one, with 6.8.0's own question digests. The record, the page
and the answers file go to tests/slate_compat_680/. The test reads them with the current
`slate_read` and expects no question put again.
"""
from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
out = repo / "tests" / "slate_compat_680"
work = Path(tempfile.mkdtemp(prefix="fixture-680-"))
try:
    archive = subprocess.run(["git", "-C", str(repo), "archive", "v6.8.0", "plugins/tamheed"],
                             check=True, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(work / "bundle", filter="data")
    sys.path[:0] = [str(work / "bundle/plugins/tamheed/server"),
                    str(work / "bundle/plugins/tamheed/db")]
    import tamheed_server as srv  # noqa: E402  (the 6.8.0 server)
    import slate as slates  # noqa: E402
    assert json.loads((work / "bundle/plugins/tamheed/.claude-plugin/plugin.json")
                      .read_text(encoding="utf-8"))["version"] == "6.8.0"

    srv.PACKAGE_ROOT = work / "packages"
    srv.PACKAGE_ROOT.mkdir()
    assert srv.package_create("demo", "Demo", "rnd")["ok"]
    assert srv.entity_upsert([
        {"type": "requirement", "id": "FR-001", "kind": "functional", "title": "Store",
         "statement": "The system keeps the audit trail.", "lifecycle_status": "Approved",
         "source_kind": "brief", "source_span": "p1"},
        {"type": "constraint", "id": "CON-001", "title": "One region"}])["ok"]
    spec = {"name": "round-1", "title": "Round 1", "intro": "Two decisions.", "rounds": [
        {"id": "r1", "title": "Access", "intro": "What was decided before.", "cites": ["CON-001"],
         "questions": [
             {"id": "q1", "question": "Which store?", "detail": "It holds the audit trail.",
              "cites": ["FR-001"],
              "options": [{"id": "A", "label": "Keep it"},
                          {"id": "B", "label": "Move it", "detail": "It costs a week."}],
              "recommended": "A", "reason": "It is measured."},
             {"id": "q2", "question": "Ship now?", "allow_other": False,
              "options": [{"id": "yes", "label": "Yes"}, {"id": "no", "label": "No"}]}]}]}
    exported = srv.slate_export(spec)
    assert exported["ok"], exported
    record = json.loads(Path(exported["record"]).read_text(encoding="utf-8"))
    digests = slates.question_digests(record)
    answers = {"format": "tamheed-slate-answers", "version": 2, "slate": "round-1",
               "slate_digest": exported["slate_digest"], "exported_at": "2026-11-12T10:00:00.000Z",
               "rounds": [{"id": "r1", "guests": "Two people", "closed": True,
                           "closed_by": "The operator", "closure": {}}],
               "answers": [{"question_digest": digests["q1"], "question": "q1", "selected": "B",
                            "other": "", "note": "Agreed"},
                           {"question_digest": digests["q2"], "question": "q2", "selected": None,
                            "other": "", "note": ""}]}
    Path(exported["answers_path"]).write_text(json.dumps(answers), encoding="utf-8")
    assert srv.slate_read("round-1")["ok"]                      # 6.8.0 reads its own files
    srv.package_close()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for name in ("round-1.slate.json", "round-1.html", "round-1.answers.json"):
        (out / name).write_bytes((Path(exported["page"]).parent / name).read_bytes())
    print("wrote", sorted(p.name for p in out.iterdir()))
finally:
    shutil.rmtree(work, ignore_errors=True)
