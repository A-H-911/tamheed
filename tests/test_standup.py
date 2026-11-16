"""Plan 233 (ADR-0003): the standup engine. State, deltas, checkpoint replay, the window, facts.

The tool that writes report rows arrives in plan 235. These tests record a report the way the
tool will: compute the draft, then insert the row and move it to Approved through the
connection.
"""
from __future__ import annotations

import json
import random
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "plugins" / "tamheed" / "server"))

import standup as S  # noqa: E402
import standup_page as P  # noqa: E402
import standup_facts as F  # noqa: E402
import tamheed_server as srv  # noqa: E402

NEVER = (lambda text: False)


class EngineTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        srv.PACKAGE_ROOT = Path(self._tmp.name)
        srv.package_create("pkg", "Pkg", "rnd")
        self.conn = srv._CURRENT.conn
        self.n = 0

    def tearDown(self):
        if srv._CURRENT is not None:
            srv.package_close()
        self._tmp.cleanup()

    # ------------------------------------------------------------------ helpers

    def up(self, *rows):
        rows = [dict({"lifecycle_status": "Proposed"}, **r) if r["type"] == "decision"
                else r for r in rows]               # a decision is born Proposed, no default
        out = srv.entity_upsert(rows)
        self.assertTrue(out["ok"], out)

    def journal(self, text, kind="work-done"):
        self.assertTrue(srv.progress_update([{"entry": text, "event_type": kind}])["ok"])

    def tables(self):
        return srv.ENTITY_TABLES.values()

    def draft(self, start=None):
        base, kind, _note, err = S.select_base(self.conn, start)
        self.assertIsNone(err)
        return base, kind, S.compute(self.conn, self.tables(), base, kind)

    def record(self, start=None, offset="+03:00", ended="2026-11-16T06:00:00Z"):
        base, kind, out = self.draft(start)
        self.n += 1
        rid = f"RPT-{self.n:03d}"
        row = {"id": rid, "kind": kind, "seq": out["seq"],
               "base_report": (base or {}).get("id"),
               "checkpoint": int(out["checkpoint"]), "pe_to": out["pe_to"],
               "av_to": out["av_to"], "ended_at": ended, "utc_offset": offset,
               "state_digest": out["digest"], "state_delta": json.dumps(out["delta"]),
               "facts": "{}", "rule_colour": "green"}
        self.conn.execute(f"INSERT INTO standup_reports ({', '.join(row)}) VALUES"
                          f" ({', '.join('?' * len(row))})", list(row.values()))
        ok, why = S.verify(self.conn, row)
        self.assertTrue(ok, why)
        self.conn.execute(
            "UPDATE standup_reports SET narrative = '{\"headline\": \"h\"}', colour = 'green',"
            " recorded_by = 'human:op', operator_words = 'record it', recorded_at = ?,"
            " lifecycle_status = 'Approved' WHERE id = ?", (ended, rid))
        return rid, out

    # ------------------------------------------------------------------ the state

    def test_the_blocked_list_reads_the_far_end(self):
        """Plan 241 (the field's FB-020, R121, R129): the list read only the edge, so a met
        dependency still blocked its slice. A far end now blocks only while it is not
        settled, by one rule per family. Each far-end family is here, open and settled.
        A slice whose every blocker is settled is free to start (R130)."""
        self.up({"type": "phase", "id": "PH-1", "title": "P"},
                {"type": "slice", "id": "SL-001", "title": "Blocked", "phase_id": "PH-1"},
                {"type": "slice", "id": "SL-002", "title": "Free", "phase_id": "PH-1"})
        sev = {"severity": "low"}
        gate = {"type": "execution-gate", "gate_kind": "approval", "definition": "d"}
        pairs = [
            ({"type": "dependency", "id": "DEP-001", "title": "d"},
             {"type": "dependency", "id": "DEP-002", "title": "d",
              "lifecycle_status": "Implemented"}),
            ({"type": "assumption", "id": "ASM-001", "title": "a"},
             {"type": "assumption", "id": "ASM-002", "title": "a", "lifecycle_status": "Rejected"}),
            ({"type": "wbs-item", "id": "WBS-1.1", "title": "w", "slice_id": "SL-002"},
             {"type": "wbs-item", "id": "WBS-1.2", "title": "w", "slice_id": "SL-002",
              "lifecycle_status": "Implemented"}),
            ({"type": "execution-plan", "id": "EP-001", "slice_id": "SL-002", "plan": "p"},
             {"type": "execution-plan", "id": "EP-002", "slice_id": "SL-002", "plan": "p",
              "lifecycle_status": "Superseded"}),
            ({"type": "defect", "id": "DEF-001", "title": "x", **sev},
             {"type": "defect", "id": "DEF-002", "title": "x", "lifecycle_status": "Fixed", **sev}),
            ({"type": "deferred-work", "id": "DW-001", "title": "x", **sev},
             {"type": "deferred-work", "id": "DW-002", "title": "x", "lifecycle_status": "Done",
              **sev}),
            ({"type": "open-question", "id": "OQ-001", "title": "q"},
             {"type": "open-question", "id": "OQ-002", "title": "q", "resolution": "answered"}),
            ({"type": "decision", "id": "DEC-001", "title": "d"},
             {"type": "decision", "id": "DEC-002", "title": "d", "lifecycle_status": "Approved"}),
            ({"type": "risk", "id": "RISK-001", "title": "r"},
             {"type": "risk", "id": "RISK-002", "title": "r", "risk_state": "mitigated"}),
            (dict(gate, id="GATE-001"), dict(gate, id="GATE-002", outcome="Go")),
        ]
        for open_row, done_row in pairs:
            self.up(open_row, done_row)
        edge = {"type": "trace-edge", "relation": "blocked_by"}
        self.up(*[dict(edge, from_id="SL-001", to_id=row["id"]) for pair in pairs for row in pair])
        self.up(*[dict(edge, from_id="SL-002", to_id=done["id"]) for _, done in pairs])
        listed = F.blocked(self.conn)
        self.assertEqual(sorted(it["note"] for it in listed if it["id"] == "SL-001"),
                         sorted(f"blocked by {o['id']}" for o, _ in pairs))
        self.assertNotIn("SL-002", [it["id"] for it in listed])
        self.assertEqual(F.lifted(self.conn),
                         {"SL-002": sorted((d["id"] for _, d in pairs), key=F._key)})
        self.assertNotIn("NOPE-1", F.settled_ids(self.conn))     # a missing row never settles
        # R135: the readiness predicates decide two edge cases, and the docs state both
        self.up({"type": "open-question", "id": "OQ-003", "title": "q",
                 "lifecycle_status": "Deferred"},
                {"type": "risk", "id": "RISK-003", "title": "r", "lifecycle_status": "Obsolete"})
        done = F.settled_ids(self.conn)
        self.assertIn("OQ-003", done)              # a Deferred question lifts its block
        self.assertNotIn("RISK-003", done)         # a retired risk still `open` keeps blocking

    def test_state_skips_the_journal_verdicts_reports_and_edges(self):
        self.journal("did a thing")
        live, cols = S.state(self.conn, self.tables())
        for skipped in S.STATE_SKIP:
            self.assertNotIn(skipped, live)
            self.assertNotIn(skipped, cols)
        self.assertIn("decisions", cols)          # an empty family still has its columns

    def test_fingerprint_skips_nulls_and_last_referenced(self):
        row = {"id": "DEC-001", "title": "t", "rationale": None}
        self.assertEqual(S.fingerprint(row), S.fingerprint({"id": "DEC-001", "title": "t"}))
        self.assertEqual(S.fingerprint(row), S.fingerprint(dict(row, last_referenced="x")))
        self.assertNotEqual(S.fingerprint(row), S.fingerprint(dict(row, title="u")))

    def test_diff_then_apply_is_the_identity(self):
        rng = random.Random(233)
        for _ in range(200):
            def rand_state():
                return {t: {f"X-{i}": rng.choice(["a|1", "b|2", "a|3"])
                            for i in range(rng.randint(0, 6))}
                        for t in rng.sample(["t1", "t2", "t3"], rng.randint(0, 3))}
            base, live = rand_state(), rand_state()
            base = {t: m for t, m in base.items() if m}
            live = {t: m for t, m in live.items() if m}
            bc = {t: ["id", "a"] for t in base}
            lc = {t: ["id", rng.choice(["a", "b"])] for t in live}
            got, cols = S.apply(base, bc, S.diff(base, bc, live, lc))
            self.assertEqual(got, live)
            for t in lc:
                self.assertEqual(cols[t], lc[t])

    def test_an_unknown_delta_version_is_refused(self):
        with self.assertRaisesRegex(ValueError, "unknown to this engine"):
            S.apply({}, {}, {"v": 99})

    # ------------------------------------------------------------------ the chain

    def test_the_first_report_is_a_checkpoint_with_the_full_state(self):
        self.up({"type": "decision", "id": "DEC-001", "title": "use SQLite"})
        _rid, out = self.record()
        self.assertTrue(out["first"])
        self.assertTrue(out["checkpoint"])
        self.assertTrue(out["delta"]["checkpoint"])
        self.assertIn("DEC-001", out["delta"]["set"]["decisions"])

    def test_replay_equals_each_drafts_state(self):
        self.up({"type": "decision", "id": "DEC-001", "title": "a"})
        self.record()
        self.up({"type": "decision", "id": "DEC-002", "title": "b"})
        _rid, second = self.record()
        self.assertFalse(second["checkpoint"])
        self.assertEqual(set(second["delta"]["set"]["decisions"]), {"DEC-002"})
        replayed, _cols, broken = S.replay(S.chain(self.conn))
        self.assertIsNone(broken)
        self.assertEqual(S.digest(replayed), second["digest"])

    def test_replay_names_a_corrupted_middle_link(self):
        self.up({"type": "decision", "id": "DEC-001", "title": "a"})
        self.record()
        self.up({"type": "decision", "id": "DEC-002", "title": "b"})
        self.record()
        self.up({"type": "decision", "id": "DEC-003", "title": "c"})
        self.record()
        self.conn.execute("PRAGMA writable_schema = 0")
        self.conn.execute("DROP TRIGGER trg_standup_reports_immutable")   # a hand edit of data/
        bad = json.dumps({"v": 1, "columns": {}, "set": {"decisions": {"DEC-002": "x|y"}},
                          "drop": {}})
        self.conn.execute("UPDATE standup_reports SET state_delta = ? WHERE id = 'RPT-002'",
                          (bad,))
        _st, _cols, broken = S.replay(S.chain(self.conn))
        self.assertEqual(broken, "RPT-002")
        base, kind, _n, _e = S.select_base(self.conn, None)
        out = S.compute(self.conn, self.tables(), base, kind)
        self.assertEqual(out["broken"], "RPT-002")
        self.assertTrue(out["checkpoint"])          # the next report re-baselines

    def test_every_30th_daily_report_is_a_checkpoint(self):
        flags = []
        for k in range(31):
            self.up({"type": "decision", "id": f"DEC-{k + 1:03d}", "title": "d"})
            _rid, out = self.record()
            flags.append(out["checkpoint"])
        self.assertEqual([k + 1 for k, f in enumerate(flags) if f], [1, 30])
        self.assertEqual(S.chain(self.conn)[0]["id"], "RPT-030")   # replay starts there
        replayed, _c, broken = S.replay(S.chain(self.conn))
        self.assertIsNone(broken)
        self.assertEqual(S.digest(replayed), out["digest"])

    # ------------------------------------------------------------------ moves

    def test_a_status_move_and_a_text_edit_are_told_apart(self):
        self.up({"type": "decision", "id": "DEC-001", "title": "a"},
                {"type": "decision", "id": "DEC-002", "title": "b"})
        self.record()
        self.up({"type": "decision", "id": "DEC-001", "title": "a",
                 "lifecycle_status": "Approved"},
                {"type": "decision", "id": "DEC-002", "title": "b reworded"},
                {"type": "decision", "id": "DEC-003", "title": "born approved",
                 "lifecycle_status": "Approved"})
        _b, _k, out = self.draft()
        cls = out["cls"]
        self.assertEqual([(t, i, a, b) for t, i, a, b in cls["moved"]],
                         [("decisions", "DEC-001", "Proposed", "Approved")])
        self.assertEqual(cls["edited"], [("decisions", "DEC-002")])
        self.assertEqual(cls["new"], [("decisions", "DEC-003", "Approved")])
        decided = F.moved_to(cls, "decisions", F.S_DECIDED)
        self.assertEqual(sorted(i for i, *_ in decided), ["DEC-001", "DEC-003"])

    def test_a_column_set_change_pauses_edits_and_a_new_family_is_first_counted(self):
        base = {"decisions": {"DEC-001": "Proposed|aaa"}}
        live = {"decisions": {"DEC-001": "Proposed|bbb"}, "lessons": {"LL-001": "Proposed|c"}}
        cls = S.classify(base, {"decisions": ["id", "title"]}, live,
                         {"decisions": ["id", "title", "new_col"], "lessons": ["id"]})
        self.assertEqual(cls["edited"], [])
        self.assertEqual(cls["paused"], ["decisions"])
        self.assertEqual(cls["first_counted"], ["lessons"])
        self.assertEqual(cls["new"], [])

    # ------------------------------------------------------------------ the window

    def test_the_window_reads_a_PE_1x_id_without_raising(self):
        self.journal("first")
        self.assertTrue(srv.entity_upsert([{"type": "progress-entry", "id": "PE-1x",
                                            "entry": "odd id", "event_type": "note"}])["ok"])
        self.assertEqual(S.pe_max(self.conn), 1)
        ids = [e["id"] for e in S.window_entries(self.conn, 1, 1)]
        self.assertEqual(sorted(ids), ["PE-001", "PE-1x"])

    def test_a_rewound_journal_is_refused(self):
        self.journal("one")
        self.journal("two")
        self.record()
        self.conn.execute("DELETE FROM progress_entries WHERE id = 'PE-002'")
        base, kind, _n, _e = S.select_base(self.conn, None)
        out = S.compute(self.conn, self.tables(), base, kind)
        self.assertIn("moved backwards", out["error"])

    def test_the_record_row_is_not_listed_in_the_next_window(self):
        self.journal("work")
        rid, _out = self.record()
        self.conn.execute("INSERT INTO progress_entries (id, entry, actor, occurred_at)"
                          " VALUES ('PE-002', ?, 'system:standup-report', 'now')", (rid,))
        self.journal("more work")
        ids = [e["id"] for e in S.window_entries(self.conn, 2, S.pe_max(self.conn))]
        self.assertEqual(ids, ["PE-003"])

    def test_a_date_snaps_in_the_rows_own_offset(self):
        self.record(offset="+03:00", ended="2026-11-15T22:30:00Z")   # 16 Nov 01:30 local
        self.up({"type": "decision", "id": "DEC-001", "title": "a"})
        self.record(offset="+03:00", ended="2026-11-17T06:00:00Z")
        base, kind, note, err = S.select_base(self.conn, "2026-11-15")
        self.assertIsNone(err)
        self.assertIsNone(base)                    # 01:30 on the 16th is after the 15th
        self.assertEqual((kind, note), ("override", "2026-11-15"))
        base, kind, _n, _e = S.select_base(self.conn, "2026-11-16")
        self.assertEqual((base["id"], kind), ("RPT-001", "override"))
        base, kind, _n, _e = S.select_base(self.conn, "2026-11-30")
        self.assertEqual((base["id"], kind), ("RPT-002", "default"))
        self.assertEqual(S.select_base(self.conn, "15/11")[3],
                         "start is a date (YYYY-MM-DD) or a recorded report id (RPT-NNN)")

    def test_a_report_start_must_be_a_recorded_daily_report(self):
        self.record()
        self.assertEqual(S.select_base(self.conn, "RPT-001")[:2][1], "default")
        err = S.select_base(self.conn, "RPT-009")[3]
        self.assertIn("RPT-009 cannot start a window: it is not a row", err)

    def test_offsets_and_local_times(self):
        self.assertIsNotNone(S.parse_offset("+14:00"))
        self.assertIsNotNone(S.parse_offset("-12:00"))
        for bad in ("+15:00", "-13:00", "+03:10", "03:00", "", None):
            self.assertIsNone(S.parse_offset(bad), bad)
        self.assertEqual(S.shown("2026-11-16T06:05:00Z", "+03:00"),
                         "Mon 16 Nov 2026, 09:05 (UTC+03:00)")
        self.assertEqual(S.normal_offset("-00:00"), "+00:00")

    # ------------------------------------------------------------------ handoff, facts

    def test_handoff_sections_parse_by_heading(self):
        self.journal("1. **Resume at.** Finish WBS-002.\n2. **In flight.** none\n"
                     "3. **Awaiting the operator.** Approve DEC-001?\n  Pick a date.\n"
                     "4. **Verified facts.** gate ok\n5. **Do not carry.** old", kind="handoff")
        got = S.handoff_sections(self.conn)
        self.assertEqual(got["resume at"], ["Finish WBS-002."])
        self.assertEqual(got["awaiting the operator"], ["Approve DEC-001?", "Pick a date."])
        screened = F.needs(self.conn, got, "2026-11-16", lambda t: "Pick" in t, None)
        titles = [it["title"] for it in screened["awaiting_operator"]["items"]]
        self.assertEqual(titles, ["Approve DEC-001?", "withheld: read the latest handoff"])

    def test_facts_lists_cap_and_keep_totals_and_the_first_report_is_whole(self):
        self.up(*[{"type": "defect", "id": f"DEF-{k:03d}", "title": f"bug {k}",
                   "severity": "low"} for k in range(1, 41)])
        _b, _k, out = self.draft()
        first = F.build(self.conn, cls=out["cls"], live=out["live"], first=True, window=out,
                        today="2026-11-16", blocker_rules=[], screen=NEVER)
        self.assertEqual(len(first["challenges"]["defects_open"]["items"]), 40)
        self.assertIn("where_we_stand", first)
        self.record()
        self.up({"type": "defect", "id": "DEF-041", "title": "new bug", "severity": "high"})
        _b, _k, out = self.draft()
        daily = F.build(self.conn, cls=out["cls"], live=out["live"], first=False, window=out,
                        today="2026-11-16", blocker_rules=[], screen=NEVER)
        open_list = daily["challenges"]["defects_open"]
        self.assertEqual((len(open_list["items"]), open_list["total"]), (30, 41))
        self.assertEqual(open_list["items"][0]["id"], "DEF-041")   # severity first
        self.assertEqual([it["id"] for it in daily["challenges"]["defects_new"]["items"]],
                         ["DEF-041"])
        self.assertNotIn("where_we_stand", daily)
        self.assertEqual(F.rule_colour(daily)[0], "red")

    def test_rule_colour(self):
        def sections(defects=(), rules=0, risks=0, overdue=0):
            items = [{"id": f"DEF-{k}", "note": sev} for k, sev in enumerate(defects)]
            return {"challenges": {"defects_open": {"items": items, "total": len(items)},
                                   "blocker_rules": {"items": [], "total": rules},
                                   "risks_high": {"items": [], "total": risks}},
                    "needs": {"questions_overdue": {"items": [], "total": overdue}}}
        self.assertEqual(F.rule_colour(sections())[0], "green")
        self.assertEqual(F.rule_colour(sections(defects=("low",)))[0], "green")
        self.assertEqual(F.rule_colour(sections(defects=("critical",)))[0], "red")
        self.assertEqual(F.rule_colour(sections(rules=1))[0], "green")   # SR51
        self.assertEqual(F.rule_colour(sections(risks=1))[0], "amber")
        self.assertEqual(F.rule_colour(sections(overdue=2)), ("amber",
                                                              ["2 overdue questions"]))
        self.assertEqual(F.rule_colour(sections(defects=("high",)))[1],
                         ["1 open critical or high defect"])

    def _row(self, rid, base, kind, out, **extra):
        return dict({"id": rid, "kind": kind, "seq": out["seq"], "base_report":
                     (base or {}).get("id"), "checkpoint": int(out["checkpoint"]),
                     "state_delta": json.dumps(out["delta"]), "state_digest": out["digest"]},
                    **extra)

    def test_an_override_verifies_and_never_enters_the_chain(self):
        self.up({"type": "decision", "id": "DEC-001", "title": "a"})
        self.record()
        self.up({"type": "decision", "id": "DEC-002", "title": "b"})
        self.record()
        self.up({"type": "decision", "id": "DEC-003", "title": "c"})
        base, kind, out = self.draft("RPT-001")
        self.assertEqual((base["id"], kind, out["seq"], out["checkpoint"]),
                         ("RPT-001", "override", None, False))
        self.assertEqual(set(out["delta"]["set"]["decisions"]), {"DEC-002", "DEC-003"})
        self.assertEqual(S.verify(self.conn, self._row("RPT-003", base, kind, out)),
                         (True, None))
        self.assertEqual([r["id"] for r in S.chain(self.conn)], ["RPT-001", "RPT-002"])

    def test_an_override_over_a_broken_link_stores_the_full_state_and_verifies(self):
        self.up({"type": "decision", "id": "DEC-001", "title": "a"})
        self.record()
        self.up({"type": "decision", "id": "DEC-002", "title": "b"})
        self.record()
        self.up({"type": "decision", "id": "DEC-003", "title": "c"})
        self.record()
        self.conn.execute("DROP TRIGGER trg_standup_reports_immutable")
        self.conn.execute("UPDATE standup_reports SET state_digest = 'bad' WHERE id = 'RPT-002'")
        base, kind, out = self.draft("RPT-002")
        self.assertEqual((kind, out["broken"]), ("override", "RPT-002"))
        self.assertTrue(out["delta"]["checkpoint"])
        self.assertEqual(S.verify(self.conn, self._row("RPT-004", base, kind, out)),
                         (True, None))

    def test_a_correction_keeps_its_place_and_verifies_after_the_old_row_moves(self):
        self.up({"type": "decision", "id": "DEC-001", "title": "a"})
        self.record()
        self.up({"type": "decision", "id": "DEC-002", "title": "b"})
        self.record()
        old = dict(zip(("seq", "base_report", "checkpoint", "state_delta", "state_digest"),
                       self.conn.execute(
                           "SELECT seq, base_report, checkpoint, state_delta, state_digest"
                           " FROM standup_reports WHERE id = 'RPT-002'").fetchone()))
        row = dict(old, id="RPT-003", supersedes="RPT-002", kind="default")
        self.assertEqual(S.verify(self.conn, row), (True, None))
        cols = ", ".join(old)
        self.conn.execute(f"INSERT INTO standup_reports (id, kind, supersedes, {cols}, pe_to,"
                          " av_to, ended_at, utc_offset, facts, rule_colour) SELECT 'RPT-003',"
                          f" 'default', 'RPT-002', {cols}, pe_to, av_to, ended_at, utc_offset,"
                          " facts, rule_colour FROM standup_reports WHERE id = 'RPT-002'")
        self.conn.execute("UPDATE standup_reports SET lifecycle_status = 'Superseded'"
                          " WHERE id = 'RPT-002'")
        self.assertEqual(S.verify(self.conn, row), (True, None))
        self.conn.execute(
            "UPDATE standup_reports SET narrative = 'n', colour = 'green', recorded_by ="
            " 'human:op', operator_words = 'w', recorded_at = 't', lifecycle_status ="
            " 'Approved' WHERE id = 'RPT-003'")
        self.assertEqual([r["id"] for r in S.chain(self.conn)], ["RPT-001", "RPT-003"])
        replayed, _c, broken = S.replay(S.chain(self.conn))
        self.assertIsNone(broken)
        self.assertEqual(S.digest(replayed), old["state_digest"])

    def test_verify_catches_drift_since_the_draft(self):
        self.record()
        self.up({"type": "decision", "id": "DEC-001", "title": "a"})
        base, kind, out = self.draft()
        row = {"id": "RPT-002", "base_report": base["id"], "checkpoint": 0,
               "state_delta": json.dumps(out["delta"]), "state_digest": out["digest"]}
        self.assertEqual(S.verify(self.conn, row), (True, None))
        self.assertFalse(S.verify(self.conn, dict(row, state_digest="0" * 64))[0])



