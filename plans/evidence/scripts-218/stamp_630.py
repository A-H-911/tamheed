"""Plan 218: stamp 6.3.0 on every version surface lint 8 reads, write the CHANGELOG entry, append
the stock guide's new body to stock-history.json, re-aim the two lab-tracker eval pins. Run from
the repository root, then `python docs/guide/build.py` (index.html carries the version) and the
fixture refresh (`refresh_lab_630.py`). The 213/215 pattern."""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[3]
OLD, NEW, DATE = "6.2.1", "6.3.0", "2026-10-10"   # the UTC date of the release commit


def sub_once(path: Path, old: str, new: str) -> None:
    t = path.read_text(encoding="utf-8")
    assert t.count(old) == 1, (path, t.count(old), old[:60])
    path.write_text(t.replace(old, new), encoding="utf-8", newline="\n")


# plugin.json
sub_once(R / "plugins/tamheed/.claude-plugin/plugin.json", f'"version": "{OLD}"', f'"version": "{NEW}"')

# the prose surfaces: the line that names the current version, never the history lines
sub_once(R / "README.md", f"Claude Code plugin + MCP-backed agent skill · v{OLD}", f"Claude Code plugin + MCP-backed agent skill · v{NEW}")
sub_once(R / "README.md", f"**v6.x** (currently v{OLD}).", f"**v6.x** (currently v{NEW}).")
sub_once(R / "plugins/tamheed/server/README.md", f"Documents the tool surface as of **tamheed v{OLD}**.", f"Documents the tool surface as of **tamheed v{NEW}**.")
sub_once(R / "plugins/tamheed/skills/tamheed/SKILL.md", f"This skill documents tamheed **v{OLD}**", f"This skill documents tamheed **v{NEW}**")
sub_once(R / "plugins/tamheed/references/artifact-catalog.md", f"(tamheed v{OLD})", f"(tamheed v{NEW})")

# the stock operator guide: its title line, and the body lands WITH its history key (lint 9)
guide = R / "plugins/tamheed/prompts/README.md"
sub_once(guide, f"operator guide (tamheed v{OLD})", f"operator guide (tamheed v{NEW})")
hist_path = R / "plugins/tamheed/prompts/stock-history.json"
hist = json.loads(hist_path.read_text(encoding="utf-8"))
assert NEW not in hist["README.md"]
hist["README.md"][NEW] = guide.read_text(encoding="utf-8")
hist_path.write_text(json.dumps(hist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

# the two lab-tracker pins on the recorded fixture (refreshed by the engine in refresh_lab_630.py)
ev = R / "evals/evals.json"
sub_once(ev, '"tamheed v6.2.1"', '"tamheed v6.3.0"')
sub_once(ev, '"<meta name=\\"tamheed-version\\" content=\\"6.2.1\\">"', '"<meta name=\\"tamheed-version\\" content=\\"6.3.0\\">"')
sub_once(ev, "The guide followed the stamp: refresh_stock carried it to the 6.2.1 body that names nine discipline skills (plans 120, 127, 183, 189, 198, 210, 213, 215).",
         "The guide followed the stamp: refresh_stock carried it to the 6.3.0 body that names nine discipline skills (plans 120, 127, 183, 189, 198, 210, 213, 215, 218).")
sub_once(ev, "The guide followed the 6.2.1 stamp: refresh_stock carried it to the shipped body at the package root, whose history key landed with the stamp (plans 168, 173, 189, 198, 210, 213, 215).",
         "The guide followed the 6.3.0 stamp: refresh_stock carried it to the shipped body at the package root, whose history key landed with the stamp (plans 168, 173, 189, 198, 210, 213, 215, 218).")

# the CHANGELOG entry, above the newest heading
cl = R / "CHANGELOG.md"
t = cl.read_text(encoding="utf-8")
head = f"## [{OLD}] - 2026-10-09"
assert t.count(head) == 1
entry = f"""## [{NEW}] - {DATE}

**MINOR — the flush writes only what changed, atomically, and reports what landed (ACMP's FB-029);
tamheed per repository, nothing at user level (plans 216–218).** A store write that failed mid-flush
with an OS error on one file had applied the row and written another file, reported a bare exception,
and left the session's own partial flush reading as an outside change until a close and reopen. The
store's dump wrote every table file on every commit with a truncating write, and the fingerprints
updated only after the whole dump. Now a commit writes only the files whose canonical bytes changed,
each to a `<table>.jsonl.writing` temp beside the target and replaced in one step, five attempts on
any OS error with four sleeps of 50 to 400 ms between them, the fingerprint set per file as it lands.
A flush that stops on one file raises `StoreFlushError`, and the tool returns its own facts (`items`,
`ids`) with `ok: false`, `applied: true` and a `flush` report naming the written, the failed and the
pending files. `package_close` keeps a pending table's bytes as `data/<table>.jsonl.unflushed` and
names them (`flushed: false`, `unflushed`). `package_open` warns on such a sidecar and removes a stale
`.writing` temp, never a migrate's `.tmp`. The temp and the sidecar are created anew with `O_EXCL`,
so a planted symlink carries nothing. The install posture moved: a project-scope record and a
project-declared marketplace per repository, nothing at user scope, because a user-scope record wins
the load over a repository's own (measured on Claude Code 2.1.294). No schema move: `schema_version`
stays 8, the store's bytes do not move. Beyond the release stamp's own lines, the bundle changes in
`db/store.py`, the server, `db/CANONICAL.md`, two skills and the server README.

**For a live package (the migration note).** Nothing to run. A package that saw a partial flush
flushes the pending file at its next write under 6.3.0. A `data/<table>.jsonl.unflushed` sidecar left
by an earlier close is named at `package_open` until the operator compares it with the `.jsonl`, keeps
one, and removes it. The field sets its feedback row `Resolved` with `resolved_in` 6.3.0 and the plan
217 reference. To install per repository: `claude plugin marketplace add A-H-911/tamheed --scope
project`, then `claude plugin install tamheed@tamheed --scope project`, from the repository's root.

### Added
- `store._flush`, `_write_atomic`, `_write_fresh`, `_table_bytes` and `StoreFlushError`: the
  changed-files-only, atomic, per-file-fingerprinted flush with its failure report. `dump()` and
  `commit()` return the flush report.
- `_commit(partial)`: a flush failure merged with the caller's own result at six sites.
- `package_close`: `unflushed` and the sidecar; `package_open`: the `warning` on a sidecar or a stale
  temp. `TOOL_EFFECTS` names the sidecar write; the guide's `entity_upsert`, `package_open` and
  `package_close` strings say so (EN and AR).

### Changed
- `CANONICAL.md`'s write-back section, the `package-writes` and `session-handoff` skills, and the
  server README rows for `entity_upsert`, `progress_update`, `package_open` and `package_close`.
- The install docs (README, `docs/install.md`, the guide's install section): per repository, no user
  scope, the measured loading rule, the update per repository, the collaborator's one command, and a
  recipe for moving a project to a newer release.

"""
t = t.replace(head, entry + head)
cl.write_text(t, encoding="utf-8", newline="\n")
print("stamped", NEW)
