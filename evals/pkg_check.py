"""Assertion primitives for the eval runner (plan 013/B10) — stdlib only.

Each subcommand is one mechanically checkable claim about a recorded v2 package,
speaking the eval spec's command + expected-exit/expected-substring contract.
Package-level checks reuse the MCP server handlers in-process (gate_run,
entity_query) so evals exercise the exact code path agents use; grep checks read
the canonical JSONL raw. Exit: 0 = claim holds, 1 = claim fails, 2 = usage/IO.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "plugins" / "tamheed" / "server"))

import tamheed_server as srv  # noqa: E402


def _open(package_dir: str) -> Path:
    pkg = Path(package_dir).resolve()
    srv.PACKAGE_ROOT = pkg.parent
    result = srv.package_open(pkg.name)
    if not result["ok"]:
        print(f"cannot open package {pkg}: {result['error']}")
        sys.exit(2)
    return pkg


def _rows(package_dir: str, etype: str) -> list[dict]:
    _open(package_dir)
    result = srv.entity_query(etype, limit=100000)
    srv.package_close()
    if not result["ok"]:
        print(result["error"])
        sys.exit(2)
    return result["rows"]


def cmd_gates(args) -> int:
    """Print ready=True/False + one G-<gate>=pass/fail line per gate (assert by substring)."""
    _open(args.package)
    report = srv.gate_run()
    srv.package_close()
    print(f"ready={report['ready']}")
    for gate, info in report["gates"].items():
        if gate.startswith("G-"):
            print(f"{gate}={info['status']}")
    return 0


def cmd_count(args) -> int:
    rows = _rows(args.package, args.type)
    for cond in args.col or []:
        key, _, value = cond.partition("=")
        rows = [r for r in rows if str(r.get(key)) == value]
    n = len(rows)
    print(f"count={n}")
    if args.min is not None and n < args.min:
        print(f"below required minimum {args.min}")
        return 1
    if args.max is not None and n > args.max:
        print(f"above allowed maximum {args.max}")
        return 1
    return 0


def cmd_nonempty(args) -> int:
    rows = _rows(args.package, args.type)
    offenders = [str(r.get("id")) for r in rows
                 if not str(r.get(args.column) or "").strip()]
    if offenders:
        print(f"empty {args.column} on: {', '.join(offenders)}")
        return 1
    print(f"all {len(rows)} row(s) carry a non-empty {args.column}")
    return 0


def _grep(args, want_present: bool) -> int:
    data = Path(args.package) / "data"
    if not data.is_dir():
        print(f"no data/ directory under {args.package}")
        return 2
    tables = (args.tables.split(",") if args.tables
              else sorted(p.stem for p in data.glob("*.jsonl")))
    hits = []
    for table in tables:
        path = data / f"{table}.jsonl"
        if not path.exists():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if args.needle in line:
                hits.append(f"{table}.jsonl:{lineno}")
    if want_present:
        print(f"found in: {', '.join(hits)}" if hits else f"{args.needle!r} not found")
        return 0 if hits else 1
    print(f"present (should be absent) in: {', '.join(hits)}" if hits else "absent")
    return 1 if hits else 0


def cmd_file_exists(args) -> int:
    ok = Path(args.path).is_file()
    print(f"{args.path}: {'exists' if ok else 'MISSING'}")
    return 0 if ok else 1


def cmd_grep_file(args) -> int:
    path = Path(args.path)
    if not path.is_file():
        print(f"{args.path}: MISSING")
        return 1
    ok = args.needle in path.read_text(encoding="utf-8")
    print(f"{args.needle!r} {'found' if ok else 'NOT found'} in {args.path}")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("gates", help="print gate_run verdicts as ready=/G-*= lines")
    p.add_argument("package")
    p.set_defaults(fn=cmd_gates)

    p = sub.add_parser("count", help="count rows of one entity family, with bounds")
    p.add_argument("package")
    p.add_argument("type")
    p.add_argument("--col", action="append", metavar="KEY=VALUE",
                   help="keep only rows where column equals value (repeatable)")
    p.add_argument("--min", type=int)
    p.add_argument("--max", type=int)
    p.set_defaults(fn=cmd_count)

    p = sub.add_parser("nonempty", help="every row carries a non-empty column")
    p.add_argument("package")
    p.add_argument("type")
    p.add_argument("column")
    p.set_defaults(fn=cmd_nonempty)

    for name, present in (("grep-absent", False), ("grep-present", True)):
        p = sub.add_parser(name, help=f"substring must be {'present' if present else 'absent'}"
                                      " in the canonical JSONL")
        p.add_argument("package")
        p.add_argument("needle")
        p.add_argument("--tables", help="comma-separated table names (default: all)")
        p.set_defaults(fn=lambda a, _p=present: _grep(a, _p))

    p = sub.add_parser("file-exists", help="a recorded file exists")
    p.add_argument("path")
    p.set_defaults(fn=cmd_file_exists)

    p = sub.add_parser("grep-file", help="a recorded file contains a substring")
    p.add_argument("path")
    p.add_argument("needle")
    p.set_defaults(fn=cmd_grep_file)

    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