GOLDEN = REPO_ROOT / "tests" / "standup_golden"
REGEN = "--regen" in sys.argv


class PageTest(unittest.TestCase):
    """Plan 234: the page is a pure function of its row, inside the review page's frame."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        srv.PACKAGE_ROOT = Path(self._tmp.name)
        with mock.patch.object(srv, "_now", return_value="2026-11-15T05:00:00Z"):
            srv.package_create("pkg", "Payments revamp", "rnd")
        self.conn = srv._CURRENT.conn

    def tearDown(self):
        if srv._CURRENT is not None:
            srv.package_close()
        self._tmp.cleanup()

    def up(self, *rows):
        rows = [dict({"lifecycle_status": "Proposed"}, **r) if r["type"] == "decision"
                else r for r in rows]
        out = srv.entity_upsert(rows)
        self.assertTrue(out["ok"], out)

    def page(self, narrative=None, *, kind_start=None, row_extra=None, exempt=None,
             reasons=()):
        base, kind, snapped, err = S.select_base(self.conn, kind_start)
        self.assertIsNone(err)
        out = S.compute(self.conn, srv.ENTITY_TABLES.values(), base, kind)
        facts = F.build(self.conn, cls=out["cls"], live=out["live"], first=out["first"],
                        window=out, today="2026-11-16", blocker_rules=[], screen=NEVER)
        colour, why = F.rule_colour(facts)
        row = dict({"id": "RPT-001", "kind": kind, "utc_offset": "+03:00",
                    "ended_at": "2026-11-16T06:05:00Z", "state_digest": out["digest"],
                    "rule_colour": colour, "lifecycle_status": "Draft"}, **(row_extra or {}))
        meta = P.meta(row, package="Payments revamp", base=base, birth="2026-11-15",
                      window=out, snapped=snapped, rule_reasons=reasons or why)
        first = out["first"] if exempt is None else exempt
        return P.fit(meta, facts, narrative, exempt=first)

    NARRATIVE = {"headline": "The export works end to end. One defect blocks the release.",
                 "did": "We finished the export (WBS-001).",
                 "challenges": "The login defect is open (DEF-001).",
                 "next": "We fix the defect first.", "plan": "Fix DEF-001, then release.",
                 "colour": "amber", "colour_reason": "One open high defect."}

    def seed(self):
        self.up({"type": "wbs-item", "id": "WBS-001", "title": "Export to CSV",
                 "lifecycle_status": "Implemented"},
                {"type": "defect", "id": "DEF-001", "title": "Login fails on Safari",
                 "severity": "high"},
                {"type": "decision", "id": "DEC-001", "title": "Use SQLite for the cache"})

    def golden(self, name, page):
        path = GOLDEN / f"{name}.html"
        if REGEN:
            GOLDEN.mkdir(exist_ok=True)
            path.write_text(page, encoding="utf-8", newline="\n")
        self.assertEqual(page, path.read_text(encoding="utf-8"), f"{name}: run with --regen")

    def test_the_first_and_a_daily_page_match_their_goldens(self):
        self.seed()
        page, _words = self.page(self.NARRATIVE)
        self.golden("first", page)
        self.assertEqual(page, self.page(self.NARRATIVE)[0])       # same row, same bytes
        self.conn.execute(
            "INSERT INTO standup_reports (id, kind, seq, lifecycle_status, checkpoint, pe_to,"
            " av_to, ended_at, utc_offset, state_digest, state_delta, facts, narrative,"
            " rule_colour, colour, recorded_by, operator_words, recorded_at) VALUES"
            " ('RPT-001', 'default', 1, 'Approved', 1, ?, 0, '2026-11-16T06:05:00Z', '+03:00',"
            " ?, ?, '{}', '{}', 'amber', 'amber', 'human:op', 'record it',"
            " '2026-11-16T06:10:00Z')",
            (S.pe_max(self.conn), *self._first_state()))
        self.up({"type": "wbs-item", "id": "WBS-002", "title": "Import from CSV",
                 "lifecycle_status": "Review"},
                {"type": "decision", "id": "DEC-001", "title": "Use SQLite for the cache",
                 "lifecycle_status": "Approved"})
        daily, _w = self.page(self.NARRATIVE, row_extra={"id": "RPT-002",
                                                        "ended_at": "2026-11-17T06:05:00Z"})
        self.golden("daily", daily)
        self.assertIn("claimed done", daily)
        self.assertIn("waiting for approval → approved", daily)

    def _first_state(self):
        live, cols = S.state(self.conn, srv.ENTITY_TABLES.values())
        return S.digest(live), json.dumps(S.full(live, cols))

    def test_the_frame_has_no_script_and_no_outward_link(self):
        self.seed()
        page, _w = self.page(self.NARRATIVE)
        self.assertIn('content="default-src \'none\'; style-src \'unsafe-inline\'"', page)
        self.assertNotIn("<script", page.lower())
        for href in re.findall(r'href="([^"]*)"', page):
            self.assertTrue(href.startswith("#"), href)
        self.assertNotIn("src=", page)

    def test_hostile_text_renders_as_text(self):
        self.up({"type": "decision", "id": "DEC-001",
                 "title": '<img src=x onerror=alert(1)>"quoted"'})
        evil = dict(self.NARRATIVE, did="<script>alert(2)</script> & more",
                    headline="<b>bold</b>", next="<i>n</i>", plan="<u>p</u>",
                    colour_reason="<s>r</s>")
        page, _w = self.page(evil)
        for raw in ("<b>bold", "<i>n", "<u>p", "<s>r"):
            self.assertNotIn(raw, page)
        odd, _w = self.page(dict(self.NARRATIVE, colour=["red"]))   # never a crash
        self.assertIn("Proposed overall:", odd)
        self.assertNotIn("<img src=x", page)
        self.assertNotIn("<script>alert(2)", page)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;&quot;quoted&quot;", page)
        self.assertIn("&lt;script&gt;alert(2)&lt;/script&gt; &amp; more", page)

    def test_the_engine_part_stays_in_its_budget_on_a_large_package(self):
        self.up(*[{"type": "wbs-item", "id": f"WBS-{k:03d}", "title": f"Task number {k} of"
                   " the large migration plan", "lifecycle_status": "Draft"}
                  for k in range(1, 501)],
                *[{"type": "defect", "id": f"DEF-{k:03d}", "title": f"Defect {k} in the"
                   " billing screen", "severity": "medium"} for k in range(1, 201)])
        self.conn.execute(
            "INSERT INTO standup_reports (id, kind, seq, lifecycle_status, checkpoint, pe_to,"
            " av_to, ended_at, utc_offset, state_digest, state_delta, facts, narrative,"
            " rule_colour, colour, recorded_by, operator_words, recorded_at) VALUES"
            " ('RPT-001', 'default', 1, 'Approved', 1, 0, 0, '2026-11-16T06:05:00Z', '+03:00',"
            " ?, ?, '{}', '{}', 'green', 'green', 'human:op', 'w', '2026-11-16T06:10:00Z')",
            self._first_state())
        self.up(*[{"type": "wbs-item", "id": f"WBS-{k:03d}", "title": f"Task number {k} of"
                   " the large migration plan", "lifecycle_status": "Implemented"}
                  for k in range(1, 501)],
                *[{"type": "defect", "id": f"DEF-{k:03d}", "title": f"Defect {k} renamed",
                   "severity": "medium"} for k in range(1, 151)])
        page, words = self.page(self.NARRATIVE, row_extra={"id": "RPT-002"})
        self.assertLessEqual(words - P.narrative_words(self.NARRATIVE), P.ENGINE_BUDGET)
        self.assertEqual(words, P.visible_words(page))
        self.assertIn("more in the record", page)                 # the 30-item freeze
        long = dict(self.NARRATIVE, did="word " * 900)
        page2, words2 = self.page(long, row_extra={"id": "RPT-002"})
        self.assertGreaterEqual(words2 - words, 890)               # the narrative never shrinks
        self.assertLessEqual(words2 - P.narrative_words(long), P.ENGINE_BUDGET)

    def test_the_first_report_is_exempt_and_complete(self):
        self.up(*[{"type": "wbs-item", "id": f"WBS-{k:03d}", "title": f"Done task {k}",
                   "lifecycle_status": "Implemented"} for k in range(1, 121)])
        page, _w = self.page(self.NARRATIVE)
        for k in (1, 60, 120):
            self.assertIn(f"WBS-{k:03d}", page)
        self.assertNotIn("more in the record", page)
        self.assertIn("Where we stand", page)

    def test_the_glossary_names_only_the_terms_on_the_page(self):
        self.up({"type": "wbs-item", "id": "WBS-001", "title": "Export",
                 "lifecycle_status": "Implemented"})
        page, _w = self.page(None)
        terms = re.findall(r"<dt>([^<]+)</dt>", page)
        self.assertIn("task", terms)
        self.assertNotIn("waiver", terms)
        self.assertNotIn("scope change", terms)

    def test_times_show_in_the_rows_offset_and_the_words_never_show(self):
        self.seed()
        page, _w = self.page(self.NARRATIVE, row_extra={
            "lifecycle_status": "Approved", "recorded_by": "human:op",
            "recorded_at": "2026-11-16T06:10:00Z", "operator_words": "SECRET WORDS",
            "colour": "amber"})
        self.assertIn("Mon 16 Nov 2026, 09:05 (UTC+03:00)", page)
        self.assertIn("Recorded by human:op on Mon 16 Nov 2026, 09:10 (UTC+03:00)", page)
        self.assertNotIn("SECRET WORDS", page)
        self.assertNotIn("Draft: not recorded yet", page)

    def test_the_rule_colour_shows_when_the_confirmed_colour_differs(self):
        self.seed()                                   # a high defect: the rule says red
        page, _w = self.page(self.NARRATIVE, row_extra={"colour": "amber"})
        self.assertIn("Proposed overall: At risk.", page)
        self.assertIn("The default rule says: off track", page)
        same, _w = self.page(dict(self.NARRATIVE, colour="red"),
                             row_extra={"colour": "red"})
        self.assertNotIn("The default rule says", same)

    def test_the_visible_counter_skips_closed_folds_but_reads_their_summary(self):
        page = ("<html><head><title>t t t</title><style>a b</style></head><body>"
                "<p>one two</p><details><summary>three</summary><p>hidden words</p>"
                "<details><summary>nested</summary></details></details>"
                "<details open><summary>four</summary><p>five</p></details></body></html>")
        self.assertEqual(P.visible_text(page).split(), ["one", "two", "three", "four", "five"])

if __name__ == "__main__":
    unittest.main(argv=[a for a in sys.argv if a != "--regen"], verbosity=2)
