"""Plan 243 (FB-017, R125): the texts of `entity_export` running `slate_read`, and the
CHANGELOG. Idempotent: a pair already applied is skipped.

    python plans/evidence/scripts-239/docs_243.py
"""
from pathlib import Path

R = Path(__file__).resolve().parents[3]
EDITS = {
    "plugins/tamheed/server/README.md": [(
        "The tools are `entity_query` (default), `trace_query`, `gate_run`, `readiness_check`,"
        " `package_verify` (`record` refused) and `server_info`.",
        "The tools are `entity_query` (default), `trace_query`, `gate_run`, `readiness_check`,"
        " `package_verify` (`record` refused), `server_info` and, since v6.7, `slate_read`. A"
        " `slate_read` export also reads the answers files: it carries their own `exported_at`"
        " times, and its digest covers the store only.")],
    "docs/architecture.md": [(
        "`<package>/exports/`, and the script quotes from that file. The digest names the state the"
        " rows came from,\n",
        "`<package>/exports/`, and the script quotes from that file. Since v6.7 the tool can be"
        " `slate_read`, whose file\nalso reads the answers files and carries their times. The"
        " digest names the state the rows came from,\n")],
    "SECURITY.md": [(
        "  only if it is itself a tamheed export. The file holds brief-derived text a script will RENDER.\n",
        "  only if it is itself a tamheed export. The file holds brief-derived text a script will RENDER.\n"
        "  Since v6.7 a `slate_read` export also holds answers that people typed on a page. That text\n"
        "  is untrusted: it keeps `screened` and `provenance: \"unverified\"`, and the agent reads the\n"
        "  transcript back to the operator before any write.\n")],
    "plugins/tamheed/skills/operator-interview/SKILL.md": [(
        "- Read the files with `slate_read`. It returns one checked transcript, and it writes nothing.\n",
        "- Read the files with `slate_read`. It returns one checked transcript, and it writes nothing.\n"
        "  A committed script can compare it with its source through\n"
        "  `entity_export(path, tool=\"slate_read\", args={\"name\": ...})`. The export changes\n"
        "  nothing below: the read-back is still required.\n")],
    "docs/guide/content.py": [(
        "Export immediately before generating, cite the digest, never reuse an export across"
        " sessions.\", \"ar\":",
        "Export immediately before generating, cite the digest, never reuse an export across"
        " sessions. Since v6.7 it also runs `slate_read`, whose file carries the answers files'"
        " own times.\", \"ar\":"), (
        "صدِّر قبل التوليد مباشرةً، واستشهد بالبصمة، ولا تعِد استخدام تصدير عبر الجلسات.\"",
        "صدِّر قبل التوليد مباشرةً، واستشهد بالبصمة، ولا تعِد استخدام تصدير عبر الجلسات. ومنذ"
        " v6.7 يشغّل أيضًا `slate_read`، ويحمل ملفه أوقات ملفات الإجابات نفسها.\"")],
}
ENTRY = (
    "- **`entity_export` runs `slate_read` (plan 243, the field's FB-017, R125).** A committed\n"
    "  script reads the store only through `exports/`, so it could not compare a round's checked\n"
    "  transcript with its source. The file holds the transcript with its `screened` and\n"
    "  `provenance` keys. It carries the answers files' own `exported_at` times, and its digest\n"
    "  covers the store only. The agent still reads the transcript back to the operator.\n")
for rel, pairs in EDITS.items():
    path = R / rel
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if new in text:
            continue
        assert text.count(old) == 1, (rel, text.count(old), old[:60])
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8", newline="\n")
log = R / "CHANGELOG.md"
text = log.read_text(encoding="utf-8")
if "(plan 243," not in text:
    anchor = "### Added\n\n"
    assert text.index(anchor) < text.index("## [6.6.0]")
    text = text.replace(anchor, anchor + ENTRY + "\n", 1)
    log.write_text(text, encoding="utf-8", newline="\n")
print("docs 243 written")
